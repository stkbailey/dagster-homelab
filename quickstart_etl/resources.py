from dagster import ConfigurableResource
from dagster_duckdb import DuckDBResource

from .utils import SubstackClient


class SubstackResource(ConfigurableResource):
    root_subdomain = "https://substack.com/api/v1"
    request_backoff = 1

    def get_substack_client(self):
        return SubstackClient()


# initialize the resources for execution
duckdb_init = DuckDBResource(database="output/duckdb.db")
substack_init = SubstackResource(root_subdomain="https://substack.com/api/v1")
