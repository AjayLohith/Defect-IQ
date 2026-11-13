"""Generator configuration profiles and deterministic seed settings."""
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

MASTER_SEED = 20261022
BASE_EPOCH = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def derive_subseed(master_seed: int, domain: str) -> int:
    """Derive a deterministic integer sub-seed from master seed and domain name.
    Strictly avoids Python's built-in hash() to guarantee cross-process stability.
    """
    key = f"{master_seed}:{domain}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    return int.from_bytes(digest[:8], "big")


@dataclass(frozen=True)
class DatasetProfile:
    name: str
    product_count: int
    supplier_count: int
    material_lot_count: int
    production_order_count: int
    inspection_result_count: int
    machine_count: int
    process_step_count: int


PROFILES = {
    "starter": DatasetProfile(
        name="starter",
        product_count=20,
        supplier_count=10,
        material_lot_count=100,
        production_order_count=200,
        inspection_result_count=800,
        machine_count=10,
        process_step_count=5,
    ),
    "full": DatasetProfile(
        name="full",
        product_count=200,
        supplier_count=50,
        material_lot_count=2000,
        production_order_count=5000,
        inspection_result_count=20000,
        machine_count=30,
        process_step_count=6,
    ),
}


def get_profile(name: str = "starter") -> DatasetProfile:
    return PROFILES.get(name, PROFILES["starter"])
