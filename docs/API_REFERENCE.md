# API Reference

## Module: doc_generator

Main module for generating documentation using LLM.

### Class: ChatConfig

Configuration for LLM API interactions.

```python
@dataclass
class ChatConfig:
    api_key: str                          # API key for LLM provider (required)
    model: str                            # Model name (default: "openai/gpt-oss-120b")
    base_url: str                         # API base URL (default: "https://openrouter.ai/api/v1")
    provider: str                         # Provider name (default: "openrouter")
    http_referer: Optional[str]           # HTTP referer header (optional)
    x_title: Optional[str]                # X-Title header (optional)
    timeout_sec: int                      # Request timeout in seconds (default: 180)
    max_retries: int                      # Maximum retry attempts (default: 3)
    retry_backoff_sec: float              # Retry backoff duration (default: 1.0)
```

### Function: load_chat_config()

Load chat configuration from environment variables.

```python
def load_chat_config() -> ChatConfig
```

**Environment Variables:**
- `DSX_API_KEY` (required): API key for LLM provider
- `DSX_CHAT_MODEL` (optional): Model selection
- `DSX_CHAT_BASE_URL` (optional): API base URL
- `DSX_CHAT_PROVIDER` (optional): Provider name
- `DSX_OPENROUTER_HTTP_REFERER` (optional): HTTP referer
- `DSX_OPENROUTER_X_TITLE` (optional): X-Title header

**Returns:**
- `ChatConfig` object with loaded settings

**Raises:**
- `ValueError`: If `DSX_API_KEY` not set

**Example:**
```python
from doc_generator import load_chat_config

cfg = load_chat_config()
print(f"Using model: {cfg.model}")
print(f"Timeout: {cfg.timeout_sec}s")
```

---

### Function: generate_job_docs()

Generate documentation for a DataStage job.

```python
def generate_job_docs(
    canonical: Dict[str, Any],
    dsx_text: str,
    cfg: ChatConfig
) -> Tuple[str, Dict[str, Any]]
```

**Parameters:**
- `canonical` (dict): Canonical DSX data model (from parser)
- `dsx_text` (str): Original DSX file content (for reference)
- `cfg` (ChatConfig): LLM configuration

**Returns:**
- Tuple of:
  - `markdown` (str): Generated Markdown documentation
  - `metadata` (dict): Metadata including:
    - `tokens_used`: Total tokens consumed
    - `model`: Model used
    - `timestamp`: Generation timestamp
    - `prompt_tokens`: Input tokens
    - `completion_tokens`: Output tokens

**Raises:**
- `ValueError`: If API key invalid
- `requests.exceptions.Timeout`: If request times out
- `requests.exceptions.ConnectionError`: If cannot connect to API

**Example:**
```python
from doc_generator import generate_job_docs, load_chat_config
from dsx_to_canonical import parse_dsx_file

# Load configuration
cfg = load_chat_config()

# Parse DSX file
canonical = parse_dsx_file("myjob.dsx")

# Generate documentation
markdown, metadata = generate_job_docs(canonical, "", cfg)

print(markdown)
print(f"Tokens used: {metadata['tokens_used']}")
```

---

## Module: dsx_to_canonical

Parser for converting DSX XML to canonical data model.

### Function: parse_dsx_file()

Parse a DataStage DSX export file.

```python
def parse_dsx_file(file_path: str) -> Dict[str, Any]
```

**Parameters:**
- `file_path` (str): Path to .dsx file

**Returns:**
- `canonical` (dict): Canonical representation with structure:
  ```json
  {
    "dsx_file_id": "unique_id",
    "file_name": "Job.dsx",
    "jobs": [
      {
        "job_id": "id",
        "job_name": "name",
        "job_description": "description",
        "stages": [...],
        "links": [...],
        "parameters": [...]
      }
    ]
  }
  ```

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `xml.etree.ElementTree.ParseError`: If XML is invalid

**Example:**
```python
from dsx_to_canonical import parse_dsx_file

canonical = parse_dsx_file("BilRev_Fact.dsx")
print(f"Jobs found: {len(canonical['jobs'])}")
for job in canonical['jobs']:
    print(f"  - {job['job_name']}: {len(job['stages'])} stages")
```

---

## Module: embeddings

Vector embeddings and semantic search.

### Function: generate_embeddings()

Generate vector embeddings for text chunks.

```python
def generate_embeddings(
    texts: List[str],
    cfg: ChatConfig
) -> List[List[float]]
```

**Parameters:**
- `texts` (List[str]): Text chunks to embed
- `cfg` (ChatConfig): LLM configuration (for API settings)

**Returns:**
- `embeddings` (List[List[float]]): Vector embeddings (1536-dim by default)

**Example:**
```python
from embeddings import generate_embeddings
from doc_generator import load_chat_config

cfg = load_chat_config()
texts = ["This job transforms customer data", "Lookups enriched with master data"]
embeddings = generate_embeddings(texts, cfg)
print(f"Generated {len(embeddings)} embeddings of {len(embeddings[0])} dimensions")
```

---

### Function: semantic_search()

Search for relevant chunks based on semantic similarity.

```python
def semantic_search(
    query: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    top_k: int = 5
) -> List[Dict[str, Any]]
```

