from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

import dsx_to_canonical
from doc_generator import ChatConfig, generate_job_docs
from utils import safe_filename, sha256_hex


# Optional: load environment variables from a local .env file.
# This mirrors semantic_search.py behavior but keeps the dependency optional.
try:
    from dotenv import find_dotenv  # type: ignore
    from dotenv import load_dotenv  # type: ignore

    _dotenv_path = find_dotenv(usecwd=True)
    load_dotenv(_dotenv_path, override=True)
except Exception:
    pass


def _write_job_docs_to_disk(
    *,
    out_dir: Path,
    file_name: str,
    job_name: str,
    markdown: str,
) -> Path:
    """Save Markdown documentation to disk."""
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_file = safe_filename(Path(file_name).stem)
    safe_job = safe_filename(job_name or "job")

    md_path = out_dir / f"{safe_file}__{safe_job}.md"

    md_path.write_text(markdown, encoding="utf-8")

    return md_path


def render_docs_tab() -> None:
    st.header("📝 Documentation")
    st.caption(
        "Generate human-friendly job documentation (Markdown) from DSX files. "
        "No database required - just upload DSX files and download generated docs."
    )

    st.subheader("1) Input")
    uploads = st.file_uploader(
        "Upload one or more .dsx files",
        type=["dsx"],
        accept_multiple_files=True,
    )

    st.subheader("2) Chat model config")
    # Use DSX_API_KEY as the primary API key variable
    api_key_default = os.environ.get("DSX_API_KEY", "")
    model_default = os.environ.get("DSX_CHAT_MODEL", "openai/gpt-oss-120b")
    base_url_default = os.environ.get("DSX_CHAT_BASE_URL", "https://openrouter.ai/api/v1")

    c1, c2 = st.columns([2, 2])
    with c1:
        st.write(
            {
                "Key detected": bool(api_key_default),
                "Source": "DSX_API_KEY" if api_key_default else "(none)",
            }
        )
    with c2:
        model = st.text_input("Chat model", value=model_default)

    base_url = st.text_input("Base URL", value=base_url_default)

    # Keep chat reliability settings internal (env-controlled) to avoid users
    # accidentally breaking the experience.
    timeout_sec = int(os.environ.get("DSX_CHAT_TIMEOUT_SEC", "180"))
    max_retries = int(os.environ.get("DSX_CHAT_MAX_RETRIES", "3"))
    retry_backoff = float(os.environ.get("DSX_CHAT_RETRY_BACKOFF_SEC", "1.0"))

    st.subheader("3) Storage")
    # Default to Desktop as a user-friendly placeholder location on Windows.
    out_dir = Path(st.text_input("Docs output folder", value=r"C:\Users\anindita.bornomala\Desktop\dsx_docs")) 
    
    # Checksum file for change detection (stored alongside docs)
    checksum_file = out_dir / ".dsx_checksums.json"

    st.subheader("4) Options")
    
    skip_unchanged = st.toggle(
        "Skip doc generation for unchanged files",
        value=True,
        help="Compares file checksums to skip regenerating docs for files that haven't changed.",
    )

    st.markdown("**Batch processing**")
    st.caption(
        "For large batches, keep concurrency low to avoid rate limits/timeouts. "
        "A value of 1 is safest; 2–3 can speed up runs if your provider allows it."
    )
    max_workers = st.number_input(
        "Max concurrent doc generations",
        min_value=1,
        max_value=10,
        value=int(os.environ.get("DSX_DOCS_MAX_WORKERS", "1")),
        step=1,
    )

    # NOTE: Database and storage toggles removed - now purely file-based workflow

    # NOTE: Database removed - now purely file-based workflow

    st.markdown("---")
    run = st.button("Generate documentation", type="primary", disabled=not uploads)
    if not run:
        return

    api_key = api_key_default
    if not api_key:
        st.error(
            "Missing API key. Set DSX_API_KEY in your .env file."
        )
        return

    # Load existing checksums for change detection
    checksums: Dict[str, str] = {}
    if skip_unchanged and checksum_file.exists():
        try:
            checksums = json.loads(checksum_file.read_text(encoding="utf-8"))
        except Exception:
            checksums = {}

    results: List[Dict[str, Any]] = []

    progress = st.progress(0)

    total = len(uploads or [])
    prep = st.empty()
    gen = st.empty()

    # Phase 1: parse + ingest + skip decisions (sequential)
    tasks: List[Dict[str, Any]] = []
    for i, up in enumerate(uploads or []):
            prep.info(f"Preparing: {i + 1} of {total} …")
            t0 = time.time()

            dsx_name = safe_filename(getattr(up, "name", "uploaded.dsx"))
            dsx_text = up.getvalue().decode("utf-8", errors="replace")

            try:
                canonical = dsx_to_canonical.build_canonical_from_text(dsx_text, file_name=dsx_name)
            except Exception as e:
                results.append(
                    {
                        "file_name": dsx_name,
                        "status": "FAIL",
                        "error": f"Parse failed: {type(e).__name__}: {e}",
                        "seconds": round(time.time() - t0, 2),
                    }
                )
                progress.progress((i + 1) / max(1, total))
                continue

            # Extract job info
            job_id: Optional[str] = None
            job_name: str = ""
            jobs = canonical.get("jobs") or []
            if jobs:
                job_id = jobs[0].get("job_id")
                job_name = jobs[0].get("job_name") or dsx_name
            else:
                job_name = dsx_name

            # File-based change detection: compare checksums
            doc_status = "new"  # Default: new file
            current_checksum = canonical.get("file_checksum")
            dsx_file_id = canonical.get("dsx_file_id")
            
            if skip_unchanged and dsx_file_id in checksums:
                stored_checksum = checksums.get(dsx_file_id)
                if current_checksum == stored_checksum:
                    # Checksum matches - file unchanged, skip regeneration
                    doc_status = "unchanged"
                    results.append(
                        {
                            "file_name": canonical.get("file_name"),
                            "dsx_file_id": dsx_file_id,
                            "job_name": job_name,
                            "status": "SKIP",
                            "detail": "File unchanged (checksum match) - docs up to date",
                            "markdown": "",
                            "seconds": round(time.time() - t0, 2),
                        }
                    )
                    progress.progress((i + 1) / max(1, total))
                    continue
                else:
                    # Checksum changed - file updated
                    doc_status = "updated"
            
            # Update checksum for this file
            if current_checksum and dsx_file_id:
                checksums[dsx_file_id] = current_checksum

            file_name = canonical.get("file_name") or dsx_name
            cfg = ChatConfig(
                api_key=api_key,
                model=model,
                base_url=base_url,
                provider=os.environ.get("DSX_CHAT_PROVIDER", "openrouter"),
                http_referer=os.environ.get("DSX_OPENROUTER_HTTP_REFERER"),
                x_title=os.environ.get("DSX_OPENROUTER_X_TITLE"),
                timeout_sec=int(timeout_sec),
                max_retries=int(max_retries),
                retry_backoff_sec=float(retry_backoff),
            )

            tasks.append(
                {
                    "t0": t0,
                    "file_name": file_name,
                    "dsx_file_id": canonical.get("dsx_file_id"),
                    "job_id": job_id,
                    "job_name": job_name,
                    "canonical": canonical,
                    "dsx_text": dsx_text,
                    "cfg": cfg,
                    "doc_status": doc_status,  # Track if new/updated
                }
            )
            progress.progress((i + 1) / max(1, total))

    # Phase 2: generation (potentially concurrent)
    prep.empty()
    if tasks:
        gen.info(f"Generating: 0 of {len(tasks)} …")

    def _generate_one(task: Dict[str, Any]) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
        md, meta = generate_job_docs(
            canonical=task["canonical"],
            dsx_text=task["dsx_text"],
            cfg=task["cfg"],
        )
        return task, md, meta

    done = 0
    if tasks:
        with ThreadPoolExecutor(max_workers=int(max_workers)) as ex:
            fut_to_task = {ex.submit(_generate_one, t): t for t in tasks}
            for fut in as_completed(fut_to_task):
                task = fut_to_task[fut]
                try:
                    task, md, meta = fut.result()
                    
                    # Always save to disk
                    md_path: Optional[str] = None
                    p_md = _write_job_docs_to_disk(
                        out_dir=out_dir,
                        file_name=task["file_name"],
                        job_name=task["job_name"],
                        markdown=md,
                    )
                    md_path = str(p_md)

                    results.append(
                        {
                            "file_name": task["file_name"],
                            "dsx_file_id": task.get("dsx_file_id"),
                            "job_name": task["job_name"],
                            "status": "OK",
                            "doc_status": task.get("doc_status", "new"),  # Show if new/updated
                            "saved_md": md_path or "",
                            "markdown": md,
                            "model": meta.get("model"),
                            "tokens": (meta.get("usage") or {}).get("total_tokens", ""),
                            "seconds": round(time.time() - float(task["t0"]), 2),
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "file_name": task.get("file_name"),
                            "dsx_file_id": task.get("dsx_file_id"),
                            "job_name": task.get("job_name"),
                            "status": "FAIL",
                            "error": f"Doc generation failed: {type(e).__name__}: {e}",
                            "seconds": round(time.time() - float(task.get("t0", time.time())), 2),
                        }
                    )
                finally:
                    done += 1
                    gen.info(f"Generating: {done} of {len(tasks)} …")
                    progress.progress(min(1.0, done / max(1, len(tasks))))

    gen.empty()
    
    # Save updated checksums to file
    if checksums:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            checksum_file.write_text(json.dumps(checksums, indent=2), encoding="utf-8")
        except Exception as e:
            st.warning(f"Could not save checksums: {e}")

        # Summary statistics
        ok = sum(1 for r in results if r.get("status") == "OK")
        skipped = sum(1 for r in results if r.get("status") == "SKIP")
        fail = len(results) - ok - skipped
        
        # Count new vs updated docs
        new_docs = sum(1 for r in results if r.get("status") == "OK" and r.get("doc_status") == "new")
        updated_docs = sum(1 for r in results if r.get("status") == "OK" and r.get("doc_status") == "updated")
        
        if ok:
            status_parts = []
            if new_docs:
                status_parts.append(f"{new_docs} new")
            if updated_docs:
                status_parts.append(f"{updated_docs} updated")
            if skipped:
                status_parts.append(f"{skipped} skipped (unchanged)")
            if fail:
                status_parts.append(f"{fail} failed")
            
            status_msg = "Documentation done: " + ", ".join(status_parts)
            st.success(status_msg)
        else:
            st.error(f"Documentation done: {ok} OK, {skipped} skipped, {fail} failed")

        # Display results with visual indicators
        # Add emoji indicators for better readability
        display_results = []
        for r in results:
            display_r = r.copy()
            if r.get("status") == "OK":
                doc_status = r.get("doc_status", "new")
                if doc_status == "new":
                    display_r["doc_status"] = "🆕 New"
                elif doc_status == "updated":
                    display_r["doc_status"] = "🔄 Updated"
            elif r.get("status") == "SKIP":
                display_r["doc_status"] = "✓ Unchanged"
            display_results.append(display_r)
        
        st.dataframe(display_results, width="stretch")

        st.markdown("---")
        st.subheader("Preview generated docs")
        st.caption("Shows the Markdown documentation for each job produced during this run.")

        for r in results:
            status = r.get("status")
            if status not in {"OK", "SKIP"}:
                continue

            job_name = r.get("job_name") or "(job)"
            file_name = r.get("file_name") or "(dsx)"
            dsx_file_id = r.get("dsx_file_id") or ""

            md = (r.get("markdown") or "").strip()

            label = f"{job_name}  —  {status}"
            with st.expander(label, expanded=False):
                st.caption(f"DSX: `{file_name}`  ·  dsx_file_id: `{dsx_file_id}`")
                if not md:
                    st.info("No Markdown available to preview.")
                else:
                    st.markdown(md)

        st.caption(
            "Next: Upload generated .md files to 🔎 Semantic Search to search across all documentation."
        )

