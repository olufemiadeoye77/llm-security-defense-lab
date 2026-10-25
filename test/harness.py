"""Run a corpus through the pipeline at a given defense profile."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from app.app import User
from app.pipeline import run
from test.judge import judge
from test.stats import wilson_ci

ROOT = Path(__file__).parent.parent
RESULTS = ROOT / "results"

CORPORA = {
    "static":   ROOT / "data" / "attack_corpus.json",
    "adaptive": ROOT / "data" / "adaptive_corpus.json",
}

PROFILES = {
    "none":            set(),
    "prompt_guard":    {"prompt_guard"},
    "authz":           {"authz"},
    "output_filter":   {"output_filter"},
    "all":             {"input_validation", "prompt_guard", "authz"},
    "all_plus_output": {"input_validation", "prompt_guard", "authz", "output_filter"},
}


def run_corpus(corpus_name: str, profile_name: str) -> list:
    cases = json.loads(CORPORA[corpus_name].read_text(encoding="utf-8-sig"))
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
            "output_findings": result.output_findings or [],
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
    asr_ci = wilson_ci(len(succeeded), len(attacks))
    fpr_ci = wilson_ci(len(fpos), len(benign))

    print("  Attacks : " + str(len(attacks)))
    print("  ASR     : {}/{} = {:.1f}%  [95% CI {:.1f}-{:.1f}%]".format(
        len(succeeded), len(attacks), asr, asr_ci[0] * 100, asr_ci[1] * 100))
    print("  Benign  : " + str(len(benign)))
    print("  FPR     : {}/{} = {:.1f}%  [95% CI {:.1f}-{:.1f}%]".format(
        len(fpos), len(benign), fpr, fpr_ci[0] * 100, fpr_ci[1] * 100))

    return {
        "total_attacks": len(attacks),
        "attacks_succeeded": len(succeeded),
        "attacks_blocked": len(blocked),
        "asr_percent": round(asr, 2),
        "asr_ci_low": round(asr_ci[0] * 100, 2),
        "asr_ci_high": round(asr_ci[1] * 100, 2),
        "total_benign": len(benign),
        "false_positives": len(fpos),
        "fpr_percent": round(fpr, 2),
        "fpr_ci_low": round(fpr_ci[0] * 100, 2),
        "fpr_ci_high": round(fpr_ci[1] * 100, 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="static", choices=list(CORPORA))
    parser.add_argument("--defenses", default="none", choices=list(PROFILES))
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    print("Corpus: " + args.corpus + "   Profile: " + args.defenses)
    print("Defenses: " + str(sorted(PROFILES[args.defenses])))
    print()

    rows = run_corpus(args.corpus, args.defenses)
    summary = summarize(rows)

    if args.save:
        RESULTS.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = RESULTS / ("run_" + ts + "_" + args.corpus + "_" + args.defenses + ".json")
        path.write_text(json.dumps({
            "timestamp": ts,
            "corpus": args.corpus,
            "profile": args.defenses,
            "defenses": sorted(PROFILES[args.defenses]),
            "summary": summary,
            "rows": rows,
        }, indent=2), encoding="utf-8")
        print("\n  Saved: " + str(path))


if __name__ == "__main__":
    main()
