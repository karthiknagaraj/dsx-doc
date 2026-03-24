# Usage Guide

## Overview

The DSX Documentation Assistant provides two primary interfaces:

- **Interactive UI (Streamlit)**: For manual exploration and documentation
- **CLI (Command-line)**: For batch processing and CI/CD automation

---

## Interactive UI (Streamlit)

### Starting the Application

```powershell
streamlit run frontend.py
```

The application will:
1. Load configuration from `.env` file
2. Initialize or connect to existing SQLite database
3. Open browser at `http://localhost:8501`

---

### Tab 1: 📝 Documentation

This tab handles DSX file ingestion and documentation generation.

#### Workflow: Ingest & Generate Docs

**Step 1: Upload DSX Files**

```
📝 Documentation Tab → 1) Upload .dsx files from your computer
```

- Click the file uploader
- Select one or more `.dsx` files
- Files are displayed in the upload widget

**Step 2: Ingest to Database**

```
Click → "Ingest to Database"
Wait for → "✓ Successfully processed X files"
```

Behind the scenes:
1. DSX files are parsed (XML → Canonical JSON)
2. Data is extracted (jobs, stages, links, parameters)
3. SQLite database is populated or updated
4. Previous data for same job is refreshed

**Step 3: Browse Database (Optional)**

After ingestion, view extracted metadata:

```
Select → Object Type (Jobs, Stages, Links, Parameters)
View → Table with all extracted data
Expand → Click rows to see full details
```

**Step 4: Generate Documentation**

```
Select → Job from dropdown list
Review → Job metadata and stage details (displayed info)
Click → "Generate Documentation for [Job Name]"
Wait → 10-30 seconds for LLM to process
```

What happens:
1. Job data, stages, and links are retrieved from database
2. A structured prompt is created
3. Selected LLM model generates documentation
4. Markdown is formatted and displayed
5. Documentation is saved to database

**Step 5: Download Documentation**

```
Click → "Download Markdown" button
Save → To your local computer (Filename: {JobName}__Documentation.md)
```

**Step 6: Reset Database (Optional)**

To start fresh:

```
Expand → "Reset Database" section
Click → "Confirm Reset"
Wait → Database cleared
```

Then re-ingest your files as needed.

---

### Tab 2: 🔎 Semantic Search

This tab enables searching across generated documentation using natural language.

#### Workflow: Search & Ask Questions

**Step 1: Select a Job**

```
Dropdown → Select DSX file
Dropdown → Select Job from that file
```

**Step 2: Build Document Chunks**

```
Click → "1) Build/update chunks"
Wait → "✓ Chunks built successfully"
```

This process:
1. Retrieves job documentation from database
2. Splits documentation into manageable chunks
3. Creates searchable index
4. Stores chunks in SQLite

**Step 3: Generate Embeddings**

```
Click → "2) Generate embeddings (API)"
Wait → "✓ Embeddings generated successfully"
```

This calls the embeddings API to:
1. Convert each chunk to a vector (1536 dimensions)
2. Store vectors in SQLite
3. Enable similarity-based search

**Step 4: Search Documents**

```
Text Input → "What columns are transformed?"
Click → "Search"
View → Results with relevance scores
```

The search:
1. Converts your query to a vector
2. Finds similar chunks using vector distance
3. Retrieves top 3-5 most relevant chunks
4. Returns chunks with source references

**Step 5: Ask Follow-up Questions (Chat)**

```
View → Retrieved chunks and summary
Type → Follow-up question in chat
Click → "Get Answer"
```

This:
1. Takes retrieved chunks as context
2. Sends your question to LLM
3. LLM answers based on documentation
4. Shows answer with citations

**Tips for Better Results:**

- Use specific terminology from your job
- Ask about data flows, transformations, and business rules
- Try questions like:
  - "What columns are transformed?"
  - "Which stages perform lookups?"
  - "What are the data quality checks?"
  - "How is the date calculated?"

---

## Command-Line Interface (CLI)

### Basic Usage

#### Generate docs for a single file

```powershell
python dsx_docs_cli.py --input job.dsx --output ./docs/
```

Output:
```
Processing: job.dsx
✓ Generated documentation: docs/job__SampleJob.md
```

#### Generate docs for multiple files (directory)

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/
```

Output:
```
Processing directory: dsx_files_input
✓ Processing: BilRev_Fact.dsx
✓ Processing: CASLDly010CustomerXpt.dsx
✓ Processing: CASLDly011CustomerIns.dsx
...
Summary: 8 files processed, 8 successful, 0 failed
```

---

### Advanced CLI Options

#### Parallel Processing (Faster)

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ --workers 4
```

- `--workers N`: Process N files concurrently
- Useful for large batches
- Default: 1 (sequential)

#### Skip Unchanged Files

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ --skip-unchanged
```

- Maintains `.dsx_checksums.json` to track changes
- Skips files that haven't been modified
- Useful for CI/CD pipelines to save API costs

#### Custom API Key

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ --api-key "sk-..."
```

- Override environment variable
- Useful for CI/CD with secrets management

