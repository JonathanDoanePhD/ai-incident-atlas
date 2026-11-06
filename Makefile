PY ?= .venv/bin/python
.PHONY: all setup data ingest profile taxonomy extract-prepare extract-validate evaluate embed graph analysis export app test clean

all: ingest profile taxonomy extract-validate evaluate embed graph analysis export app

setup:
	uv venv -p 3.12 .venv && uv pip install -r requirements.txt && uv pip install -e .
	cd app && npm ci

data ingest:
	$(PY) -m atlas.ingest.load

profile: ingest
	$(PY) -m atlas.ingest.profile

test:
	$(PY) -m pytest -q
	cd app && npx vitest run

clean:
	rm -f data/atlas.sqlite
