from setuptools import find_packages, setup

setup(
    name="quickstart_etl",
    packages=find_packages(exclude=["quickstart_etl_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "boto3",
        "pandas",
        "requests",
        "dagster-duckdb",
        "beautifulsoup4",
        "networkx",
    ],
    extras_require={"dev": ["dagit", "pytest", "black", "isort"]},
)
