"""Minimal embeddings functionality for semantic search without database dependency."""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


@dataclass
class EmbeddingsConfig:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_sec: float = 60.0
    http_referer: str = ""
    x_title: str = ""


def load_embeddings_config() -> EmbeddingsConfig:
    """Load config for an OpenAI-compatible embeddings API.

    Environment variables (preferred):
    - DSX_PROVIDER (default: openrouter)
    - DSX_MODEL (default: openai/text-embedding-3-small)
    - DSX_API_KEY (required)
    - DSX_BASE_URL (default: https://openrouter.ai/api/v1)

    Note: If you're using Azure OpenAI or another compatible endpoint, set BASE_URL accordingly.
    """

    provider = os.environ.get("DSX_PROVIDER", "openrouter")
    model = os.environ.get("DSX_MODEL", "openai/text-embedding-3-small")
    api_key = os.environ.get("DSX_API_KEY", "").strip()
    # Be tolerant of values that include surrounding quotes.
    if (api_key.startswith('"') and api_key.endswith('"')) or (api_key.startswith("'") and api_key.endswith("'")):
        api_key = api_key[1:-1].strip()
    base_url = os.environ.get("DSX_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    http_referer = os.environ.get("DSX_OPENROUTER_HTTP_REFERER", "").strip()
    x_title = os.environ.get("DSX_OPENROUTER_X_TITLE", "").strip()

    if not api_key:
        raise RuntimeError(
            "Missing DSX_API_KEY. Set it in your environment before generating embeddings."
        )

    # NOTE: Chat completion models (e.g. openai/gpt-5-nano) do NOT generate embeddings.
    # For embeddings via OpenRouter, choose an embedding model (see:
    # https://openrouter.ai/models?fmt=cards&output_modalities=embeddings)
    return EmbeddingsConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        http_referer=http_referer,
        x_title=x_title,
    )


def _post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout_sec: float) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def embed_texts_openai_compatible(cfg: EmbeddingsConfig, texts: Sequence[str]) -> List[List[float]]:
    """Call OpenAI-compatible /embeddings endpoint."""

    url = f"{cfg.base_url}/embeddings"
    headers = {"Authorization": f"Bearer {cfg.api_key}"}
    # OpenRouter optional attribution headers
    if cfg.http_referer:
        headers["HTTP-Referer"] = cfg.http_referer
    if cfg.x_title:
        headers["X-Title"] = cfg.x_title

    payload = {"model": cfg.model, "input": list(texts)}
    out = _post_json(url, headers=headers, payload=payload, timeout_sec=cfg.timeout_sec)

    data = out.get("data") or []
    # Ensure returned order is by index
    data_sorted = sorted(data, key=lambda x: x.get("index", 0))
    vectors: List[List[float]] = []
    for item in data_sorted:
        vec = item.get("embedding")
        if not isinstance(vec, list):
            raise RuntimeError("Embeddings API returned unexpected payload")
        vectors.append([float(x) for x in vec])
    return vectors


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Calculate cosine similarity between two vectors without numpy."""
    if len(a) != len(b):
        raise ValueError("Vector dims mismatch")
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / ((na ** 0.5) * (nb ** 0.5))
