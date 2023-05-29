from setuptools import find_packages, setup

setup(
    name="dagster_repo",
    packages=find_packages(exclude=["tests", "terraform"]),
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
