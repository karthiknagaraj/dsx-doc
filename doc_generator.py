from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ChatConfig:
    api_key: str
    model: str = "openai/gpt-oss-120b"  # Default model for doc generation (good balance of quality + cost)
    base_url: str = "https://openrouter.ai/api/v1"
    provider: str = "openrouter"
    http_referer: Optional[str] = None
    x_title: Optional[str] = None
    timeout_sec: int = 180
    max_retries: int = 3
    retry_backoff_sec: float = 1.0


def load_chat_config() -> ChatConfig:
    """Loads chat completion config from env.

    Primary variable: DSX_API_KEY
    """

    api_key = os.environ.get("DSX_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing API key. Set DSX_API_KEY in your .env file or environment variables." 
        )

    return ChatConfig(
        api_key=api_key,
        model=os.environ.get("DSX_CHAT_MODEL", "openai/gpt-oss-120b"),  # Override via env var if needed
        base_url=os.environ.get("DSX_CHAT_BASE_URL", "https://openrouter.ai/api/v1"),
        provider=os.environ.get("DSX_CHAT_PROVIDER", "openrouter"),
        http_referer=os.environ.get("DSX_OPENROUTER_HTTP_REFERER"),
        x_title=os.environ.get("DSX_OPENROUTER_X_TITLE"),
    )


def _request_json(
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
    *,
    timeout_sec: int,
    max_retries: int,
    retry_backoff_sec: float,
) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    last_err: Exception | None = None
    for attempt in range(max(1, int(max_retries))):
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except (TimeoutError, urllib.error.URLError) as e:
            # Transient network/timeout; retry.
            last_err = e
            if attempt + 1 >= max(1, int(max_retries)):
                break
            time.sleep(retry_backoff_sec * (2**attempt))

    raise last_err or RuntimeError("Request failed")


def _compact_canonical_for_prompt(canonical: Dict[str, Any], max_chars: int = 120_000) -> str:
    """Create a compact JSON string to keep prompts bounded.

    We include the high-signal fields but drop the huge/low-signal ones.
    """

    doc: Dict[str, Any] = {
        "dsx_file_id": canonical.get("dsx_file_id"),
        "file_name": canonical.get("file_name"),
        "export_timestamp": canonical.get("export_timestamp"),
        "jobs": [],
    }

    for job in canonical.get("jobs") or []:
        j: Dict[str, Any] = {
            "job_id": job.get("job_id"),
            "job_name": job.get("job_name"),
            "category": job.get("category"),
            "description": job.get("description"),
            "developer": job.get("developer"),
            "job_version": job.get("job_version"),
            "date_modified": job.get("date_modified"),
            "parameters": job.get("parameters") or [],
            "stages": [],
            "links": job.get("links") or [],
        }
        for stg in job.get("stages") or []:
            j["stages"].append(
                {
                    "stage_id": stg.get("stage_id"),
                    "stage_name": stg.get("stage_name"),
                    "stage_type": stg.get("stage_type"),
                    "ole_type": stg.get("ole_type"),
                    "category": stg.get("category"),
                    "description": stg.get("description"),
                }
            )
        doc["jobs"].append(j)

    s = json.dumps(doc, ensure_ascii=False)
    if len(s) <= max_chars:
        return s

    # Last resort: truncate; still valid JSON? No. So keep a clipped string.
    return s[:max_chars] + "\n...<truncated>"


