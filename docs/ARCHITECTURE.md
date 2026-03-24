# DSX Documentation Assistant - Architecture Guide

## System Overview

The DSX Documentation Assistant is a Python-based tool that parses IBM DataStage export files (DSX format) and generates comprehensive, AI-powered documentation. It operates in two modes: **Interactive UI** (Streamlit) and **CLI** (for CI/CD integration).

```
┌─────────────────────────────────────────────────────┐
│                    User Input                        │
│         (DSX Files, Upload, API Keys)               │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌───────▼──────────┐
│  Streamlit UI  │      │  CLI Interface   │
│  (frontend.py) │      │  (dsx_docs_cli) │
└───────┬────────┘      └───────┬──────────┘
        │                       │
        └───────────┬───────────┘
                    │
        ┌───────────▼────────────┐
        │  DSX Parser Module     │
        │ (dsx_to_canonical.py) │
        │  - Parse XML          │
        │  - Extract metadata   │
        │  - Build job model    │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  SQLite Database       │
        │  (dsx_graph_all.sqlite)│
        │  - Jobs               │
        │  - Stages             │
        │  - Links              │
        │  - Parameters         │
        └───────────┬────────────┘
                    │
        ┌───────────▼──────────────┐
        │  Doc Generation Engine   │
        │  (doc_generator.py)      │
        │  - LLM Integration       │
        │  - Markdown Generation   │
        │  - Chunking & Formatting │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │  Semantic Search Engine  │
        │  (embeddings.py)         │
        │  - Vector Search         │
        │  - Chunk Management      │
        │  - LLM Chat Integration  │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │   Output Generation      │
        │  - Markdown Docs         │
        │  - JSON Reports          │
        │  - Search Results        │
        └──────────────────────────┘
```

---

## Core Modules

### 1. **frontend.py** - Streamlit Application
- **Purpose**: User-facing web interface
- **Components**:
  - Tab navigation (Documentation & Semantic Search)
  - Session state management
  - Error handling and display
- **Responsibilities**:
  - Route user requests to appropriate tabs
  - Manage Streamlit page configuration
  - Display application layout and branding

### 2. **dsx_to_canonical.py** - DSX Parser
- **Purpose**: Parse DataStage DSX files into canonical data model
- **Key Functions**:
  - XML parsing
  - Job metadata extraction
  - Stage definition extraction
  - Link/connection mapping
  - Parameter identification
- **Output**: Canonical JSON representation of DSX structure
- **Supported Elements**:
  - Jobs (main executable units)
  - Stages (processing components)
  - Links (data connections)
  - Parameters (job variables)

### 3. **doc_generator.py** - Documentation Engine
- **Purpose**: Generate human-readable Markdown documentation using LLM
- **Key Components**:
  - `ChatConfig`: Configuration for LLM API calls
  - `load_chat_config()`: Load credentials from environment
  - `generate_job_docs()`: Main documentation generation function
  - `_request_json()`: HTTP client for LLM API
- **Process**:
  1. Format canonical DSX data as context
  2. Prepare structured prompt for LLM
  3. Call LLM API (OpenRouter or compatible)
  4. Parse and format response as Markdown
  5. Generate metadata (tokens used, etc.)
- **Output Format**: Markdown with structured sections

### 4. **embeddings.py** - Vector Search Engine
- **Purpose**: Enable semantic search over documentation
- **Capabilities**:
  - Generate vector embeddings for document chunks
  - Store embeddings in SQLite
  - Perform semantic search queries
  - Retrieve relevant chunks for LLM context
- **Integration Points**:
  - Takes generated Markdown documentation
  - Chunking strategy (sentence/paragraph level)
  - Embedding API integration

### 5. **tab_documentation.py** - Documentation Tab
- **Purpose**: Streamlit interface for documentation generation
- **Features**:
  - DSX file upload interface
  - File ingestion to SQLite
  - Database browsing and inspection
  - Documentation generation triggers
  - Download generated docs
- **Workflow**:
  1. Upload DSX files
  2. Parse and ingest to database
  3. Browse extracted metadata
  4. Generate documentation
  5. Download or view results

### 6. **tab_semantic_search.py** - Search Tab
- **Purpose**: Streamlit interface for semantic search
- **Features**:
  - Job selection
  - Chunk building
  - Embedding generation
  - Query input
  - Results display with citations
- **Workflow**:
  1. Build/update chunks from documentation
  2. Generate embeddings
  3. Execute semantic search
  4. Display results and citations

### 7. **dsx_docs_cli.py** - Command-Line Interface
- **Purpose**: Batch processing and CI/CD integration
- **Features**:
  - Batch file processing
  - Directory scanning
  - Progress reporting
  - JSON output
  - Exit codes for pipeline integration
- **CLI Arguments**:
  - `--input`: Input DSX file or directory
  - `--output`: Output documentation directory
  - `--api-key`: LLM API key
  - `--workers`: Concurrent processing workers
  - `--json-output`: Machine-readable results

### 8. **utils.py** - Utility Functions
- **Purpose**: Shared helper functions
- **Includes**:
  - File I/O helpers
  - Path normalization
  - Logging utilities
  - Common data transformations

---

## Data Models

