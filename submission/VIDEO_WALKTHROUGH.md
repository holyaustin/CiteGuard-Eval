# 5-minute walkthrough script

**0:00–0:35 — Problem**
Academic references can look credible while containing wrong metadata, and a real source can be attached to a claim it does not support. CiteGuard-Eval tests both capabilities separately.

**0:35–1:15 — Benchmark design**
Show `citeguard/data/tasks.json`. Explain the ten controlled tasks: metadata mismatches, DOI errors, missing DOI, direct support, contradiction, causality, partial support and combined reasoning. Clarify that fixtures are synthetic so every gold label is auditable.

**1:15–2:00 — Run the tests**
Run `python -m unittest discover -s tests -v`. Explain that the grader is deterministic and does not ask another language model to judge the answer.

**2:00–3:00 — Run a model**
Show environment variables and `python citeguard/run_model.py`. Explain that the runner uses an OpenAI-compatible API and never sends the gold answer to the model.

**3:00–4:10 — Inspect grading**
Run `python citeguard/grade.py`. Open `citeguard/results/graded_results.json` and show task-level criteria, not just the aggregate score. Point out the distinction between an incorrect DOI and an unsupported research claim.

**4:10–5:00 — Findings and limitations**
Present only actual model results generated during the run. Identify the exact task-level failures. State that this pilot uses synthetic fixtures and does not claim to test live DOI registration. Explain how real registry-backed tasks and a larger independently reviewed set would extend it.
