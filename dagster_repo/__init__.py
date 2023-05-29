from dagster import Definitions, load_assets_from_package_module

from . import assets
from .resources import duckdb_init, substack_init
from .schedules import daily_refresh_schedule

defs = Definitions(
    assets=load_assets_from_package_module(assets),
    schedules=[daily_refresh_schedule],
    resources={"substack": substack_init, "duckdb": duckdb_init},
)
