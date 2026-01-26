#!/usr/bin/env python3
"""Load knowledge base files with rate-limit-friendly delays.

This script loads knowledge base files one at a time with delays
to avoid hitting Voyage AI's rate limits (3 RPM on free tier).

Usage:
    python scripts/load_knowledge_with_delay.py

Options:
    --delay SECONDS    Delay between files (default: 25 seconds)
    --skip-loaded      Skip files that are already in the database
    --dry-run          Show what would be loaded without actually loading
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from content_assistant.config import get_config, clear_config_cache
from content_assistant.rag.embeddings import clear_client_cache
from content_assistant.rag.vector_store import get_all_sources, get_chunk_count
from content_assistant.rag.knowledge_base import load_file_to_knowledge_base, KnowledgeBaseError


def get_knowledge_files() -> list[Path]:
    """Get all knowledge base files to load."""
    config = get_config()
    knowledge_dir = Path(config.knowledge_dir)

    files = []
    for ext in [".md", ".txt"]:
        files.extend(knowledge_dir.rglob(f"*{ext}"))

    return sorted(files)


def get_loaded_sources() -> set[str]:
    """Get sources already loaded in the database."""
    return set(get_all_sources())


def load_with_delay(
    delay_seconds: int = 25,
    skip_loaded: bool = True,
    dry_run: bool = False,
) -> dict:
    """Load knowledge base files with delays between each file.

    Args:
        delay_seconds: Seconds to wait between files (default 25 for 3 RPM limit)
        skip_loaded: Skip files already in database
        dry_run: Just show what would be loaded

    Returns:
        dict with results
    """
    # Clear caches to ensure fresh config
    clear_config_cache()
    clear_client_cache()

    files = get_knowledge_files()
    loaded_sources = get_loaded_sources() if skip_loaded else set()

    print("=" * 60)
    print("TheLifeCo Knowledge Base Loader (Rate-Limited)")
    print("=" * 60)
    print(f"Knowledge directory: {get_config().knowledge_dir}")
    print(f"Total files found: {len(files)}")
    print(f"Already loaded: {len(loaded_sources)}")
    print(f"Delay between files: {delay_seconds} seconds")
    print(f"Voyage model: {get_config().voyage_model}")
    print(f"Embedding dimension: {get_config().embedding_dimension}")
    print("=" * 60)

    if dry_run:
        print("\n[DRY RUN - No files will be loaded]\n")

    results = {
        "files_processed": 0,
        "chunks_created": 0,
        "skipped": 0,
        "errors": [],
    }

    files_to_load = []
    for f in files:
        source_name = f.name
        if skip_loaded and source_name in loaded_sources:
            print(f"  [SKIP] {source_name} (already loaded)")
            results["skipped"] += 1
        else:
            files_to_load.append(f)

    if not files_to_load:
        print("\nNo files to load!")
        return results

    print(f"\nFiles to load: {len(files_to_load)}")
    estimated_time = len(files_to_load) * delay_seconds
    print(f"Estimated time: {estimated_time // 60} min {estimated_time % 60} sec")
    print("-" * 60)

    if dry_run:
        for f in files_to_load:
            print(f"  [WOULD LOAD] {f.name}")
        return results

    for i, file_path in enumerate(files_to_load, 1):
        print(f"\n[{i}/{len(files_to_load)}] Loading {file_path.name}...")

        try:
            result = load_file_to_knowledge_base(
                file_path,
                replace_existing=True,
            )
            results["files_processed"] += 1
            results["chunks_created"] += result.get("chunks_created", 0)
            print(f"  ✓ Created {result.get('chunks_created', 0)} chunks")

        except KnowledgeBaseError as e:
            error_msg = str(e)
            results["errors"].append(f"{file_path.name}: {error_msg}")
            print(f"  ✗ Error: {error_msg[:100]}...")

            # Check if it's a rate limit error
            if "rate limit" in error_msg.lower() or "RPM" in error_msg:
                print(f"  → Rate limited! Waiting extra 30 seconds...")
                time.sleep(30)

        # Wait before next file (except for the last one)
        if i < len(files_to_load):
            print(f"  Waiting {delay_seconds}s before next file...")
            time.sleep(delay_seconds)

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {results['files_processed']}")
    print(f"Chunks created: {results['chunks_created']}")
    print(f"Files skipped: {results['skipped']}")
    print(f"Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"]:
            print(f"  - {err[:80]}...")

    # Show total chunks in database
    total_chunks = get_chunk_count()
    total_sources = len(get_all_sources())
    print(f"\nDatabase status:")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Total sources: {total_sources}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Load knowledge base files with rate-limit-friendly delays"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=25,
        help="Delay in seconds between files (default: 25)",
    )
    parser.add_argument(
        "--skip-loaded",
        action="store_true",
        default=True,
        help="Skip files already in database (default: True)",
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Don't skip already loaded files (reload all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be loaded without loading",
    )

    args = parser.parse_args()

    skip_loaded = not args.no_skip

    try:
        load_with_delay(
            delay_seconds=args.delay,
            skip_loaded=skip_loaded,
            dry_run=args.dry_run,
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
