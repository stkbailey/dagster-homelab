run:
	dagster dev

setup:
	pip install -e .[dev]

format:
	black . && isort .

materialize:
	dagster asset materialize -m quickstart_etl --select substack_graph

test:
	pytest quickstart_etl_tests