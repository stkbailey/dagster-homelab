import pathlib
import pickle
from typing import List

import networkx
from dagster import Config, OpExecutionContext, asset
from dagster_duckdb import DuckDBResource

from dagster_repo.resources import SubstackResource


class AssetConfig(Config):
    subdomain: str = "stkbailey"
    file_path: str = "output/substack_graph.pik"


def read_pickled_graph(p: pathlib.Path):
    with p.open("rb") as f:
        g = pickle.load(f)
    return g


def write_pickled_graph(g: networkx.Graph, p: pathlib.Path):
    with p.open("wb") as f:
        pickle.dump(g, f)


def add_page_with_recommendations(g: networkx.Graph, page):
    g.add_node(page.subdomain, **page.contents)
    for ii in page.recommendations:
        target_subdomain = ii["recommendedPublication"]["subdomain"]
        g.add_edge(
            u_of_edge=page.subdomain,
            v_of_edge=target_subdomain,
        )
    return g


@asset(
    compute_kind="networkx",
)
def substack_graph(
    context: OpExecutionContext,
    config: AssetConfig,
    substack: SubstackResource,
) -> networkx.Graph:
    # setup
    client = substack.get_substack_client()
    p = pathlib.Path(config.file_path)
    if p.exists():
        g = read_pickled_graph(p)
    else:
        g = networkx.Graph()

    # fetch the root page
    root = client._scrape_substack_page(config.subdomain)
    g = add_page_with_recommendations(g, root)

    # find nodes that haven't been updated recently
    stale_subdomains = [
        x for x, data in g.nodes(data=True) if data.get("scraped_at") is None
    ]
    for n in stale_subdomains:
        page = client._scrape_substack_page(n)
        g = add_page_with_recommendations(g, page)

    # add output metadata
    written = networkx.write_network_text(g)
    context.add_output_metadata(
        {
            "count_nodes": len(g.nodes),
            "count_edges": len(g.edges),
            "network_text": written,
        }
    )

    # write graph to file
    write_pickled_graph(g, p)

    return g
