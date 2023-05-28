run:
	dagster dev

setup:
	pip install -e .[extra]

format:
	black .

materialize:
	dagster asset materialize -m quickstart_etl --select substack_stats

test:
	pytest quickstart_etl_tests