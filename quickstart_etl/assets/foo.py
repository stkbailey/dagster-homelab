from dagster import asset


@asset
def foo():
    return "bar"