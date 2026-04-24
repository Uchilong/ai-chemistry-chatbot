"""Basic chemistry evaluation scaffold for local quality tracking."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def load_eval_set(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def score_response(case: Dict[str, Any], response: str) -> Dict[str, Any]:
    text = response.lower()
    expected = [k.lower() for k in case.get("expected_keywords", [])]
    hit_count = sum(1 for k in expected if k in text)
    keyword_score = hit_count / max(len(expected), 1)
    units_ok = True
    if case.get("must_include_units", False):
        units_ok = any(unit in text for unit in ["g/mol", "mol", "m", "atm", "kj"])
    return {
        "id": case["id"],
        "category": case["category"],
        "keyword_score": round(keyword_score, 3),
        "units_ok": units_ok,
        "pass": keyword_score >= 0.6 and units_ok,
    }


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    by_category: Dict[str, List[float]] = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r["keyword_score"])
    return {
        "total_cases": total,
        "pass_rate": round(passed / max(total, 1), 3),
        "category_keyword_avg": {
            c: round(sum(vals) / len(vals), 3) for c, vals in by_category.items()
        },
    }


def main() -> None:
    eval_path = Path(__file__).parent / "chemistry_eval_set.json"
    dataset = load_eval_set(eval_path)
    print(f"Loaded {len(dataset)} chemistry eval cases.")
    print("This scaffold expects model outputs from your app pipeline.")
    print("Next step: wire live response generation into this runner.")


if __name__ == "__main__":
    main()