**Parameters:**
- `query` (str): Search query
- `chunks` (List[dict]): Document chunks with texts
- `embeddings` (List[List[float]]): Pre-computed embeddings for chunks
- `top_k` (int): Number of results to return (default: 5)

**Returns:**
- `results` (List[dict]): Top-K matching chunks with:
  - `chunk`: Original chunk text
  - `score`: Similarity score (0-1)
  - `rank`: Ranking position

**Example:**
```python
from embeddings import semantic_search, generate_embeddings
from doc_generator import load_chat_config

cfg = load_chat_config()

# Prepare chunks
chunks = [
    {"text": "Column A is transformed to Column B"},
    {"text": "Lookup joins with master data"},
    {"text": "Invalid records are filtered out"}
]

# Generate embeddings
texts = [c["text"] for c in chunks]
embeddings = generate_embeddings(texts, cfg)

# Search
query = "How are columns transformed?"
results = semantic_search(query, chunks, embeddings, top_k=2)

for r in results:
    print(f"{r['rank']}. {r['chunk']} (score: {r['score']:.2f})")
```

---

## Database Schema

### SQLite Database: dsx_graph_all.sqlite

#### Table: jobs
```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    dsx_file_id TEXT,
    job_name TEXT NOT NULL,
    job_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Table: stages
```sql
CREATE TABLE stages (
    stage_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    stage_name TEXT NOT NULL,
    stage_type TEXT,
    properties JSON,
    created_at TIMESTAMP,
    UNIQUE(job_id, stage_id)
)
```

#### Table: links
```sql
CREATE TABLE links (
    link_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    from_stage TEXT NOT NULL,
    to_stage TEXT NOT NULL,
    link_name TEXT,
    created_at TIMESTAMP
)
```

#### Table: columns
```sql
CREATE TABLE columns (
    column_id TEXT PRIMARY KEY,
    stage_id TEXT REFERENCES stages(stage_id),
    column_name TEXT NOT NULL,
    data_type TEXT,
    length INTEGER,
    is_key BOOLEAN DEFAULT 0
)
```

#### Table: parameters
```sql
CREATE TABLE parameters (
    param_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    param_name TEXT NOT NULL,
    param_type TEXT,
    default_value TEXT
)
```

#### Table: job_documentation
```sql
CREATE TABLE job_documentation (
    doc_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL UNIQUE REFERENCES jobs(job_id),
    markdown_content TEXT NOT NULL,
    model_used TEXT,
    tokens_used INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
)
```

#### Table: embeddings
```sql
CREATE TABLE embeddings (
    embedding_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    chunk_text TEXT NOT NULL,
    embedding BLOB NOT NULL,
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## REST API Query Examples

### OpenRouter Chat Completion API

**Endpoint:** `POST https://openrouter.ai/api/v1/chat/completions`

**Request:**
```json
{
  "model": "openai/gpt-oss-120b",
  "messages": [
    {
      "role": "user",
      "content": "Generate documentation for this DataStage job..."
    }
  ],
  "temperature": 0.3,
  "max_tokens": 2000
}
```

**Response:**
```json
{
  "id": "gen-...",
  "object": "text_completion",
  "created": 1234567890,
  "model": "openai/gpt-oss-120b",
  "choices": [
    {
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "# Job Documentation\n\n..."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 850,
    "total_tokens": 1000
  }
}
```

---

### OpenRouter Embeddings API

**Endpoint:** `POST https://openrouter.ai/api/v1/embeddings`

**Request:**
```json
{
  "model": "openai/text-embedding-3-small",
  "input": ["text to embed", "another text"]
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, ...],
      "index": 0
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

---

## Error Handling

### Common Error Codes

| Error | HTTP Code | Cause | Solution |
|-------|-----------|-------|----------|
| Invalid API Key | 401 | Wrong or expired key | Update `DSX_API_KEY` |
| Model Not Found | 404 | Model doesn't exist | Check `DSX_CHAT_MODEL` |
| Rate Limited | 429 | Too many requests | Increase retry delay |
| Timeout | 408/504 | Request too slow | Increase `timeout_sec` |
| Invalid Input | 400 | Malformed request | Check canonical format |

### Retry Logic

```python
# Automatic retry with exponential backoff
# Defaults: max_retries=3, retry_backoff_sec=1.0
# Backoff progression: 1s → 2s → 4s

def attempt_with_retry(fn, max_retries=3, backoff=1.0):
    for attempt in range(max_retries):
        try:
            return fn()
        except (TimeoutError, ConnectionError):
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
            else:
                raise
```

---

## Configuration Examples

### Development (Cost-Optimized)
```python
ChatConfig(
    api_key="sk-...",
    model="openai/gpt-3.5-turbo",  # Fastest, cheapest
    timeout_sec=60,                 # Quick timeouts
    max_retries=2                   # Minimal retries
)
```

### Production (Quality-Optimized)
```python
ChatConfig(
    api_key="sk-...",
    model="openai/gpt-4",           # Best quality
    timeout_sec=300,                # Allow slow requests
    max_retries=5,                  # High reliability
    retry_backoff_sec=2.0           # Longer backoff
)
```

### Balanced (Recommended)
```python
ChatConfig(
    api_key="sk-...",
    model="openai/gpt-oss-120b",   # Good balance
    timeout_sec=180,
    max_retries=3,
    retry_backoff_sec=1.0
)
```

