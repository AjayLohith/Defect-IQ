"""CLI Entrypoint for the deterministic generator."""
import argparse
from generator.src.config import MASTER_SEED, get_profile


def main():
    parser = argparse.ArgumentParser(description="Deterministic Synthetic Data Generator CLI")
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser("generate", help="Generate synthetic dataset")
    gen_parser.add_argument("--profile", default="starter", choices=["starter", "full"])
    gen_parser.add_argument("--seed", type=int, default=MASTER_SEED)

    args = parser.parse_args()

    if args.command == "generate":
        print(f"Generator initialized with seed={args.seed}, profile={args.profile}")
        print("Scaffold ready for Phase 3 implementation.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

