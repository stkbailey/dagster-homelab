run:
	dagster dev

setup:
	pip install -e .[dev]

format:
	black . && isort .

materialize:
	dagster asset materialize -m dagster_repo --select substack_graph

test:
	pytest tests
