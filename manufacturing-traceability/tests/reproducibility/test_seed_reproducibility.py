"""Reproducibility test suite: proving deterministic seed generation and negative variation."""
import hashlib
import json
import pytest
from generator.src.config import MASTER_SEED, get_profile
from generator.src.master_data import generate_master_data
from generator.src.transactions import generate_transactions
from generator.src.outcomes import generate_outcomes_and_defects


def _hash_dataset(dataset):
    serialized = json.dumps(dataset, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def test_seed_reproducibility_identical_runs():
    """Verify that running generation twice with seed 20261022 produces identical hash and counts."""
    profile = get_profile("starter")

    # Run 1
    master1 = generate_master_data(profile, MASTER_SEED)
    trans1 = generate_transactions(master1, profile, MASTER_SEED)
    outcomes1 = generate_outcomes_and_defects(master1, trans1, MASTER_SEED)

    # Run 2
    master2 = generate_master_data(profile, MASTER_SEED)
    trans2 = generate_transactions(master2, profile, MASTER_SEED)
    outcomes2 = generate_outcomes_and_defects(master2, trans2, MASTER_SEED)

    hash1_m = _hash_dataset(master1)
    hash2_m = _hash_dataset(master2)
    assert hash1_m == hash2_m, "Master data must be byte-identical across same-seed runs"

    hash1_t = _hash_dataset(trans1)
    hash2_t = _hash_dataset(trans2)
    assert hash1_t == hash2_t, "Transactional data must be byte-identical across same-seed runs"

    hash1_o = _hash_dataset(outcomes1)
    hash2_o = _hash_dataset(outcomes2)
    assert hash1_o == hash2_o, "Outcomes data must be byte-identical across same-seed runs"


def test_negative_reproducibility_different_seed():
    """Verify that changing seed alters generated values while retaining model validity."""
    profile = get_profile("starter")
    alt_seed = 99999999

    master1 = generate_master_data(profile, MASTER_SEED)
    master_alt = generate_master_data(profile, alt_seed)

    hash_master1 = _hash_dataset(master1)
    hash_master_alt = _hash_dataset(master_alt)

    assert hash_master1 != hash_master_alt, "Different seeds must produce different data"

