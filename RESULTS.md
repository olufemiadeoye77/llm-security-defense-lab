# Results

All runs on: Windows, Python 3.14.8, `MockModel` (deterministic), corpus = `data/attack_corpus.json` (23 attacks + 5 benign controls).
Run artifacts in `results/run_*.json`.

## Ablation table

| Profile | Defenses enabled | ASR | Attacks blocked | FPR | Artifact |
|---|---|---|---|---|---|
| none | (baseline) | 11/23 = 47.8% | 12 | 0/5 = 0.0% | `run_*_none.json` |
| prompt_guard | `prompt_guard` | 8/23 = 34.8% | 15 | 0/5 = 0.0% | `run_*_prompt_guard.json` |
| authz | `authz` | 11/23 = 47.8% | 12 | 0/5 = 0.0% | `run_*_authz.json` |
| all | `input_validation`, `prompt_guard`, `authz` | 8/23 = 34.8% | 15 | 0/5 = 0.0% | `run_*_all.json` |

## Findings

1. **Keyword blocklisting catches only 3 of 11 baseline successes (27%).** The 7-phrase blocklist in `app/prompt_guard.py` does not match paraphrases such as "ignore prior", "override", "disregard", "forget your", or "act as an admin". This is consistent with the OWASP LLM Top 10 2026 note that injection "cannot be fully prevented" by pattern matching.

2. **Pipeline-level authorization is redundant with tool-level authorization.** `authz` produces no measurable change because `execute_mock_tool()` in `app/app.py` enforces role checks internally. Control placement matters as much as control existence.

3. **No synergy between layers.** `all` (34.8%) equals `prompt_guard` alone (34.8%). The 8 remaining successes are text-leak attacks that neither layer inspects.

4. **Missing control identified: output filtering.** No current layer inspects the model response. System-prompt leakage therefore succeeds whenever the model produces it, regardless of input filtering or tool authorization.

## Limitations

- `MockModel` is deterministic and simulates an over-compliant LLM. Real LLM behavior will differ (Stage 4 replaces the adapter without changing the pipeline).
- Corpus is small (n=23 attacks, n=5 benign). Percentages are indicative, not statistically conclusive. Confidence intervals will be added in Stage 3.
- Attacks in this corpus were designed against the known blocklist; a truly independent corpus would produce different numbers.

## Next steps

- **Stage 2:** Add an output-filter defense layer; rerun the ablation.
- **Stage 3:** Adaptive attacks (paraphrased, encoded, multi-turn) + confidence intervals.
- **Stage 4:** Swap `MockModel` for API and local adapters; compare ASR / FPR / utility tradeoffs.
