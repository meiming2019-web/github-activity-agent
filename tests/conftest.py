"""Skip only frozen-snapshot integration cases when the local snapshot is absent."""

from pathlib import Path

import pytest


SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "data/github.duckdb"
# Exact function names preserve parameterized cases without skipping whole modules.
# Temporary-database fixtures and substituted transports do not need this snapshot.
FROZEN_SNAPSHOT_TESTS = {
    "test_v4_bounds.py": {
        "test_real_new_entry_and_independent_parser_reject_invalid_questions",
        "test_new_entry_real_offline_gate_all_105_intervals_and_adversarial_cases",
        "test_legacy_full_context_replay_uses_original_source_and_real_database",
    },
    "test_v4_generation.py": {
        "test_each_template_executes_through_real_readonly_allowlist",
        "test_language_rankings_have_explicit_deterministic_ties",
        # Even with substituted SQL, generate() hashes the actual snapshot bytes.
        "test_fixed_seed_and_finite_regeneration_failure",
        "test_full_generation_reproducibility_structure_sensitivity_and_probes",
    },
}


def _snapshot_missing(path):
    """Only absence is optional; permission errors and existing invalid files are not."""
    try:
        path.stat()
    except FileNotFoundError:
        return True
    return False


def pytest_collection_modifyitems(items):
    """Apply one explicit missing-snapshot reason to the audited integration cases."""
    if not _snapshot_missing(SNAPSHOT_PATH):
        return
    skip = pytest.mark.skip(reason=(
        "Frozen snapshot data/github.duckdb is missing; obtain the verified snapshot "
        "as documented in README.md to run the complete integration suite. "
        "This skip does not validate snapshot-dependent behavior."
    ))
    for item in items:
        if getattr(item, "originalname", item.name) in FROZEN_SNAPSHOT_TESTS.get(item.path.name, ()):
            item.add_marker(skip)
