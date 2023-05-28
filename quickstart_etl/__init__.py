from dagster import (
    Definitions,
    load_assets_from_package_module,
)

from . import assets
from .schedules import daily_refresh_schedule
from .resources import substack_init, duckdb_init


defs = Definitions(
    assets=load_assets_from_package_module(assets),
    schedules=[daily_refresh_schedule],
    resources={"substack": substack_init, "duckdb": duckdb_init},
)