### Canonical DSX Model
```json
{
  "dsx_file_id": "uuid",
  "file_name": "JobName.dsx",
  "jobs": [
    {
      "job_id": "unique_id",
      "job_name": "Job Display Name",
      "job_description": "Optional description",
      "stages": [
        {
          "stage_id": "stage_1",
          "stage_name": "Source Stage",
          "stage_type": "DS2Stage|Transformer|TargetStage",
          "properties": { "key": "value" },
          "columns": [
            {
              "column_name": "col1",
              "data_type": "string",
              "length": 255
            }
          ]
        }
      ],
      "links": [
        {
          "from_stage": "stage_1",
          "to_stage": "stage_2",
          "link_name": "link_1"
        }
      ],
      "parameters": [
        {
          "param_name": "P_StartDate",
          "param_type": "string",
          "default_value": "2025-01-01"
        }
      ]
    }
  ]
}
```

### Database Schema
- **jobs** table: Job metadata
- **stages** table: Stage definitions
- **links** table: Inter-stage connections
- **columns** table: Column definitions
- **parameters** table: Job parameters
- **job_documentation** table: Generated documentation
- **embeddings** table: Vector embeddings for search

---

## API Integration

### LLM Provider: OpenRouter
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Models Supported**:
  - `openai/gpt-oss-120b` (default - balanced cost/quality)
  - `openai/gpt-4` (premium quality)
  - `openai/gpt-3.5-turbo` (fast, budget-friendly)
- **Authorization**: API Key in headers
- **Request Format**: OpenAI-compatible Chat Completion API
- **Timeout**: 180 seconds (configurable)
- **Retry Logic**: 3 attempts with exponential backoff

### Embedding Provider: OpenRouter Embeddings
- **Endpoint**: `https://openrouter.ai/api/v1/embeddings`
- **Models**: `openai/text-embedding-3-small` (default)
- **Dimensions**: 1536
- **Uses**: Semantic search and relevance ranking

---

## Configuration Management

### Environment Variables
```env
DSX_API_KEY                 # Required: API key for LLM provider
DSX_CHAT_MODEL             # Optional: Model selection (default: openai/gpt-oss-120b)
DSX_CHAT_BASE_URL          # Optional: API base URL
DSX_CHAT_PROVIDER          # Optional: Provider name (default: openrouter)
DSX_CHAT_TIMEOUT_SEC       # Optional: Request timeout in seconds
DSX_CHAT_MAX_RETRIES       # Optional: Max retry attempts
DSX_DOCS_MAX_WORKERS       # Optional: Concurrent workers for batch processing
```

### Files
- `.env`: Local environment file (Git-ignored)
- `.env.example`: Template for required variables
- `.streamlit/config.toml`: Streamlit configuration
- `.streamlit/secrets.toml`: Secret management (alternative to .env)

---

## Deployment Architecture

### Docker Container
- **Base Image**: `python:3.11-slim`
- **Port**: 8501 (Streamlit default)
- **Health Check**: Streamlit health endpoint
- **Volumes**:
  - `/app/data`: SQLite database persistence
  - `/app/dsx_files`: DSX file input directory

### Docker Compose
- **Services**: Single service (DSX Assistant)
- **Networking**: Default bridge network
- **Restart Policy**: Unless stopped
- **Environment**: Loaded from `.env` file

### GitHub Actions Workflow
- **Trigger**: Push to repository
- **Steps**:
  1. Check out code
  2. Set up Python 3.11
  3. Install dependencies
  4. Run CLI on DSX files
  5. Commit generated documentation
  6. Push changes back to repo
- **Exit Codes**:
  - 0: Success
  - 1: Partial failure
  - 2: Total failure
  - 3: Configuration error

---

## Data Flow Examples

### Documentation Generation Flow
```
User Upload → Parse DSX → Extract Metadata → Store in SQLite
    ↓
Retrieve from SQLite → Build Prompt → Call LLM → Format Response
    ↓
Save Markdown → Display in UI/CLI → Download/Commit
```

### Semantic Search Flow
```
Select Job → Load Documentation → Chunk Content → Generate Embeddings
    ↓
Store in SQLite → User Query → Generate Query Embedding → Vector Search
    ↓
Retrieve Top-K Chunks → Build Context → Call LLM → Return Answer
```

---

## Security Considerations

### API Key Management
- Never commit `.env` file
- Store secrets in GitHub Secrets for CI/CD
- Support `.streamlit/secrets.toml` for local dev
- Environment variable isolation

### Database Security
- SQLite file in local `./data/` directory
- No remote database exposure
- Local-only access for Streamlit app

### Input Validation
- DSX file format validation
- API response validation
- Error handling without exposing internals

---

## Performance Characteristics

### Parsing
- Single DSX file: < 5 seconds
- Metadata extraction: O(1) per job
- Database indexing: On job_id, stage_id

### Documentation Generation
- Per-job: 10-30 seconds (depends on size and LLM)
- Concurrent batch: Scales with workers parameter
- API timeout: 180 seconds (configurable)

### Semantic Search
- Embedding generation: ~2-3 seconds per job
- Vector search: < 1 second per query
- Top-K retrieval: Constant time

---

## Extension Points

1. **Custom LLM Models**: Modify `load_chat_config()` and `generate_job_docs()`
2. **Alternative Embedding Providers**: Replace embeddings.py integration
3. **Output Formats**: Extend `doc_generator.py` for PDF, HTML, etc.
4. **Database Backends**: Use SQLAlchemy for portability
5. **Authentication**: Add user management layer in frontend.py
6. **Custom Prompts**: Create prompt templates for different job types

---

## Dependencies Overview

### Core
- `streamlit`: Web UI framework
- `python-dotenv`: Environment configuration
- `requests` / `urllib3`: HTTP client
- `jsonschema`: Schema validation

### Optional
- `pytest`: Testing framework
- `docker`: Containerization

For complete requirements, see [requirements.txt](../requirements.txt)

