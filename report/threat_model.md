# Threat Model — LLM Security Defense Lab

## 1. System overview
A fictional enterprise assistant accepts user prompts, retrieves synthetic documents, consults synthetic records, and may request mock tool actions. The lab compares:
1. API-based model: prompt and permitted context are sent to a model provider.
2. Local/embedded model: inference runs on a controlled local host.
3. Multi-model pipeline: model A summarizes or classifies input and model B answers or requests a tool action.

The system is a teaching environment, not a production design.

## 2. Security objectives
- Confidentiality: users receive only data they are authorized to access.
- Integrity: untrusted instructions and model outputs cannot silently alter privileged policy or trigger unauthorized actions.
- Availability: abusive query patterns do not exhaust test resources.
- Accountability: test runs and mock tool decisions are logged without storing secrets unnecessarily.
- Least privilege: each component receives only the data and tool permissions required for its task.

## 3. Assets
| Asset | Classification | Security objective |
|---|---|---|
| Synthetic customer records | Confidential (synthetic) | Enforce user-level access |
| Mock system instructions | Internal | Avoid unintended disclosure; do not rely on secrecy as the only control |
| Model/provider credentials | Secret (must not be in repo) | Keep out of prompts, logs, and source control |
| Mock tool actions | Restricted capability | Enforce server-side authorization |
| Test results and audit logs | Internal | Preserve integrity and minimize sensitive content |
| Model configuration and outputs | Internal | Protect configuration; monitor extraction-like query behavior |

## 4. Threat actors
- Malicious or curious user attempting to override policy or access other users' records.
- Author of a retrieved document containing adversarial instructions.
- Abusive client submitting repeated or crafted queries.
- Misconfigured application developer who trusts model output as policy.
- Compromised or overprivileged tool integration.
- Attacker exploiting trust between chained models.

## 5. Trust boundaries
1. User/browser → application API.
2. User-supplied or retrieved text → model prompt/context.
3. Model output → parser, renderer, or downstream model.
4. Model tool request → server-side authorization layer → mock tool.
5. Application → external model provider (API architecture).
6. Model A output → Model B input (multi-model architecture).
7. Application logs → stored test evidence.

Treat user input, retrieved documents, model output, and inter-model messages as untrusted until validated. Prompt wording alone is not an authorization boundary.

## 6. In-scope vulnerability categories and hypotheses
| ID | Category | Test hypothesis | Primary defense |
|---|---|---|---|
| LLM-01 | Direct prompt injection | User instructions can conflict with app policy | Separate instructions/data; policy checks; adversarial tests |
| LLM-02 | Indirect prompt injection | Retrieved document may contain instructions aimed at the model | Mark retrieved text untrusted; isolate context; constrain downstream actions |
| LLM-03 | Insecure output handling | Model output may be treated as executable or trusted structured data | Strict schema validation, context-aware escaping, sandboxing |
| LLM-04 | Model extraction/theft | Repeated queries may expose protected behavior or protected synthetic content | Authentication, rate limits, monitoring, output controls; recognize that output perturbation is not a complete defense |
| LLM-05 | Sensitive information disclosure | A user may obtain records outside their authorization | Server-side authorization, data minimization, classification, redaction |
| LLM-06 | Insecure plugin/tool design | Tool calls may bypass permissions or accept unsafe arguments | Allowlisted tools, typed arguments, server-side authorization, least privilege |
| LLM-07 | Excessive agency | A model may cause a consequential action without approval | Read-only defaults, explicit approvals, action limits, reversible mock actions |

The assignment requires at least six categories; LLM-01 through LLM-07 provide seven test tracks.

## 7. Out of scope
- Testing systems without explicit authorization.
- Attacking public model endpoints or third-party accounts.
- Extracting real model weights, private training data, or production secrets.
- Executing untrusted generated code on the host.
- Real email sending, payments, account changes, or destructive tool actions.
- Claims of universal security based on a small demonstration dataset.

## 8. Assumptions and limitations
- All names, identifiers, account balances, and documents in `data/` are fictional.
- The local model and API provider may behave differently across model versions and settings.
- A successful or failed test is specific to the configuration, test prompt, model version, and date.
- Synthetic canary strings demonstrate detection of disclosure; they do not prove that a real model's weights or training data are protected.
- Rate limiting reduces abuse but does not independently prevent model extraction.
- Prompt injection cannot be reliably solved by input sanitization alone. Authorization must be enforced outside the model.

## 9. Initial risk priorities
1. Critical/High: unauthorized data access and unauthorized tool actions.
2. High: direct/indirect prompt injection that changes decisions or crosses a trust boundary.
3. High: unsafe output consumed by parsers, renderers, or tools.
4. Medium/High: sensitive data leakage and repeated-query abuse.
5. Medium: model configuration disclosure and extraction-like behavior, depending on exposure and impact.

These are preliminary priorities, not final findings. Final severity must be based on observed impact, likelihood, and evidence.

## 10. Evidence required for each finding
- Finding ID and vulnerability category.
- Exact test case ID, model/configuration, date, and run count.
- Expected safe behavior and observed behavior.
- Reproducible evidence with synthetic data only.
- Root cause and affected trust boundary.
- Baseline result and post-defense result.
- Residual risk, false positives, and limitations.
- Severity, remediation owner, and priority.

## 11. Success criteria
- At least six categories tested with documented root cause.
- The same attack cases run before and after controls.
- Attack success rate, defense block rate, and false positive rate reported with denominators.
- API, local, and multi-model configurations compared where technically available.
- Final report separates measured evidence from assumptions and proposed controls.
