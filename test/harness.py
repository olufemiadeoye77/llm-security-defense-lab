"""Run the attack corpus through the pipeline at a given defense profile."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from app.app import User
from app.pipeline import run
from test.judge import judge

ROOT = Path(__file__).parent.parent
CORPUS = ROOT / "data" / "attack_corpus.json"
RESULTS = ROOT / "results"

PROFILES = {
    "none":             set(),
    "input_validation": {"input_validation"},
    "prompt_guard":     {"prompt_guard"},
    "authz":            {"authz"},
    "all":              {"input_validation", "prompt_guard", "authz"},
}


def run_corpus(profile_name: str) -> list:
    cases = json.loads(CORPUS.read_text(encoding="utf-8-sig"))
    defenses = PROFILES[profile_name]
    out = []
    for case in cases:
        role = case.get("actor_role", "analyst")
        user = User(user_id="harness-" + role, role=role)
        result = run(user, case["input"], defenses=defenses)
        verdict = judge(case, result)
        out.append({
            "test_id": case["test_id"],
            "category": case["category"],
            "kind": case.get("kind", "attack"),
            "input": case["input"],
            "blocked": result.blocked,
            "block_reason": result.block_reason,
            "verdict": verdict,
        })
    return out


def summarize(rows: list) -> dict:
    attacks = [r for r in rows if r["kind"] == "attack"]
    benign = [r for r in rows if r["kind"] == "benign"]
    succeeded = [r for r in attacks if r["verdict"] == "attack_succeeded"]
    blocked = [r for r in attacks if r["verdict"] == "attack_blocked"]
    fpos = [r for r in benign if r["verdict"] == "false_positive"]
    allowed = [r for r in benign if r["verdict"] == "allowed"]

    asr = (len(succeeded) / len(attacks) * 100) if attacks else 0.0
    fpr = (len(fpos) / len(benign) * 100) if benign else 0.0

    print("  Attacks : " + str(len(attacks)))
    print("  Success : " + str(len(succeeded)) + "   Blocked: " + str(len(blocked)))
    print("  ASR     : " + str(len(succeeded)) + "/" + str(len(attacks))
          + " = {:.1f}%".format(asr))
    print("  Benign  : " + str(len(benign)))
    print("  FP      : " + str(len(fpos)) + "   Allowed: " + str(len(allowed)))
    print("  FPR     : " + str(len(fpos)) + "/" + str(len(benign))
          + " = {:.1f}%".format(fpr))

    return {
        "total_attacks": len(attacks),
        "attacks_succeeded": len(succeeded),
        "attacks_blocked": len(blocked),
        "asr_percent": round(asr, 2),
        "total_benign": len(benign),
        "false_positives": len(fpos),
        "fpr_percent": round(fpr, 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--defenses", default="none", choices=list(PROFILES))
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    print("Profile: " + args.defenses)
    print("Defenses: " + str(sorted(PROFILES[args.defenses])))
    print()

    rows = run_corpus(args.defenses)
    summary = summarize(rows)

    if args.save:
        RESULTS.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = RESULTS / ("run_" + ts + "_" + args.defenses + ".json")
        path.write_text(json.dumps({
            "timestamp": ts,
            "profile": args.defenses,
            "defenses": sorted(PROFILES[args.defenses]),
            "summary": summary,
            "rows": rows,
        }, indent=2), encoding="utf-8")
        print("\n  Saved: " + str(path))


if __name__ == "__main__":
    main()
