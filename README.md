# LLM Security Defense Lab

A controlled, reproducible lab for measuring prompt-injection defenses on an LLM-powered enterprise assistant — before and after defense-in-depth controls, against both a deterministic mock and a real RLHF-aligned model.

## Headline findings

1. **Signature defenses collapse under adaptive attack.** A 7-phrase keyword blocklist scored 34.8% ASR on a defense-naive corpus and **100%** on an adaptive corpus that paraphrases the same 23 attacks. An output filter scoring 0% on the static corpus scored **30.4%** on base64-encoded leaks.
2. **Model alignment is the strongest single defense.** An RLHF-aligned real model (`openai/gpt-oss-20b` via Groq) refused **23/23** attacks on both corpora at baseline, before any pipeline control activated. This defense is not replicable in code and not measurable with a mock.

Full results, tables, and limitations: **[`RESULTS.md`](RESULTS.md)**

## Why this exists

Prompt injection is [#1 in the OWASP LLM Top 10 (2026)](https://genai.owasp.org/), and the same document notes that injection "cannot be fully prevented" by input filtering. This lab measures **how much** a signature-based defense helps — and **when it stops helping** — with reproducible numbers, confidence intervals, and archived run artifacts.

## Structure

| Directory | Purpose |
|---|---|
| `app/` | Pipeline: input validation -> prompt_guard -> model -> output_filter -> authz -> mock tool |
| `app/model_adapter.py` | Uniform interface for `MockModel` (offline) and `GroqAdapter` (real API) |
| `data/` | Synthetic records + two attack corpora (defense-naive, defense-aware) |
| `test/harness.py` | Runs a corpus at a given defense profile; saves `results/run_*.json` |
| `test/judge.py` | Verdict logic (encoding-aware) |
| `test/stats.py` | Wilson 95% confidence intervals |
| `report/` | Threat model and (Stage 5) paper draft |
| `results/` | Every run, as JSON, committed for reproducibility |

## Reproduce

Mock model — no API key, no network, fully deterministic:

    python -m test.harness --adapter mock --corpus static   --defenses none         --save
    python -m test.harness --adapter mock --corpus adaptive --defenses prompt_guard --save

Real model (optional) — requires a Groq API key:

1. Sign up free at https://console.groq.com
2. Create API key
3. Create `.env` in repo root with `GROQ_API_KEY=gsk_...`

    python -m test.harness --adapter groq --corpus adaptive --defenses all_plus_output --save

Verified on **Windows 11**, **Python 3.14.8**. `.env` is git-ignored; never commit real credentials.

## Safety boundaries

- Only synthetic records, synthetic documents, and mock tools. No real email, payment, customer, or production systems.
- Mock tools are non-functional placeholders. `execute_mock_tool` is the only executor.
- No attempt at model-weight extraction. The project measures prompt-level defenses only.

## Limitations (short version — full list in [`RESULTS.md`](RESULTS.md))

- `MockModel` is a deliberately over-compliant simulation, not a real LLM. It provides a controlled attack surface for ablation, not a model-behavior claim.
- The Groq adapter does not yet pass `tools` to the API, so tool-execution attacks are measured against the mock only. This is the primary limitation and the top item on future work.
- Corpora are small (n=23 attacks, n=5 benign controls each). Wilson CIs are wide; the ranking is the defensible claim, not the point estimate.

## Author

Olufemi Adeoye — [github.com/olufemiadeoye77](https://github.com/olufemiadeoye77)

Project built as a self-directed research exercise in LLM security engineering. Feedback welcome via Issues.