"""CLI entrypoint for deterministic data generator."""
import argparse
import os
from generator.src.config import MASTER_SEED, get_profile
from generator.src.master_data import generate_master_data
from generator.src.transactions import generate_transactions
from generator.src.outcomes import generate_outcomes_and_defects
from generator.src.anomalies import inject_anomalies
from generator.src.exports import export_all
from generator.src.manifest import build_manifest


def run_generation(profile_name: str = "starter", seed: int = MASTER_SEED, artifacts_dir: str = "artifacts", sql_dir: str = "sql"):
    """Runs complete deterministic synthetic data generation including anomalies and ground truth."""
    print(f"=== Starting Deterministic Data Generation ===")
    print(f"Profile: {profile_name}")
    print(f"Master Seed: {seed}")
    print(f"Artifacts Dir: {artifacts_dir}")
    print(f"SQL Dir: {sql_dir}")

    profile = get_profile(profile_name)

    # 1. Master Data
    print("Generating master data...")
    master = generate_master_data(profile, seed)

    # 2. Transactions
    print("Generating transactions & balance reconciliations...")
    trans = generate_transactions(master, profile, seed)

    # 3. Outcomes & Quality Lifecycle
    print("Generating inspection outcomes, defects, CAPAs, and state events...")
    outcomes = generate_outcomes_and_defects(master, trans, seed)

    baseline_dataset = {
        "products": master["products"],
        "suppliers": master["suppliers"],
        "boms": master["boms"],
        "bom_lines": master["bom_lines"],
        "machines": master["machines"],
        "process_steps": master["process_steps"],
        "inspection_plans": master["inspection_plans"],
        "material_lots": trans["material_lots"],
        "production_orders": trans["production_orders"],
        "material_consumptions": trans["material_consumptions"],
        "process_executions": trans["process_executions"],
        "inspection_results": trans["inspection_results"],
        "defects": outcomes["defects"],
        "containment_actions": outcomes["containment_actions"],
        "corrective_actions": outcomes["corrective_actions"],
        "capa_verifications": outcomes["capa_verifications"],
        "state_events": outcomes["state_events"],
    }

    # 4. Inject 5 Safe Anomalies
    print("Injecting deliberate safe anomalies and building isolated ground truth...")
    dataset, ground_truth = inject_anomalies(baseline_dataset)

    print(f"Generated {len(dataset['products'])} Products")
    print(f"Generated {len(dataset['suppliers'])} Suppliers")
    print(f"Generated {len(dataset['material_lots'])} Material Lots")
    print(f"Generated {len(dataset['production_orders'])} Production Orders")
    print(f"Generated {len(dataset['inspection_results'])} Inspection Results")
    print(f"Generated {len(dataset['defects'])} Defects")
    print(f"Generated {len(dataset['containment_actions'])} Containment Actions")
    print(f"Generated {len(dataset['corrective_actions'])} Corrective Actions (CAPAs)")
    print(f"Generated {len(dataset['capa_verifications'])} CAPA Verifications")
    print(f"Generated {len(dataset['state_events'])} State Events")
    print(f"Generated {len(ground_truth)} Labelled Ground-Truth Anomalies")

    # 5. Exports
    print("Exporting CSV, JSON, SQL seed, and Ground Truth files...")
    export_all(dataset, artifacts_dir, sql_dir, ground_truth)

    # 6. Manifest
    print("Building source manifest and SHA-256 checksums...")
    table_counts = {k: len(v) for k, v in dataset.items()}
    table_counts["ground_truth"] = len(ground_truth)
    manifest = build_manifest(artifacts_dir, seed, profile_name, table_counts)
    print(f"Manifest written with {manifest['file_count']} tracked files.")
    print("=== Generation Completed Successfully ===")
    return dataset, ground_truth, manifest


def main():
    parser = argparse.ArgumentParser(description="Deterministic Synthetic Data Generator CLI")
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser("generate", help="Generate synthetic dataset")
    gen_parser.add_argument("--profile", default=os.getenv("GENERATOR_PROFILE", "starter"), choices=["starter", "full"])
    gen_parser.add_argument("--seed", type=int, default=int(os.getenv("GENERATOR_SEED", MASTER_SEED)))
    gen_parser.add_argument("--artifacts-dir", default=os.getenv("ARTIFACTS_DIR", "artifacts"))
    gen_parser.add_argument("--sql-dir", default=os.getenv("SQL_DIR", "sql"))

    args = parser.parse_args()

    if args.command == "generate":
        run_generation(args.profile, args.seed, args.artifacts_dir, args.sql_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
