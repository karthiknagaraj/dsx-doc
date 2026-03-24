# dsx-doc-assistant

Parse IBM DataStage `.dsx` exports and generate human-readable documentation using AI.

**Two modes available:**
1. **Interactive UI** (Streamlit) - For manual documentation generation and exploration
2. **CI/CD Plugin** (CLI) - For automated documentation in pipelines

## Features

- Browse **jobs / stages / links / parameters**
- Generate **Markdown documentation** for each job (non-technical audience)
- Ask **human-readable questions** over the generated docs (semantic retrieval + chat answers)
- **CI/CD integration** - Automate documentation in your pipeline

---

## Quick Start

### Option 1: Interactive UI (Streamlit)

```powershell
python -m streamlit run .\frontend.py
```

In the app:

1. **� Documentation** → Upload .dsx files and generate Markdown docs
2. **🔎 Semantic Search** → Build chunks, generate embeddings, and search

### Option 2: CI/CD Plugin (Command Line)

```bash
# Generate docs for all .dsx files
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/

# For CI/CD pipelines (with JSON output)
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ \
    --json-output results.json --fail-on-error
```

**See [GITHUB_AUTOMATION_SETUP.md](GITHUB_AUTOMATION_SETUP.md) for GitHub setup guide.**  
**See [CI_CD_INTEGRATION.md](CI_CD_INTEGRATION.md) for other CI/CD platforms.**

---

## How to use the app (step-by-step)

### 🗃️ DB Browser

Use this tab to ingest one or more `.dsx` files into the local SQLite database and browse what was extracted.

1. Open the app and select **🗃️ DB Browser** in the sidebar.
2. Upload one or more `.dsx` files.
3. Click the ingest button and wait for the results table.
4. Browse extracted objects (jobs, stages, links, etc.).

**Resetting the database (optional):**

1. In **🗃️ DB Browser**, open the **Reset database** section.
2. Confirm reset.
3. Re-ingest your DSX files.

Notes:

- The app uses a single DB file: `dsx_graph_all.sqlite`.
- Re-ingesting the same DSX file is safe; rows are refreshed for that job/file.

### 🔎 Semantic Search

Use this tab to search across ingested content using embeddings (vector search).

1. Select **🔎 Semantic Search** in the sidebar.
2. Pick a DSX file/job from **Select DSX job**.
3. Run **1) Build/update chunks**.
  - Docs-first: by default the app indexes stored Markdown job docs.
4. Run **2) Generate embeddings (API)**.
  - This calls an OpenAI-compatible `/embeddings` endpoint (defaults target OpenRouter).
5. In **3) Search**, type a question and click **Search**.
6. Review the **answer** and optionally expand retrieved chunks (citations source).

Tips:

- If you see *no results*, you likely haven’t generated embeddings for that DSX file yet.
- Use the **Docs only** quick filter (when present) to search only generated documentation chunks:
- `job_documentation_md`

### (Optional) CLI ingest

```powershell
python .\dsx_to_sqlite.py .\dsx_files\CiamShared230_Load_SixNode.dsx --db .\dsx_graph_all.sqlite
```

## Database & schema

- `dsx_graph_all.sqlite` is a **generated local artifact** (ignored by `.gitignore`).
- Schema lives in `dsx_sqlite_schema.sql`.

Rebuild the DB from the committed samples:

```powershell
python .\reingest_samples.py
```

Note: This repo focuses on docs-first metadata + documentation. Raw DSX record bodies are not surfaced in the default UI.

## What gets stored (high level)

- `dsx_file`, `job`, `job_parameter`
- `stage`, `stage_property`, `pin`
- `link`, `link_column`
- `graph_edge` (generic structural edges)
- `doc_chunk`, `doc_embedding` (semantic search)

## Semantic Search (API embeddings)

The embeddings client uses an OpenAI-compatible `/embeddings` endpoint (defaults target **OpenRouter**).

Environment variables:

- `DSX_API_KEY` (required)
- `DSX_MODEL` (optional, default: `openai/text-embedding-3-small`)
- `DSX_BASE_URL` (optional, default: `https://openrouter.ai/api/v1`)
- `DSX_PROVIDER` (optional, default: `openrouter`)
- `DSX_OPENROUTER_HTTP_REFERER` (optional)
- `DSX_OPENROUTER_X_TITLE` (optional)

Legacy variable names are still supported (backward compatible):
`DSX_EMBEDDINGS_API_KEY`, `DSX_EMBEDDINGS_MODEL`, `DSX_EMBEDDINGS_BASE_URL`, `DSX_EMBEDDINGS_PROVIDER`.

PowerShell example:

```powershell
$env:DSX_API_KEY = "..."
$env:DSX_MODEL = "openai/text-embedding-3-small"
$env:DSX_BASE_URL = "https://openrouter.ai/api/v1"
$env:DSX_OPENROUTER_HTTP_REFERER = "http://localhost"
$env:DSX_OPENROUTER_X_TITLE = "dsx-doc-assistant"
```

## Deployment & Sharing

Want to share this tool with your team or automate documentation?

**For GitHub Automation:**
- See **[GITHUB_AUTOMATION_SETUP.md](GITHUB_AUTOMATION_SETUP.md)** - Setup automated doc generation on GitHub

**For Other CI/CD Platforms:**
- See **[CI_CD_INTEGRATION.md](CI_CD_INTEGRATION.md)** - Examples for GitLab, Jenkins, Azure DevOps, etc.

**For Docker Deployment:**
```powershell
# Build and run with Docker
docker-compose up
```

---

## Project Structure

```
dsx-doc-assistant/
├── frontend.py                    # Streamlit UI
├── dsx_docs_cli.py               # CLI tool for automation
├── doc_generator.py              # Documentation generation logic
├── dsx_to_canonical.py           # DSX file parser
├── embeddings.py                 # Semantic search functionality
├── tab_documentation.py          # Documentation tab UI
├── tab_semantic_search.py        # Semantic search tab UI
├── utils.py                      # Utility functions
├── requirements.txt              # Python dependencies
├── dsx_files_input/              # Input: Your .dsx files
├── dsx_docs_output/              # Output: Generated markdown docs
├── .github/workflows/            # GitHub Actions automation
│   └── generate-docs.yml
└── Documentation/
    ├── README.md                 # This file
    ├── GITHUB_AUTOMATION_SETUP.md
    └── CI_CD_INTEGRATION.md
```

---

## Example SQL

Stages in a job:

```sql
SELECT j.job_name, s.stage_name, s.stage_type
FROM job j
JOIN stage s ON s.job_id = j.job_id
ORDER BY j.job_name, s.stage_name;
```

Lineage (stage-to-stage):

```sql
SELECT
  l.link_name,
  s1.stage_name AS source_stage,
  s2.stage_name AS target_stage
FROM link l
JOIN stage s1 ON s1.stage_id = l.source_stage_id
JOIN stage s2 ON s2.stage_id = l.target_stage_id
ORDER BY s1.stage_name, l.link_name;
```
