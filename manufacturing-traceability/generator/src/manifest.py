"""Deterministic manifest generator and SHA-256 checksum calculator."""
import hashlib
import json
import os
import re
from typing import Dict, Any, Optional


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def count_lines(filepath: str) -> int:
    """Counts non-empty lines in a file (diagnostic metadata)."""
    count = 0
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def determine_logical_row_count(filepath: str, table_counts: Optional[Dict[str, int]] = None) -> int:
    """Determines exact logical data record count (excluding headers/structural lines)."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return 0

    basename = os.path.basename(filepath)
    table_name = os.path.splitext(basename)[0]

    if table_counts and table_name in table_counts:
        return table_counts[table_name]

    if filepath.endswith(".json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return len(data)
                elif isinstance(data, dict):
                    return len(data)
        except Exception:
            return 0

    if filepath.endswith(".csv"):
        # Header + data rows
        total_lines = count_lines(filepath)
        return max(0, total_lines - 1)

    if filepath.endswith(".sql"):
        # Count values tuples
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Count instances of "  (" starting tuple rows
                matches = re.findall(r"^\s*\([^)]+\)", content, re.MULTILINE)
                return len(matches)
        except Exception:
            return 0

    return 0


def build_manifest(artifacts_dir: str, seed: int, profile_name: str, table_counts: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Generates source_manifest.json containing logical row counts, SHA-256 hashes, and line counts."""
    manifest_dir = os.path.join(artifacts_dir, "manifest")
    os.makedirs(manifest_dir, exist_ok=True)

    files_manifest: Dict[str, Dict[str, Any]] = {}
    table_row_counts: Dict[str, int] = {}

    subdirs = ["csv", "json", "sql", "ground_truth"]
    for sub in subdirs:
        dir_path = os.path.join(artifacts_dir, sub)
        if not os.path.exists(dir_path):
            continue
        for root, _, files in sorted(os.walk(dir_path)):
            for file in sorted(files):
                if file.endswith((".csv", ".json", ".sql")):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, artifacts_dir).replace("\\", "/")
                    table_name = os.path.splitext(file)[0]
                    logical_rows = determine_logical_row_count(full_path, table_counts)

                    if table_name not in table_row_counts and not table_name.startswith("source_"):
                        table_row_counts[table_name] = logical_rows

                    files_manifest[rel_path] = {
                        "row_count": logical_rows,
                        "line_count": count_lines(full_path),
                        "sha256": compute_file_sha256(full_path),
                        "size_bytes": os.path.getsize(full_path),
                    }

    manifest_data = {
        "manifest_version": "1.1.0",
        "master_seed": seed,
        "dataset_profile": profile_name,
        "base_epoch": "2026-01-01T00:00:00Z",
        "file_count": len(files_manifest),
        "table_row_counts": table_row_counts,
        "files": files_manifest,
    }

    manifest_path = os.path.join(manifest_dir, "source_manifest.json")
    with open(manifest_path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, sort_keys=True)

    return manifest_data
