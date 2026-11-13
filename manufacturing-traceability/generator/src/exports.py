"""Deterministic CSV, JSON, and SQL export engine."""
import csv
import json
import os
from typing import Dict, List, Any


def write_csv(path: str, records: List[Dict[str, Any]]):
    """Writes records to CSV with deterministic column ordering and LF newlines."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not records:
        with open(path, "w", newline="", encoding="utf-8") as f:
            pass
        return

    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def write_json(path: str, records: List[Dict[str, Any]]):
    """Writes records to JSON with sorted keys and 2-space indentation."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(records, f, indent=2, sort_keys=True)


def format_sql_value(val: Any) -> str:
    """Formats Python values into safe SQL literal strings."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float)):
        return str(val)
    # Strings, dates, timestamps
    s_val = str(val).replace("'", "''")
    return f"'{s_val}'"


def generate_sql_inserts(table_name: str, records: List[Dict[str, Any]]) -> str:
    """Generates batched SQL INSERT statements."""
    if not records:
        return ""

    columns = list(records[0].keys())
    col_str = ", ".join(columns)
    lines = [f"-- Table: {table_name}"]

    # Batch in groups of 100 for optimal execution
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        val_rows = []
        for r in batch:
            row_vals = [format_sql_value(r[c]) for c in columns]
            val_rows.append(f"  ({', '.join(row_vals)})")
        lines.append(f"INSERT INTO {table_name} ({col_str}) VALUES\n" + ",\n".join(val_rows) + "\nON CONFLICT DO NOTHING;\n")

    return "\n".join(lines) + "\n"


def export_all(dataset: Dict[str, List[Dict[str, Any]]], artifacts_dir: str, sql_dir: str):
    """Exports all dataset entities to artifacts/csv, artifacts/json, and sql/seed.sql."""
    csv_dir = os.path.join(artifacts_dir, "csv")
    json_dir = os.path.join(artifacts_dir, "json")
    sql_art_dir = os.path.join(artifacts_dir, "sql")

    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(sql_art_dir, exist_ok=True)
    os.makedirs(sql_dir, exist_ok=True)

    sql_statements = ["-- Manufacturing Defect-Traceability Seed Data\n-- Generated deterministically from seed 20261022\n\n"]

    # Table insertion order respecting foreign-key hierarchy
    table_order = [
        ("products", "products"),
        ("suppliers", "suppliers"),
        ("boms", "boms"),
        ("bom_lines", "bom_lines"),
        ("machines", "machines"),
        ("process_steps", "process_steps"),
        ("inspection_plans", "inspection_plans"),
        ("material_lots", "material_lots"),
        ("production_orders", "production_orders"),
        ("material_consumptions", "material_consumptions"),
        ("process_executions", "process_executions"),
        ("inspection_results", "inspection_results"),
        ("defects", "defects"),
        ("containment_actions", "containment_actions"),
        ("corrective_actions", "corrective_actions"),
        ("capa_verifications", "capa_verifications"),
        ("state_events", "state_events"),
    ]

    for table_name, data_key in table_order:
        records = dataset.get(data_key, [])
        # Write CSV
        write_csv(os.path.join(csv_dir, f"{table_name}.csv"), records)
        # Write JSON
        write_json(os.path.join(json_dir, f"{table_name}.json"), records)
        # Append SQL
        if records:
            sql_statements.append(generate_sql_inserts(table_name, records))

    full_sql = "".join(sql_statements)
    # Write to sql/seed.sql and artifacts/sql/seed.sql
    with open(os.path.join(sql_dir, "seed.sql"), "w", newline="\n", encoding="utf-8") as f:
        f.write(full_sql)
    with open(os.path.join(sql_art_dir, "seed.sql"), "w", newline="\n", encoding="utf-8") as f:
        f.write(full_sql)