def generate_job_docs(
    *,
    canonical: Dict[str, Any],
    dsx_text: str,
    cfg: ChatConfig,
) -> Tuple[str, Dict[str, Any]]:
    """Generate (markdown, meta).

    We intentionally generate Markdown only (best default for semantic chunking).
    meta includes token usage info when available.
    """

    # Limit the raw DSX snippet included.
    raw_snippet = dsx_text[:80_000]
    canonical_compact = _compact_canonical_for_prompt(canonical)

    required_headings = [
        "# ",
        "## Executive Summary",
        "## Business Context",
        "## What This Job Does",
        "## Key Parameters",
        "## Technical Debt & Modernization Opportunities",
        "## Migration Complexity",
        "## Domain Glossary",
    ]

    system_prompt = (
        "You are a technical documentation assistant helping non-technical stakeholders understand IBM DataStage ETL jobs. "
        "Your audience includes business analysts, project managers, and executives who need to assess migration readiness and business value. "
        "Write in plain English. Avoid jargon. If you must use technical terms, define them in the glossary. "
        "Do NOT invent table names, column names, business context, or specifics that aren't in the metadata. "
        "If something is unclear or missing, say 'Not available from metadata' and suggest what to check."
    )

    user_prompt = (
        "Generate a SINGLE Markdown document describing this DataStage job for a NON-TECHNICAL audience.\n\n"
        "Return a SINGLE JSON object with exactly this key: markdown.\n"
        "- markdown: string (the full Markdown document)\n\n"
        "TARGET AUDIENCE: Business analysts, project managers, executives evaluating this job for migration/modernization.\n\n"
        "CRITICAL RULES:\n"
        "1. Use THIS exact heading structure and order (headings must match exactly).\n"
        "2. Write in plain English. Assume the reader has NEVER used DataStage.\n"
        "3. Do NOT invent sources, targets, columns, or business context. Use ONLY what's in the metadata.\n"
        "4. When inferring business purpose, label your confidence level (High/Medium/Low).\n"
        "5. Focus on BUSINESS VALUE and MIGRATION READINESS, not technical implementation details.\n\n"
        "REQUIRED OUTLINE:\n"
        "------------------------------------------------------------\n"
        "# <Job Name>\n\n"
        
        "## Executive Summary\n"
        "Write 2-3 sentences answering:\n"
        "  - What does this job do? (in plain English, no jargon)\n"
        "  - Why does it exist? (business purpose)\n"
        "  - How critical is it? (based on job name, category, after-routines)\n\n"
        
        "## Business Context\n"
        "Format each field on its own line:\n\n"
        "**Business Purpose**: <1-2 sentences explaining what business process this supports>\n\n"
        "**Business Domain**: <e.g., Billing, Customer Management, Fraud Detection, Sales Analytics>\n\n"
        "**Confidence Level**: High/Medium/Low\n"
        "  - High: Job name, description, and metadata clearly indicate purpose\n"
        "  - Medium: Can infer from naming patterns but not fully documented\n"
        "  - Low: Cryptic naming, missing descriptions, unclear purpose\n\n"
        
        "## What This Job Does\n"
        "Explain in plain English what happens to the data. Structure this section as:\n\n"
        "### Data Sources\n"
        "Present as a simple table:\n"
        "| Source | Type | Purpose |\n"
        "|--------|------|----------|\n"
        "| <name or 'Not specified'> | <Database/File/API/Stream> | <What data it provides> |\n\n"
        
        "### Data Targets\n"
        "Present as a simple table:\n"
        "| Target | Type | Purpose |\n"
        "|--------|------|----------|\n"
        "| <name or 'Not specified'> | <Table/File/API> | <Where output goes and why> |\n\n"
        
        "### Key Transformations\n"
        "List ONLY the important transformations in plain English (NOT all stages).\n"
        "Focus on: joins, lookups, aggregations, filters that matter to understanding business logic.\n"
        "Skip: technical connectors, copy stages, minor formatting.\n"
        "Example: 'Joins customer data with transaction history to calculate billing totals.'\n"
        "If no significant transformations: 'Simple data movement with minimal transformation.'\n\n"
        
        "### Data Flow\n"
        "Show the high-level flow using simple arrows:\n"
        "Example:\n"
        "```\n"
        "Source DB → Lookup Customer Info → Join with Transactions → Aggregate Totals → Target Table\n"
        "```\n"
        "Keep it simple. Don't list every stage.\n\n"
        
        "## Key Parameters\n"
        "ONLY include parameters that a non-technical person would care about.\n"
        "Focus on: file paths, date ranges, environment names, batch sizes, processing modes.\n"
        "SKIP: database passwords, technical connection strings, internal flags.\n"
        "Present as a table:\n"
        "| Parameter | What It Controls | Example Impact |\n"
        "|-----------|------------------|----------------|\n"
        "| FilePath | Location of input files | Wrong path = job fails to find data |\n"
        "| HistoricalLoadFlag | Whether to load all history or just recent changes | Affects runtime and data volume |\n"
        "If no relevant parameters: 'No user-configurable parameters detected.'\n\n"
        
        "## Technical Debt & Modernization Opportunities\n"
        "Identify issues and improvement opportunities:\n\n"
        "**Red Flags Detected:**\n"
        "- Missing or poor documentation (e.g., stage descriptions are '<none>')\n"
        "- Hard-coded values instead of parameters\n"
        "- High complexity (many stages/joins)\n"
        "- Deprecated stage types (if detectable)\n"
        "- No cleanup/archival routines\n"
        "If none detected: 'No major red flags detected.'\n\n"
        
        "**Modernization Suggestions:**\n"
        "- What could be improved? (e.g., 'Add parameter for date range instead of hard-coded values')\n"
        "- Are there modern alternatives? (e.g., 'Could be replaced with cloud-native ETL tool')\n"
        "- Documentation gaps to fill\n\n"
        
        "## Migration Complexity\n"
        "Provide a DATA-DRIVEN complexity assessment:\n\n"
        "**Quantitative Metrics:**\n"
        "- Number of stages: <count>\n"
        "- Number of sources: <count>\n"
        "- Number of targets: <count>\n"
        "- Number of joins/lookups: <count>\n"
        "- Number of transformations: <count>\n\n"
        
        "**Complexity Score**: Low / Medium / High\n"
        "- Low: < 5 stages, simple extract-load, well-documented\n"
        "- Medium: 5-15 stages, some joins/transformations, partial documentation\n"
        "- High: > 15 stages, complex logic, poor documentation, many dependencies\n\n"
        
        "**Migration Effort Estimate**: Simple / Moderate / Complex\n"
        "- Simple: Could be automated or replaced with modern tool easily\n"
        "- Moderate: Requires some redesign but logic is clear\n"
        "- Complex: Needs deep analysis, refactoring, and SME involvement\n\n"
        
        "## Domain Glossary\n"
        "List only the UNIQUE technical or domain terms that appear in THIS specific job and need explanation.\n\n"
        "IMPORTANT GUIDELINES:\n"
        "- DO NOT include generic DataStage terms (stage, link, transformer, lookup) - assume readers have basic DataStage knowledge\n"
        "- ONLY include terms if they appear in this job's metadata (job name, stage names, parameters, descriptions)\n"
        "- DO NOT guess or infer meanings of abbreviations/acronyms - only define if explicitly stated in metadata\n"
        "- If a term appears but its meaning is unclear from metadata, write: '<Term>: Not defined in metadata - requires SME clarification'\n"
        "- If there are NO unique terms to define, write: 'No job-specific terms require definition.'\n\n"
        
        "**Job-Specific Terms:**\n"
        "- <List only terms that are unique to this job and actually appear in the metadata>\n"
        "- <Only provide definitions if they are clear from the metadata or stage descriptions>\n"
        "------------------------------------------------------------\n\n"
        
        "DATA (canonical JSON, compact):\n"
        f"{canonical_compact}\n\n"
        "RAW DSX SNIPPET (for extracting FullDescription, developer notes, comments):\n"
        f"{raw_snippet}\n\n"
        
        "REMEMBER: Write for someone who has NEVER seen DataStage. Explain everything in business terms."
    )

    url = cfg.base_url.rstrip("/") + "/chat/completions"
    payload: Dict[str, Any] = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    if cfg.http_referer:
        headers["HTTP-Referer"] = cfg.http_referer
    if cfg.x_title:
        headers["X-Title"] = cfg.x_title

    data = _request_json(
        url,
        payload,
        headers,
        timeout_sec=cfg.timeout_sec,
        max_retries=cfg.max_retries,
        retry_backoff_sec=cfg.retry_backoff_sec,
    )

    content = data["choices"][0]["message"]["content"]
    out = json.loads(content)
    markdown = out.get("markdown") or ""

    # Guardrail: ensure the most important headings exist so downstream chunking/search is consistent.
    # We don't try to heavily rewrite the model output here; we just append missing sections.
    if markdown:
        missing: List[str] = []
        for h in required_headings[1:]:
            if h not in markdown:
                missing.append(h)
        if missing:
            markdown = markdown.rstrip() + "\n\n" + "\n\n".join(
                [
                    f"{h}\nNot available." if h.startswith("##") else f"{h}Not available."
                    for h in missing
                ]
            )

    meta = {
        "provider": cfg.provider,
        "model": cfg.model,
        "usage": data.get("usage") or {},
    }

    return markdown, meta


