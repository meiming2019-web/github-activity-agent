"""Exact normalized-text deduplication against both frozen historical sets."""

import argparse
import json
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]


def normalized_text(text):
    """Compare case-folded NFKC text with punctuation and whitespace normalized."""
    return re.sub(r"[^\w]+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def check_dedup(records):
    """Require unique v4 question text and no full-question overlap with v2/v3."""
    old = {normalized_text(json.loads(line)["question"])
           for path in (ROOT / "eval/github_test_questions_v2.jsonl", ROOT / "eval/v3_questions.jsonl")
           for line in path.read_text().splitlines() if line.strip()}
    texts = [normalized_text(record["question"]) for record in records]
    assert len(set(texts)) == len(texts), "Duplicate normalized v4 question text."
    assert not set(texts) & old, "Normalized question overlaps a frozen historical question."
    return {"v4_unique": len(texts), "historical_unique": len(old), "historical_overlap": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=ROOT / "eval/v4_questions.jsonl")
    args = parser.parse_args()
    records = [json.loads(line) for line in args.path.read_text().splitlines() if line.strip()]
    print(json.dumps(check_dedup([row for row in records if row.get("record_type") == "question"])))
