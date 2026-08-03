# RAG Integration — Context for Claude Code

## Goal
Add a RAG-based "AI Assistant" module (Phase 3 on the README roadmap) to this
project: root cause analysis and natural language investigation over data
quality validation results, using retrieval-augmented generation.

## What's already built and working (prototype scripts in rag_prototype/)
- `day11_azure_search_connection.py` — confirms Azure AI Search connectivity,
  creates a basic index.
- `day12_azure_pipeline.py` — full pipeline: section-aware chunking, OpenAI
  embeddings (text-embedding-3-small, 1536 dimensions), upload to Azure AI
  Search with a vector field (HNSW), threshold-filtered retrieval, generation
  via gpt-4o-mini.
- `day13_real_project.py` — same pipeline, indexed against this repo's real
  README content instead of placeholder text.
- `src/rag_engine.py` — `chunk_reports()` is implemented (2026-07-30): reads
  `reports/validation_report.csv` and `reports/history.csv` and produces one
  chunk per failed validation rule and one chunk per historical quality-score
  entry, each tagged with flat `table_name` and `type`
  (`validation_failure` / `history_entry`) fields — the shape needed to slot
  straight into the `day12/13` embed-and-upload flow. This is real chunking
  of real pipeline output, not the placeholder README chunks from Day 13.
  Not yet done: embedding these chunks, uploading them to the Azure index, or
  wiring retrieval over them into an actual assistant module.

## Key calibrated values (don't reset these without re-testing)
- Embedding model: `text-embedding-3-small` (1536 dims)
- Chat model: `gpt-4o-mini`, temperature=0 for deterministic outputs
- Azure AI Search similarity threshold: 0.56 (cosine similarity, higher =
  better match) — calibrated against this project's actual content, not a
  generic default. This was calibrated against README chunks only
  (`day13_real_project.py`) — it has NOT been re-validated against the
  validation-failure / history-entry chunks from `rag_engine.py`, which are
  shorter and more numeric/templated. Re-calibrate against real vs.
  irrelevant queries over those chunks before trusting 0.56 for report data.
- `rag_engine.py`'s `FAILED_ROWS_SAMPLE_SIZE = 10` — capped sample size for
  failed-row indices per validation-failure chunk. Calibrated against
  `reports/validation_report.csv`'s actual failed-row-count distribution as
  of 2026-07-30 (real Unity Catalog data: range 4-35, median 14, 25th
  percentile 8). Re-check this distribution if failure volumes change
  significantly.
- Index name: `dq-assistant-index`, fields: id, content, source, section,
  content_vector. Will need `table_name` and `type` added as filterable
  fields to support the report chunks from `rag_engine.py` (mirroring the
  flat metadata style already used for `source`/`section`).

## Environment variables already set locally (do not hardcode these)
- OPENAI_API_KEY
- AZURE_SEARCH_ENDPOINT
- AZURE_SEARCH_KEY

## Honest current gap (updated 2026-07-30)
The Unity Catalog question below is resolved: option (a) was taken.
`src/file_loader.py` now has `load_table_from_databricks(catalog, schema,
table_name)` using `databricks-sql-connector`, reading credentials from
`DATABRICKS_SERVER_HOSTNAME` / `DATABRICKS_HTTP_PATH` / `DATABRICKS_TOKEN`
env vars (never hardcoded) and running a plain `SELECT *` against real Unity
Catalog tables (`dq_assistant.bronze.customers` / `.products`, confirmed
working via `src/test_databricks_connection.py`). `src/validator.py` now
takes `--source csv` (default, unchanged) or `--source databricks`, and both
paths return the same DataFrame shape so everything downstream (rule engine,
report generator, dashboard) is untouched. `reports/validation_report.csv`
and `reports/history.csv` are now genuinely produced from real Unity Catalog
data, not placeholder CSVs.

What this is NOT: there's no Delta Lake write path, no lineage, no
Unity Catalog permissions/governance layer, and no streaming — this is a
read-only query path against existing managed tables. If "Unity Catalog
integration" needs to mean governance features for an interview narrative,
that's still unbuilt and should be scoped separately.

The remaining real gap is on the RAG side: `src/ai_assistant.py` still calls
OpenAI directly with no retrieval step, so it can't yet answer questions
grounded in `reports/validation_report.csv` / `reports/history.csv`.
`rag_engine.py`'s `chunk_reports()` produces the chunks (see above) but
nothing yet embeds, indexes, or retrieves them.

## What to actually build next
1. ~~Wire the RAG pipeline from `day12/day13` into the existing project
   structure~~ — in progress. `chunk_reports()` in `src/rag_engine.py` is
   done. Still needed: embed those chunks (`text-embedding-3-small`, per the
   calibrated values above), upload to the `dq-assistant-index` Azure index
   (extending its schema with `table_name`/`type` fields), and add a
   retrieval + generation path — either extend `src/rag_engine.py` or wire
   it into `src/ai_assistant.py` (decide which; `ai_assistant.py` is the
   module the README's Phase 3 section actually names).
2. Done: the real "documents" are now the pipeline's own outputs
   (`validation_report.csv`, `history.csv`) via `rag_engine.py`, not the
   README. This is what makes "why did customer quality score drop this
   week" (the README's Phase 3 example) answerable — once retrieval is wired
   up over these chunks.
3. Unity Catalog decision — resolved, see above. Any further Databricks
   governance work (lineage, permissions, Delta writes) is a new, separate
   decision, not implied by what's built.
4. Keep the retrieval threshold calibration workflow (measure real vs.
   irrelevant query distances, don't guess) — this was a deliberate,
   hard-won practice from earlier sessions and should carry into the real
   implementation. Specifically: 0.56 was calibrated against README chunks
   and has NOT been validated against the shorter, more templated
   validation-failure / history-entry chunks — re-run the calibration
   against real queries over those before trusting it.