def generate_answer_with_citations(
    *,
    question: str,
    chunks: List[Dict[str, Any]],
    cfg: ChatConfig,
    max_chunk_chars: int = 2_000,
) -> Tuple[str, Dict[str, Any]]:
    """Answer a question using only provided chunks; include citations.

    Returns (answer_markdown, meta).
    """

    context_blocks: List[str] = []
    for i, ch in enumerate(chunks, start=1):
        title = ch.get("title") or ch.get("chunk_type") or ch.get("chunk_id")
        dsx_file_id = ch.get("dsx_file_id") or ""
        job_id = ch.get("job_id") or ""
        chunk_type = ch.get("chunk_type") or ""
        content = (ch.get("content") or "")[:max_chunk_chars]

        context_blocks.append(
            "\n".join(
                [
                    f"[{i}] title: {title}",
                    f"    dsx_file_id: {dsx_file_id}",
                    f"    job_id: {job_id}",
                    f"    chunk_type: {chunk_type}",
                    "    content:",
                    content,
                ]
            )
        )

    system_prompt = (
        "Answer the user's question using ONLY the provided context snippets. "
        "If the answer is not present, say what is missing and suggest what to check. "
        "Write in Markdown. When stating a specific fact, include citations like [1] or [2]. "
        "Use bullet points to make your answer clear and easy to scan."
    )

    user_prompt = (
        f"Question: {question}\n\n"
        "Context snippets:\n"
        + "\n\n".join(context_blocks)
        + "\n\n"
        "Write a concise answer using bullet points for clarity. "
        "When you state a fact, include at least one citation."
    )

    url = cfg.base_url.rstrip("/") + "/chat/completions"
    payload: Dict[str, Any] = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    if cfg.http_referer:
        headers["HTTP-Referer"] = cfg.http_referer
    if cfg.x_title:
        headers["X-Title"] = cfg.x_title

    data = _request_json(
        url,
        payload,
        headers,
        timeout_sec=cfg.timeout_sec,
        max_retries=cfg.max_retries,
        retry_backoff_sec=cfg.retry_backoff_sec,
    )

    answer = data["choices"][0]["message"]["content"]
    meta = {
        "provider": cfg.provider,
        "model": cfg.model,
        "usage": data.get("usage") or {},
    }
    return answer, meta
