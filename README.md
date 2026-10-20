# LLM Security Defense Lab
**Capstone:** LLM Security: Vulnerabilities and Defense Patterns — Applied AI Engineering Specialization

## Purpose
A controlled, synthetic-data lab for assessing an LLM-powered enterprise assistant before and after defense-in-depth controls. The project compares API-based, locally hosted, and multi-model pipeline patterns.

## Safety boundaries
- Use only synthetic records and systems you own or are explicitly authorized to test.
- The included tools and actions are mock examples; do not connect them to real email, payments, customer systems, or production data.
- Never commit API keys, access tokens, real customer data, or private prompts.
- Do not use this lab to extract proprietary model weights or attack third-party services.

## Initial repository contents
- `reports/threat_model.md` — scope, assets, actors, trust boundaries, assumptions, and risk priorities.
- `data/synthetic_records.json` — invented customer records with access classifications.
- `data/synthetic_documents.json` — benign and adversarially-instructed mock documents for indirect-injection tests.
- `data/security_test_cases.json` — starter test cases across the six required vulnerability categories.
- `data/test_users.json` — invented users and access roles.
- `data/mock_tool_catalog.json` — harmless mock tools and their permission boundaries.
- `reports/risk_register.csv` — initial risk register to update with observed evidence.
- `tests/README.md` — testing and measurement plan.

## Suggested build order
1. Review the threat model and synthetic dataset.
2. Implement a deliberately vulnerable local demo app using only mock data and mock tools.
3. Run baseline tests and record results.
4. Add defenses and rerun the exact same test cases.
5. Add API and local model adapters; keep secrets in environment variables.
6. Orchestrate repeatable tests with n8n.
7. Compare API, local, and multi-model results; document residual risks.
8. Publish the final report with measured results and limitations.

## Metrics
- Attack success rate (ASR) = successful attack tests / total attack tests × 100%.
- Defense block rate = blocked attack attempts / total attack attempts × 100%.
- False positive rate = legitimate tests incorrectly blocked / total legitimate tests × 100%.
- Report counts and denominators, not percentages alone. For small test sets, percentages are indicative rather than statistically conclusive.

## Create your GitHub repository
Create a **public** repository named `llm-security-defense-lab` only if you are comfortable publishing all included files. Review the dataset and remove anything you do not want public.
Then upload this folder or push it with Git:
```bash
git init
git add .
git commit -m "Initialize LLM security defense lab"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/llm-security-defense-lab.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. If using a connected GitHub integration, authorize it first and confirm the target repository before publishing.

## Status
Planning assets and synthetic data only. No application has been implemented or tested yet; do not report vulnerability results until tests are run.
