from dagster import asset, OpExecutionContext
from quickstart_etl.resources import SubstackResource
from dagster_duckdb import DuckDBResource


@asset
def substack_stats(
    context: OpExecutionContext, substack: SubstackResource, duckdb: DuckDBResource
):
    # Print the status code
    SUBDOMAINS = [
        "stkbailey",
        # "ribbonfarmstudio",
        # "benn",
        # "analyticsengineeringroundup",
        # "mikkeldengsoe",
        # "erikhoel"
    ]
    for s in SUBDOMAINS:
        output = substack.scrape(s, search_distance=3)
        substack.write_scrape_output_duckdb(output, prefix=s, dir="output")

    return "name"
