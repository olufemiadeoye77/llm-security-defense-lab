# Paper Outline — LLM Security Defense Lab

**Working title:** Measuring the Limits of Signature-Based Prompt-Injection Defenses: A Dual-Corpus Study Across a Deterministic Mock and a Real RLHF-Aligned Model

**Author:** Olufemi Adeoye
**Status:** Outline (pre-prose) — 2026-10-25

---

## Abstract (150–200 words)

One paragraph covering:
- The problem: prompt injection (OWASP LLM01:2026) resists signature defenses; the field needs empirical measurements of *when* they fail.
- The method: dual-corpus (defense-naive + defense-aware), dual-adapter (deterministic mock + real `openai/gpt-oss-20b`) ablation of four pipeline defenses.
- The two findings: (i) signature defenses collapse under adaptive attack (mock: 34.8% → 100%, 0% → 30.4%); (ii) model alignment is the strongest single defense (real model: 0/23 at baseline, no pipeline controls active).
- The implication: static-corpus ASR is an upper bound on robustness, not a measure of it; mock-only evaluations overestimate pipeline defenses.

---

## 1. Introduction (~500 words)

- 1.1 Prompt injection is #1 on OWASP LLM Top 10 2026 and "cannot be fully prevented" by input filtering.
- 1.2 Practitioners ship signature defenses (keyword blocklists, output filters). Are they useful? Against whom?
- 1.3 Contribution: reproducible ablation across two corpora, two adapter types, four defense profiles, with Wilson CIs.
- 1.4 The dual finding: signature defenses are brittle; model alignment is the dominant defense.
- 1.5 Roadmap: Section 2 related work, Section 3 threat model, Section 4 methodology, Section 5 results, Section 6 discussion, Section 7 limitations, Section 8 reproducibility.

---

## 2. Related Work (~600 words)

- 2.1 Prompt-injection taxonomy (direct, indirect, encoded; OWASP categories).
- 2.2 Defense families: input filtering, output filtering, authorization, alignment.
- 2.3 Public benchmarks: PINT, InjecAgent, AgentDojo, HarmBench — and why this project uses a small custom corpus (ablation, not leaderboard).
- 2.4 Adaptive attacks: the field's move from static benchmarks to adaptive pressure; why the mock's 0/23 was never a robustness claim.
- 2.5 Gap this project fills: comparative measurement of signature defenses against both a mock and a real model, with explicit acknowledgment of the model-alignment confounder.

---

## 3. Threat Model (~400 words)

Reference existing `report/threat_model.md`. Summarize:
- 3.1 Assets: synthetic customer records, system prompt, mock tool catalog.
- 3.2 Actors: authenticated analyst, support, admin (role-based).
- 3.3 Trust boundaries: user input, retrieved documents, model output, tool execution.
- 3.4 Assumptions: attacker cannot access the model's weights; attacker can craft arbitrary prompts.
- 3.5 Out of scope: model-weight extraction, third-party systems, real data.

---

## 4. Methodology (~800 words)

- 4.1 Architecture: four-layer pipeline (`input_validation`, `prompt_guard`, `output_filter`, `authz`) with toggleable defenses.
- 4.2 Adapters: `MockModel` (deterministic, over-compliant) and `GroqAdapter` (`openai/gpt-oss-20b`, temperature 0.0).
- 4.3 Corpora: 23 attacks + 5 benign each. Static (defense-naive) vs. adaptive (paraphrase + base64).
- 4.4 Verdict logic: encoding-aware judge (`test/judge.py`).
- 4.5 Metrics: ASR, FPR, Wilson 95% CI.
- 4.6 Reproducibility: committed artifacts, pinned Python version, deterministic mock.
- 4.7 Threats to validity (preview — full treatment in Section 7).

---

## 5. Results (~1000 words)

- 5.1 Mock — static corpus ablation (Table from `RESULTS.md` Part 1).
- 5.2 Mock — adaptive corpus ablation (Table from `RESULTS.md` Part 1).
- 5.3 The static-vs-adaptive gap (Figure 2 — slope chart). The headline mock finding.
- 5.4 Real model — both corpora (Table from `RESULTS.md` Part 2). All four profiles at 0/23.
- 5.5 The alignment finding (Figure 3 — mock-vs-real comparison). The headline real-model finding.
- 5.6 Determinism check — re-run stability of `prompt_guard` and `output_filter`.

