#!/usr/bin/env python3
"""
DSX Documentation Generator - CI/CD Plugin

Command-line tool for generating human-readable documentation from DataStage (.dsx) files.
Designed for integration into CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI, etc.)

Features:
- Simple CLI interface
- Exit codes for pipeline integration (0=success, non-zero=failure)
- JSON output for machine parsing
- Batch processing support
- Change detection (skip unchanged files)
- Configurable via environment variables or CLI flags
- No UI/GUI dependencies

Usage Examples:

    # Single file
    python dsx_docs_cli.py --input job.dsx --output ./docs/

    # Batch processing (entire directory)
    python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --workers 4

    # With explicit config
    python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ \
        --api-key "your-key" --model "openai/gpt-4" --skip-unchanged

    # CI/CD mode (JSON output, exit codes)
    python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ \
        --json-output results.json --fail-on-error

Environment Variables:
    DSX_API_KEY              - API key for LLM provider (required if not via --api-key)
    DSX_CHAT_MODEL           - Model to use (default: openai/gpt-oss-120b)
    DSX_CHAT_BASE_URL        - API base URL (default: https://openrouter.ai/api/v1)
    DSX_CHAT_PROVIDER        - Provider name (default: openrouter)
    DSX_DOCS_MAX_WORKERS     - Concurrent workers (default: 1)
    DSX_CHAT_TIMEOUT_SEC     - API timeout (default: 180)
    DSX_CHAT_MAX_RETRIES     - Max retries on failure (default: 3)

Exit Codes:
    0  - Success (all docs generated)
    1  - Partial failure (some docs generated, some failed)
    2  - Total failure (no docs generated)
    3  - Configuration error (missing API key, invalid paths, etc.)
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import existing modules
import dsx_to_canonical
from doc_generator import ChatConfig, generate_job_docs
from utils import safe_filename, sha256_hex


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    import logging
    
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def save_markdown(output_dir: Path, dsx_filename: str, job_name: str, markdown: str) -> Path:
    """Save generated documentation to a markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_file = safe_filename(Path(dsx_filename).stem)
    safe_job = safe_filename(job_name or "job")
    
    md_path = output_dir / f"{safe_file}__{safe_job}.md"
    md_path.write_text(markdown, encoding="utf-8")
    
    return md_path


