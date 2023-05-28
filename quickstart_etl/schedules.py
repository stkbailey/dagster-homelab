from dagster import (
    ScheduleDefinition,
    define_asset_job,
)

from . import assets

daily_refresh_schedule = ScheduleDefinition(
    job=define_asset_job(name="all_assets_job"), cron_schedule="0 0 * * *"
)