### Figures needed for this section

- **Figure 1:** Ablation bar chart — mock model, both corpora, 6 profiles, ASR with CI whiskers.
- **Figure 2:** Slope chart — for each defense, static ASR → adaptive ASR (mock).
- **Figure 3:** Mock-vs-real comparison — same x-axis (defense profile), two series (mock, real), grouped bar chart.

---

## 6. Discussion (~600 words)

- 6.1 Signature defenses are necessary but not sufficient. Where they help (static leak, known payload) vs. where they fail (paraphrase, encoding).
- 6.2 The mock's over-compliance is not a flaw — it is the controlled substrate that makes defense ablation measurable. But it is also why mock-only ASR cannot be quoted as a robustness claim.
- 6.3 Alignment as defense: the finding a mock cannot produce. RLHF refusals happen before pipeline controls activate. This is a defense no amount of engineering replicates.
- 6.4 Practical recommendation: layer pipeline defenses (for when the model fails) *and* choose aligned models (for when it doesn't fail). Neither alone is sufficient.
- 6.5 The static-vs-adaptive gap as a reporting convention: any paper claiming a defense "works" should report both numbers.

---

## 7. Limitations (~500 words)

Copy and expand from `RESULTS.md` limitations. Emphasize:
- 7.1 Mock is a simulation. Not a model-behavior claim.
- 7.2 **Tool-call gap.** `GroqAdapter` does not pass `tools`, so tool-execution attacks were not measured against the real model. Adaptive corpus is unaffected (all text-leak). Static-corpus 0/23 is partially a measurement gap.
- 7.3 One real model. `openai/gpt-oss-20b`. Results may not generalize to other models, sizes, providers, or future versions.
- 7.4 Small n. Wilson CIs are wide (0.0–14.3% for 0/23). Ranking is the claim; point estimates are indicative.
- 7.5 Adaptive corpus targets known signatures. An attacker without corpus knowledge sees different numbers. This is the point, not a limitation.
- 7.6 No adaptive attacks against encoding (ROT13, hex, multi-turn, homoglyph).
- 7.7 Real-model non-determinism. Temperature 0.0 reduces but does not eliminate sampling variance; provider model updates can change behavior.

---

## 8. Reproducibility and Data Availability (~300 words)

- 8.1 Repository: `https://github.com/olufemiadeoye77/llm-security-defense-lab`
- 8.2 Every figure in this paper derives from a `results/run_*.json` file, all committed.
- 8.3 Commands to reproduce each table and figure.
- 8.4 Model version pinning: `openai/gpt-oss-20b` as of 2026-10-25. `llama-3.1-8b-instant` was retired 2026-08-16 during this project — an example of the version-instability problem in LLM research.
- 8.5 Zenodo DOI (to be added at release).

---

## 9. Conclusion (~200 words)

- 9.1 Restate the two findings in one sentence each.
- 9.2 The practical implication: report static and adaptive ASR; choose aligned models; layer defenses.
- 9.3 Future work: tool-call extraction, larger models, alignment-targeted attacks (jailbreak, multi-turn).

---

## References (target 15–25)

Must include:
- OWASP LLM Top 10 (2026) — LLM01 Prompt Injection
- At least 1 red-teaming survey / methodology paper
- PINT, InjecAgent, AgentDojo, HarmBench (or their paper equivalents)
- At least 2 recent defense papers (e.g. ARGUS, BrowseSafe++)
- Wilson (1927) — score interval (for the CI method)

---

## Writing plan

| Session | Sections | Word target |
|---|---|---|
| 1 | Abstract, 1, 2 | ~1300 |
| 2 | 3, 4, 5 | ~2200 |
| 3 | 6, 7, 8, 9 + references | ~1600 |
| 4 | Review pass, figures, release | — |

Total paper target: **~5000–6000 words**, standard for a workshop or short-conference submission.

---

## What's still unknown

- Whether to submit this somewhere (arXiv preprint, a workshop, a blog post) — decision after the paper is written.
- Whether to keep the `llama-3.1-8b-instant` retirement story in the paper. **Yes** — it illustrates the version-instability problem in LLM research and should be in Section 8.