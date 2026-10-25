# Results

All runs on: Windows, Python 3.14.8, `MockModel` (deterministic), corpus = `data/attack_corpus.json` (23 attacks + 5 benign controls).
Run artifacts in `results/run_*.json`.

## Ablation table (static corpus)

| Profile | Defenses enabled | ASR | Attacks blocked | FPR | Artifact |
|---|---|---|---|---|---|
| none | (baseline) | 11/23 = 47.8% | 12 | 0/5 = 0.0% | `run_*_none.json` |
| prompt_guard | `prompt_guard` | 8/23 = 34.8% | 15 | 0/5 = 0.0% | `run_*_prompt_guard.json` |
| authz | `authz` | 11/23 = 47.8% | 12 | 0/5 = 0.0% | `run_*_authz.json` |
| all | `input_validation`, `prompt_guard`, `authz` | 8/23 = 34.8% | 15 | 0/5 = 0.0% | `run_*_all.json` |
| output_filter | `output_filter` | 0/23 = 0.0% | 23 | 0/5 = 0.0% | `run_*_output_filter.json` |
| all_plus_output | `input_validation`, `prompt_guard`, `authz`, `output_filter` | 0/23 = 0.0% | 23 | 0/5 = 0.0% | `run_*_all_plus_output.json` |

## Determinism check

`prompt_guard` was run twice, on separate invocations, in the same session.
Both runs produced **8/23 = 34.8% ASR**. The MockModel, judge, and pipeline are deterministic; ablation differences reflect defense changes, not measurement noise. This is a precondition for interpreting the ablation table.

## Findings

1. **Keyword blocklisting catches only 3 of 11 baseline successes (27%).** The 7-phrase blocklist in `app/prompt_guard.py` does not match paraphrases such as "ignore prior", "override", "disregard", "forget your", or "act as an admin". Consistent with OWASP LLM Top 10 2026: injection "cannot be fully prevented" by pattern matching.

2. **Pipeline-level authorization is redundant with tool-level authorization.** `authz` produces no measurable change because `execute_mock_tool()` in `app/app.py` enforces role checks internally. Control placement matters as much as control existence.

3. **No synergy between input-side layers.** `all` (34.8%) equals `prompt_guard` alone (34.8%).

4. **Output filtering closes the leak path on this corpus.** With `output_filter` enabled, ASR drops to 0/23. This is expected: every baseline success is a text leak containing a marker that the filter matches.

5. **The 0/23 result is NOT a robustness claim, and must not be presented as one.** The output filter is signature-based. It matches the literal strings in `SYSTEM_PROMPT_MARKERS` and `RESTRICTED_DATA_MARKERS`. Two attack classes trivially evade it: (a) a leaked prompt formatted differently from the mock's leak template, and (b) an encoded leak (base64, homoglyphs, character-splitting) where the markers no longer appear as substrings. Stage 3 quantifies this gap.

## Hypotheses for Stage 3 (adaptive attacks)

- H1: `prompt_guard` ASR rises substantially on paraphrase attacks that the 7-phrase list does not match but the model still obeys.
- H2: `output_filter` ASR rises on encoded-output attacks, because the filter matches literal strings only.
- H3: The gap between static-corpus ASR and adaptive-corpus ASR is the metric that distinguishes a signature defense from a robust one.

## Limitations

- `MockModel` is deterministic and simulates an over-compliant LLM. It does not represent any specific real model. Stage 4 replaces the adapter without changing the pipeline.
- Corpus is small (n=23 attacks, n=5 benign). Percentages are indicative, not statistically conclusive. Confidence intervals are added in Stage 3.
- All current attacks target the mock's known trigger words. Attackers with knowledge of the defense would attack with different phrasings (Stage 3).

## Next steps

- **Stage 3:** Adaptive corpus + confidence intervals (Wilson). Expect `prompt_guard` ASR to rise and `output_filter` ASR to be tested against encoding.
- **Stage 4:** Swap `MockModel` for API and local adapters; compare ASR / FPR / utility tradeoffs.
