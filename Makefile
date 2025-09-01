fmt:
	poetry run ruff format .
	poetry run ruff check . --fix --unsafe-fixes
	poetry run toml-sort pyproject.toml

lint:
	poetry run ruff format --check .
	poetry run ruff check .
	poetry run toml-sort pyproject.toml --check

