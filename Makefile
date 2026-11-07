# AI Incident Atlas — reproducible pipeline. `make all` rebuilds everything downstream of the committed
# LLM extraction outputs (data/enrich/raw/*.json); re-running extraction itself needs an LLM (see docs/methodology.md).
PY ?= .venv/bin/python
.PHONY: all setup data ingest profile plan prepare validate status embed graph clusters insights evaluate export app verify test clean

all: ingest profile validate embed graph clusters insights evaluate export app

setup:
	uv venv -p 3.12 .venv && uv pip install -r requirements.txt && uv pip install -e .
	cd app && npm ci

data ingest:          ## Phase 0–1: download + checksum snapshot, load SQLite
	$(PY) -m atlas.ingest.load

profile:              ## Phase 1: reports/data_profile.md
	$(PY) -m atlas.ingest.profile

plan:                 ## Phase 3: deterministic batch plan (pilot → expert-labelled → stratified rest)
	$(PY) -m atlas.extract.batches plan

prepare:              ## Phase 3: write batch inputs with report excerpts (git-ignored)
	$(PY) -m atlas.extract.batches prepare

validate:             ## Phase 3: schema + verbatim quote grounding + privacy checks → SQLite
	$(PY) -m atlas.extract.validate
	$(PY) -m atlas.extract.validate second

status:
	$(PY) -m atlas.extract.status

embed:                ## Phase 5: sentence embeddings
	$(PY) -m atlas.embed.embed

graph:                ## Phase 5: multi-view similarity graphs with explained edges
	$(PY) -m atlas.graph.similarity

clusters: graph       ## Phase 5: UMAP + Ward, k by silhouette × stability; layout, bridges, entity network
	$(PY) -m atlas.graph.cluster

insights:             ## Phase 5: temporal + descriptive analyses
	$(PY) -m atlas.analysis.insights

evaluate:             ## Phase 4: agreement with expert labels and blind second coder
	$(PY) -m atlas.analysis.evaluation

export:               ## Phase 6: static JSON bundle for the app
	$(PY) -m atlas.export.bundle

app:                  ## Phase 6: build the static site
	cd app && npm run build

verify:               ## Phase 6: Playwright screenshots + "filters never rebuild nodes" check (needs `npx vite preview`)
	cd app && node scripts/verify.cjs http://localhost:4173/ ../docs/screenshots

test:
	$(PY) -m pytest -q
	cd app && npx vitest run

clean:
	rm -f data/atlas.sqlite
