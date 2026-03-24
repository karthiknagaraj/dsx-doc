"""Pytest-style checks for Markdown documentation format.

These tests do NOT call the network. They monkeypatch the internal request
helper in `doc_generator` to return a fake model response.

Note: pytest is not a runtime dependency of the Streamlit app. Keep this file
only if you want regression checks.
"""

from __future__ import annotations

from doc_generator import ChatConfig, generate_job_docs


def _extract_section(md: str, heading: str) -> str:
    start = md.find(heading)
    if start < 0:
        return ""
    start = md.find("\n", start)
    if start < 0:
        return ""
    start += 1
    next_h2 = md.find("\n## ", start)
    if next_h2 < 0:
        return md[start:].strip()
    return md[start:next_h2].strip()


def _has_markdown_table(section_text: str) -> bool:
    lines = [ln.strip() for ln in section_text.splitlines() if ln.strip()]
    has_pipe_row = any(ln.startswith("|") and ln.endswith("|") for ln in lines)
    has_sep_row = any("|" in ln and "---" in ln for ln in lines)
    return has_pipe_row and has_sep_row


def _has_bullets(section_text: str) -> bool:
    for ln in section_text.splitlines():
        s = ln.lstrip()
        if s.startswith("-") or s.startswith("*"):
            return True
    return False


def test_doc_format_contract(monkeypatch) -> None:
    import json
    import doc_generator as dg

    def fake_request_json(url, payload, headers, *, timeout_sec, max_retries, retry_backoff_sec):
        markdown = """# Sample Job (DSX file: sample.dsx)

## Overview
A short overview.

## Inputs (Sources)
| Source | Type | Notes |
|---|---|---|
| Not available | Not available | Not available |

## Outputs (Targets)
| Target | Type | Notes |
|---|---|---|
| Not available | Not available | Not available |

## Data Flow
SourceStage1 -> Transformer1 -> TargetStage1

## Data lineage summary
A short paragraph.

## Parameters
No parameters found.

## Glossary
Stage: A processing step.
"""
        return {
            "choices": [{"message": {"content": json.dumps({"markdown": markdown})}}],
            "usage": {"total_tokens": 123},
        }

    monkeypatch.setattr(dg, "_request_json", fake_request_json)

    canonical = {
        "dsx_file_id": "abc123",
        "file_name": "sample.dsx",
        "jobs": [
            {
                "job_id": "job1",
                "job_name": "Sample Job",
                "stages": [],
                "links": [],
                "parameters": [],
            }
        ],
    }

    md, meta = generate_job_docs(canonical=canonical, dsx_text="", cfg=ChatConfig(api_key="x"))
    assert isinstance(meta, dict)

    required = [
        "## Overview",
        "## Inputs (Sources)",
        "## Outputs (Targets)",
        "## Data Flow",
        "## Data lineage summary",
        "## Parameters",
        "## Glossary",
    ]
    for h in required:
        assert h in md

    inputs = _extract_section(md, "## Inputs (Sources)")
    outputs = _extract_section(md, "## Outputs (Targets)")
    data_flow = _extract_section(md, "## Data Flow")
    lineage = _extract_section(md, "## Data lineage summary")

    assert _has_markdown_table(inputs)
    assert _has_markdown_table(outputs)
    assert not _has_bullets(data_flow)
    assert not _has_bullets(lineage)
