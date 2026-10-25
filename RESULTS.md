# Results

Runs: Windows, Python 3.14.8, `MockModel` (deterministic). Two corpora:
- `data/attack_corpus.json` — 23 attacks + 5 benign (defense-naive)
- `data/adaptive_corpus.json` — 23 attacks + 5 benign (defense-aware: paraphrases + base64 encoding)

All run artifacts in `results/run_*.json`. Confidence intervals are Wilson 95%.

## Static corpus (defense-naive)

| Profile | ASR | 95% CI | FPR | 95% CI |
|---|---|---|---|---|
| none | 11/23 = 47.8% | — | 0/5 = 0.0% | — |
| prompt_guard | 8/23 = 34.8% | 18.8–55.1% | 0/5 = 0.0% | — |
| authz | 11/23 = 47.8% | — | 0/5 = 0.0% | — |
| all (no output) | 8/23 = 34.8% | 18.8–55.1% | 0/5 = 0.0% | — |
| output_filter | 0/23 = 0.0% | 0.0–14.3% | 0/5 = 0.0% | — |
| all_plus_output | 0/23 = 0.0% | 0.0–14.3% | 0/5 = 0.0% | — |

## Adaptive corpus (defense-aware)

| Profile | ASR | 95% CI | FPR | 95% CI |
|---|---|---|---|---|
| none | 23/23 = 100.0% | 85.7–100.0% | 0/5 = 0.0% | — |
| prompt_guard | **23/23 = 100.0%** | 85.7–100.0% | 0/5 = 0.0% | — |
| output_filter | **7/23 = 30.4%** | 15.6–50.9% | 0/5 = 0.0% | — |
| all_plus_output | **7/23 = 30.4%** | 15.6–50.9% | 0/5 = 0.0% | — |

## Headline finding

**Signature-based defenses collapse under adaptive attacks.**

- `prompt_guard` (7-phrase blocklist): **34.8% → 100% ASR** when the attacker knows the blocklist. Every single adaptive attack evades the filter. This defense contributes zero protection against a knowing adversary.
- `output_filter` (literal-string markers): **0.0% → 30.4% ASR** when the leak is base64-encoded. The filter matches English substrings only; ciphertext contains none.
- Layered `all_plus_output`: **30.4%** — same as `output_filter` alone, because `prompt_guard` provides no protection in this regime.

## Static vs adaptive: the comparison that matters

| Defense | Static ASR | Adaptive ASR | Delta |
|---|---|---|---|
| prompt_guard | 34.8% | 100.0% | **+65.2 pp** |
| output_filter | 0.0% | 30.4% | **+30.4 pp** |
| all_plus_output | 0.0% | 30.4% | **+30.4 pp** |

A defense's static-corpus ASR is an **upper bound on its robustness, not a measure of it**. The gap between the two columns is the price of relying on signature-based detection.

## Confirmations

- **H1 confirmed:** prompt_guard ASR rises substantially on adaptive attacks (34.8% → 100%, both deterministic).
- **H2 confirmed:** output_filter ASR rises on encoded outputs (0% → 30.4%), bounded by the 7 encoded attacks in the corpus.
- **H3 confirmed:** static-vs-adaptive gap distinguishes signature defense from robust defense quantitatively.

## Determinism check

`prompt_guard` and `output_filter` were re-run on the static corpus with the Stage 3 mock. Both reproduced Stage 1–2 numbers exactly (8/23 and 0/23). The mock changes are backward-compatible; ablation differences reflect defense changes, not measurement noise.

## Findings

1. **Keyword blocklisting catches only 3 of 11 baseline successes on static corpus (27%).** On adaptive corpus, catches 0 of 23. Paraphrase alone defeats it.

2. **Pipeline-level authorization is redundant with tool-level authorization.** `authz` produces no measurable change on either corpus because `execute_mock_tool()` in `app/app.py` enforces role checks internally.

3. **Output filtering closes the static leak path but not the encoded path.** Base64-encoded leaks pass through because the filter matches English markers.

4. **The 0/23 on the static corpus is not a robustness claim.** The adaptive corpus demonstrates this: same defense, same code, 30.4% ASR.

5. **Defense-in-depth fails when a layer contributes zero protection.** `all_plus_output` = `output_filter` alone because `prompt_guard` protects nothing against adaptive attackers.

## Limitations

- `MockModel` is deterministic and simulates an over-compliant LLM. Real LLMs will exhibit different baseline ASR but the same qualitative ranking of defenses is expected to hold (to be verified in Stage 4).
- Corpora are small (n=23 each). Wilson CIs are wide (e.g. 15.6–50.9% for output_filter adaptive). Point estimates are indicative; the ranking is the defensible claim.
- Adaptive corpus was designed to target known signatures of the included defenses. An attacker without corpus knowledge would see different numbers — this is the point, not a limitation.
- No adaptive attacks against the encoding defense yet (e.g. ROT13, hex, multi-turn split). Stage 4 or follow-up work.

## Next steps

- **Stage 4:** Swap `MockModel` for API and local adapters. Confirm the qualitative ranking (output_filter > prompt_guard > none) holds on real models; measure utility cost of each defense.
- **Stage 5:** Paper-formatted report, Zenodo DOI, reproducibility package, GitHub release tag.
