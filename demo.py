"""Print decisions for synthetic evidence without calling any external service."""

import argparse
import json
from pathlib import Path
import sys

from gate import evaluate

ROOT = Path(__file__).resolve().parent
SCENARIOS = {
    "matched-commit.json": ("PASS", "HUMAN_REVIEW"),
    "regression.json": ("FAIL", "REMEDIATE"),
    "stale-commit.json": ("ESCALATE", "STOP"),
    "cycle-limit.json": ("ESCALATE", "STOP"),
}


def load(path):
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"Duplicate JSON key: {key}")
            obj[key] = value
        return obj

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, help="Evaluate one synthetic JSON report")
    args = parser.parse_args()
    if args.evidence:
        try:
            decision = evaluate(load(args.evidence))
        except (OSError, ValueError) as error:
            print(json.dumps({"verdict": "ESCALATE", "next_action": "STOP", "reasons": [str(error)]}, indent=2))
            return 2
        print(json.dumps(decision.to_dict(), indent=2))
        return {"PASS": 0, "FAIL": 1, "ESCALATE": 2}[decision.verdict]
    for name, expected in SCENARIOS.items():
        decision = evaluate(load(ROOT / "examples" / "evidence" / name))
        print(f"{name}: {decision.verdict} -> {decision.next_action}")
        for reason in decision.reasons:
            print(f"  {reason}")
        if (decision.verdict, decision.next_action) != expected:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