#### Custom Model

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ --model "openai/gpt-4"
```

- Change LLM model on-the-fly
- See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for available models

#### JSON Output (for CI/CD)

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ --json-output results.json
```

Output file `results.json`:
```json
{
  "status": "success",
  "timestamp": "2025-03-24T10:30:00Z",
  "summary": {
    "total_files": 8,
    "successful": 8,
    "failed": 0,
    "skipped": 1
  },
  "results": [
    {
      "file_name": "BilRev_Fact.dsx",
      "status": "success",
      "documentation_file": "BilRev_Fact__BilRev_Fact.md",
      "tokens_used": 2150,
      "processing_time_sec": 12.5
    }
  ]
}
```

#### Fail on Error (for CI/CD)

```powershell
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/ --fail-on-error
```

- Exit code 2 if any file fails
- Exit code 1 if partial failures
- Exit code 0 if all successful
- Useful for GitHub Actions to block on failures

---

### CLI Exit Codes

```powershell
# Check exit code after running
echo $LASTEXITCODE
```

| Code | Meaning | Use Case |
|------|---------|----------|
| 0 | Success - all files processed | CI/CD approval |
| 1 | Partial failure - some files failed | Investigation needed |
| 2 | Total failure - no files processed | Block CI/CD pipeline |
| 3 | Configuration error | Check API key and paths |

---

### Complete CLI Example (CI/CD Pipeline)

```powershell
# Set up (already done in CI/CD)
$env:DSX_API_KEY = "sk-..."
$env:DSX_CHAT_MODEL = "openai/gpt-4"

# Run documentation generation
python dsx_docs_cli.py `
  --input ./dsx_files_input/ `
  --output ./dsx_docs_output/ `
  --workers 4 `
  --skip-unchanged `
  --json-output results.json `
  --fail-on-error

# Check result
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Documentation generated successfully"
    Get-Content results.json | ConvertFrom-Json | Format-Table
} else {
    Write-Host "✗ Failed to generate documentation"
    exit $LASTEXITCODE
}
```

---

## Output Examples

### Generated Markdown Documentation

After documentation generation, you'll get a file like `BilRev_Fact__BilRev_Fact.md`:

```markdown
# BilRev_Fact (DSX file: BilRev_Fact.dsx)

## Overview
This job loads billing revenue facts from source systems into the data warehouse.

## Inputs (Sources)
| Source | Type | Notes |
|---|---|---|
| Oracle DB | DS2Stage | Legacy billing system |
| Staging Area | DS2Stage | Pre-processed data |

## Outputs (Targets)
| Target | Type | Notes |
|---|---|---|
| Warehouse DB | TargetStage | Fact table for BI reporting |

## Data Flow
Oracle → Staging → Deduplication → Join with Master → Filtering → Warehouse

## Transformations
- **Deduplication**: Remove duplicate billing records from source
- **Master join**: Enrich with customer master data
- **Filtering**: Keep only valid transactions (status = 'ACTIVE')
- **Calculation**: Derive net revenue = gross - discounts

## Parameters
- P_RunDate: Execution date (format: YYYY-MM-DD)
- P_Environment: Target environment (DEV/TEST/PROD)
```

---

## Common Tasks

### Task 1: Generate Docs for All Jobs

```powershell
# Interactive (Streamlit)
streamlit run frontend.py
# Then use UI to select jobs one by one

# Or CLI (Batch)
python dsx_docs_cli.py --input ./dsx_files_input/ --output ./dsx_docs_output/
```

### Task 2: Search Across Specific Job

```
🔎 Semantic Search Tab
→ Select Job
→ Build Chunks
→ Generate Embeddings
→ Ask Question
```

### Task 3: Automate in GitHub

```yaml
# .github/workflows/generate-docs.yml (already prepared)
# Push .dsx files → GitHub automatically generates docs
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for setup.

### Task 4: Integrate with Own System

```powershell
# Import and use as module
python -c "
from doc_generator import generate_job_docs, load_chat_config
from dsx_to_canonical import parse_dsx_file

# Parse DSX
dsx_data = parse_dsx_file('myfile.dsx')

# Generate docs
cfg = load_chat_config()
markdown, metadata = generate_job_docs(dsx_data, '', cfg)

print(markdown)
"
```

---

## Performance Tips

### Speed Up Documentation Generation

1. **Use faster model** (trades quality for speed):
   ```env
   DSX_CHAT_MODEL=openai/gpt-3.5-turbo
   ```

2. **Increase timeout** (for slow connections):
   ```env
   DSX_CHAT_TIMEOUT_SEC=300
   ```

3. **Use batch processing** with workers:
   ```powershell
   python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --workers 4
   ```

4. **Skip unchanged files**:
   ```powershell
   python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --skip-unchanged
   ```

### Reduce API Costs

1. **Use cheaper model** (good quality/cost ratio):
   ```env
   DSX_CHAT_MODEL=openai/gpt-oss-120b
   ```

2. **Cache documentation** - Don't regenerate unchanged jobs

3. **Use semantic search** instead of regenerating - Ask questions over existing docs

---

## Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions to common issues.