def load_checksums(checksum_file: Path) -> Dict[str, str]:
    """Load checksums from JSON file."""
    if not checksum_file.exists():
        return {}
    
    try:
        return json.loads(checksum_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_checksums(checksum_file: Path, checksums: Dict[str, str]):
    """Save checksums to JSON file."""
    try:
        checksum_file.parent.mkdir(parents=True, exist_ok=True)
        checksum_file.write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not save checksums: {e}", file=sys.stderr)


def process_single_file(
    dsx_path: Path,
    output_dir: Path,
    cfg: ChatConfig,
    checksums: Dict[str, str],
    skip_unchanged: bool,
    logger
) -> Dict[str, Any]:
    """Process a single DSX file and generate documentation."""
    
    result = {
        "file": str(dsx_path),
        "status": "unknown",
        "output": None,
        "error": None,
        "duration_sec": 0,
        "tokens": 0,
    }
    
    start_time = time.time()
    
    try:
        # Read DSX file
        logger.info(f"Processing: {dsx_path.name}")
        dsx_text = dsx_path.read_text(encoding="utf-8", errors="replace")
        
        # Parse to canonical format
        canonical = dsx_to_canonical.build_canonical_from_text(
            dsx_text, 
            file_name=dsx_path.name
        )
        
        # Extract job info
        jobs = canonical.get("jobs") or []
        job_name = jobs[0].get("job_name") if jobs else dsx_path.stem
        
        # Check if file changed (skip if unchanged)
        current_checksum = canonical.get("file_checksum")
        dsx_file_id = canonical.get("dsx_file_id")
        
        if skip_unchanged and dsx_file_id in checksums:
            stored_checksum = checksums.get(dsx_file_id)
            if current_checksum == stored_checksum:
                result["status"] = "skipped"
                result["duration_sec"] = round(time.time() - start_time, 2)
                logger.info(f"  ✓ Skipped (unchanged): {dsx_path.name}")
                return result
        
        # Generate documentation
        logger.info(f"  → Generating docs for: {job_name}")
        markdown, meta = generate_job_docs(
            canonical=canonical,
            dsx_text=dsx_text,
            cfg=cfg,
        )
        
        # Save to file
        output_path = save_markdown(output_dir, dsx_path.name, job_name, markdown)
        
        # Update checksum
        if current_checksum and dsx_file_id:
            checksums[dsx_file_id] = current_checksum
        
        result["status"] = "success"
        result["output"] = str(output_path)
        result["tokens"] = (meta.get("usage") or {}).get("total_tokens", 0)
        result["duration_sec"] = round(time.time() - start_time, 2)
        
        logger.info(f"  ✓ Success: {output_path.name} ({result['tokens']} tokens, {result['duration_sec']}s)")
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["duration_sec"] = round(time.time() - start_time, 2)
        logger.error(f"  ✗ Failed: {dsx_path.name} - {result['error']}")
    
    return result


def find_dsx_files(input_path: Path, recursive: bool = True) -> List[Path]:
    """Find all .dsx files in the input path."""
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() == ".dsx" else []
    
    if recursive:
        return list(input_path.rglob("*.dsx"))
    else:
        return list(input_path.glob("*.dsx"))


def main():
    parser = argparse.ArgumentParser(
        description="Generate human-readable documentation from DataStage (.dsx) files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Input/Output
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input .dsx file or directory containing .dsx files"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory for generated markdown files"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=True,
        help="Recursively search for .dsx files in subdirectories (default: true)"
    )
    
    # API Configuration
    parser.add_argument(
        "--api-key",
        help="API key for LLM provider (or set DSX_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("DSX_CHAT_MODEL", "openai/gpt-oss-120b"),
        help="Model to use (default: openai/gpt-oss-120b)"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("DSX_CHAT_BASE_URL", "https://openrouter.ai/api/v1"),
        help="API base URL (default: https://openrouter.ai/api/v1)"
    )
    parser.add_argument(
        "--provider",
        default=os.environ.get("DSX_CHAT_PROVIDER", "openrouter"),
        help="Provider name (default: openrouter)"
    )
    
    # Processing Options
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=int(os.environ.get("DSX_DOCS_MAX_WORKERS", "1")),
        help="Number of concurrent workers (default: 1)"
    )
    parser.add_argument(
        "--skip-unchanged",
        action="store_true",
        default=True,
        help="Skip files that haven't changed (based on checksum, default: true)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if files haven't changed"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("DSX_CHAT_TIMEOUT_SEC", "180")),
        help="API timeout in seconds (default: 180)"
    )
    
    # CI/CD Options
    parser.add_argument(
        "--json-output",
        help="Save results as JSON to this file (for CI/CD parsing)"
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with non-zero code if ANY file fails"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 3
    
    output_dir = Path(args.output)
    
    # Get API key
    api_key = args.api_key or os.environ.get("DSX_API_KEY")
    if not api_key:
        logger.error("Missing API key. Provide via --api-key or DSX_API_KEY environment variable")
        return 3
    
    # Find DSX files
    dsx_files = find_dsx_files(input_path, args.recursive)
    if not dsx_files:
        logger.warning(f"No .dsx files found in: {input_path}")
        return 0
    
    logger.info(f"Found {len(dsx_files)} .dsx file(s)")
    
    # Load checksums (for skip-unchanged)
    checksum_file = output_dir / ".dsx_checksums.json"
    checksums = load_checksums(checksum_file) if not args.force else {}
    skip_unchanged = args.skip_unchanged and not args.force
    
    # Create chat config
    cfg = ChatConfig(
        api_key=api_key,
        model=args.model,
        base_url=args.base_url,
        provider=args.provider,
        timeout_sec=args.timeout,
        max_retries=int(os.environ.get("DSX_CHAT_MAX_RETRIES", "3")),
        retry_backoff_sec=float(os.environ.get("DSX_CHAT_RETRY_BACKOFF_SEC", "1.0")),
    )
    
    # Process files
    results = []
    start_time = time.time()
    
    if args.workers == 1:
        # Sequential processing
        for dsx_file in dsx_files:
            result = process_single_file(
                dsx_file, output_dir, cfg, checksums, skip_unchanged, logger
            )
            results.append(result)
    else:
        # Concurrent processing
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(
                    process_single_file,
                    dsx_file, output_dir, cfg, checksums, skip_unchanged, logger
                ): dsx_file
                for dsx_file in dsx_files
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
    
    # Save updated checksums
    if checksums:
        save_checksums(checksum_file, checksums)
    
    # Summary
    total_duration = round(time.time() - start_time, 2)
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")
    total_tokens = sum(r.get("tokens", 0) for r in results)
    
    summary = {
        "total_files": len(dsx_files),
        "success": success_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "total_tokens": total_tokens,
        "total_duration_sec": total_duration,
        "results": results,
    }
    
    # Print summary
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files:     {summary['total_files']}")
    logger.info(f"Success:         {success_count}")
    logger.info(f"Failed:          {failed_count}")
    logger.info(f"Skipped:         {skipped_count}")
    logger.info(f"Total tokens:    {total_tokens}")
    logger.info(f"Total duration:  {total_duration}s")
    logger.info("=" * 60)
    
    # Save JSON output if requested
    if args.json_output:
        json_path = Path(args.json_output)
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        logger.info(f"Results saved to: {json_path}")
    
    # Determine exit code
    if failed_count == 0:
        return 0  # All success
    elif success_count > 0:
        # Partial success - exit code depends on --fail-on-error flag
        return 1 if args.fail_on_error else 0
    else:
        return 2  # Total failure


if __name__ == "__main__":
    sys.exit(main())
