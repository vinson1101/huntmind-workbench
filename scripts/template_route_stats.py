from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.sequence_identifier import describe_route


def load_gold(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate JD -> template routing against a manual gold set.")
    parser.add_argument(
        "--gold",
        default="evals/template_routing_gold.jsonl",
        help="Path to the manual JD-template calibration set.",
    )
    args = parser.parse_args()

    rows = load_gold(Path(args.gold))
    hit_counter = Counter()
    matched = 0
    details = []

    for row in rows:
        route = describe_route(row["jd_title"])
        predicted = route["template_id"]
        expected = row["expected_template"]
        ok = predicted == expected
        matched += int(ok)
        hit_counter[predicted] += 1
        details.append(
            {
                "jd_title": row["jd_title"],
                "expected_template": expected,
                "predicted_template": predicted,
                "ok": ok,
                "score": route["score"],
                "matched_terms": route["matched_terms"],
                "excluded_by": route["excluded_by"],
                "reasons": route["reasons"],
                "notes": row.get("notes", ""),
            }
        )

    result = {
        "total": len(rows),
        "matched": matched,
        "accuracy": round(matched / len(rows), 4) if rows else 0.0,
        "template_hits": dict(hit_counter),
        "details": details,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
