# 07 — AI Authenticity & AI Engineering Audit

> **Current-state addendum:** Replace “OpenAI” in the baseline with **Google Gemini**. The genuine 23-tool, ORM-grounded, confirmation-gated architecture remains. Tenant isolation, real customer chat wiring, stable/configurable model selection, and quota fallbacks are covered. Live customer/admin paths now record privacy-redacted interaction/tool metrics. `evaluate_no_show_model()` adds deterministic holdout precision, recall, F1, Brier, calibration error, and explicit real/synthetic provenance; the current synthetic result is published at `docs/ai/no-show-evaluation.md`. Current AI score is **10.75/12**. Deductions remain for synthetic data/cancellation-as-no-show labeling, absent prompt-injection/tool-abuse behavioral evals, and no persisted admin conversation history.

This is the most important section for a developer positioning as an AI/Full-Stack Developer, so the standard applied here is strict: every README AI claim was checked against actual code, not accepted at face value.

## Claim-by-claim verdict

| README claim | Verdict | Key evidence |
|---|---|---|
| OpenAI function calling, multi-turn | **Genuine and functional** | `apps/ai/copilot.py:73-75` real `OpenAI()` client; `:177-179` real `chat.completions.create(tools=..., tool_choice="auto")`; bounded multi-round loop (`MAX_TOOL_ROUNDS=8`) |
| 23 registered tools | **Genuine and functional** | `apps/ai/tools.py:1033-1373` — exact count verified in code and locked in by `tests/test_ai.py::test_tool_count`; every tool executes a real Django ORM query, none are stubs |
| Booking draft confirmation-gated workflow | **Genuine and functional, code-enforced** | `create_booking_draft` only ever writes a `BookingDraft` row (`tools.py:280-290`); the only path to a real `Appointment` is a separate, explicit `confirm_booking_draft` tool call (`tools.py:348-394`) with 15-minute expiry — this is a real two-phase commit, not just a prompt instruction |
| Conversation persistence with history | **Genuine for the customer copilot; missing for the admin copilot** | Real `Conversation`/`Message` models (`apps/ai/models.py:8-54`), persisted every turn (`copilot.py:81-101`). `admin_chat()` uses an in-memory list only and never persists — a real gap in the README's blanket claim |
| Rate-limited (30/hr customer, 60/hr admin) | **Genuine and functional** | Real DRF `UserRateThrottle` subclasses (`apps/ai/views.py:11-13,46-48`) matching `DEFAULT_THROTTLE_RATES` in settings exactly |
| Service recommendation, hybrid weighted scoring | **Genuine and functional** | `apps/ai/recommender.py` — five real signals (history, rating, availability, popularity, recency) computed from live DB queries, combined via literal weighted sum with configurable weights; guest fallback verified (non-personalized ranking when no `customer_id`) |
| No-show prediction, XGBoost + SHAP | **Genuine implementation, structurally weak in realistic use** | Real `xgb.XGBClassifier` trained on-demand (no saved model artifact — the code's own docstring calls this out). **Falls back to 1,000 synthetic samples whenever real appointment rows < 30**, which is the norm for demo-seeded data (~36–72 appointments). SHAP (`shap.TreeExplainer`) genuinely computes per-prediction explanations. Uses `status == "cancelled"` as a no-show label proxy, which is semantically questionable. **No precision/recall/calibration evaluation exists anywhere in the test suite** — only structural smoke tests (feature-vector length, probability bounds). |
| Revenue forecasting, exponential smoothing | **Genuine and functional** | `apps/ai/revenue_forecast.py:64-107` — a real, correctly-structured hand-rolled exponential smoothing with trend estimation and widening 95%-style confidence intervals; not a fake trend line. Not built on `statsmodels`, so it's a manual reimplementation rather than a library, worth noting for rigor but not a false claim. |
| Evaluation framework, 11 test cases | **Genuine but narrow** | `apps/ai/evaluation.py:40-108` — exactly 11 `EvalCase` entries, real pass/fail harness for tool-selection/parameter-matching. Does **not** evaluate response content quality, hallucination, or safety, and is not shown wired to a live OpenAI call in CI — it's a tool-selection regression harness, not a full behavioral eval suite. |
| Embeddings / RAG / vector DB | **Correctly absent** — not claimed, not present | Confirmed via repo-wide search; no false credit taken |

## Additional findings not directly claimed by the README

- **Observability module is fully built and unit-tested but never invoked in the live request path.** `apps/ai/observability.py` (`MetricsCollector`, `log_tool_call`, `timed` decorator) has real tests but is never imported by `copilot.py` or `admin_copilot.py` — a complete, dead subsystem. Any marketing claim of "AI observability" would currently be inaccurate in production.
- **No prompt-injection protection or LLM-output validation layer.** The only defense against the model inventing data or acting outside its role is the system prompt plus the structural fact that the LLM can only call registered, schema-typed tool functions. There is no explicit input sanitization, moderation-endpoint usage, or output-schema validation before a tool result is used to take a DB-writing action.
- **Cross-tenant data leak via the admin copilot** — see `04-backend-audit.md` and `06-testing-security-performance.md` (Admin AI Copilot always analyzes the first active business in the DB, not the requesting admin's business, because `user=None` is hardcoded in `admin_chat()`). This is the single most damaging AI-related finding: a genuinely well-built feature undermined by one authorization bug.

## AI authenticity score: 8.5 / 12

Justification: the large majority of the AI surface — copilot architecture, tool registry, draft/confirm safety mechanism, recommender, forecaster — is real, working, non-trivial engineering, clearly above "API wrapper" or "rule-based dressed up as AI." Points are deducted for: the no-show model's practical dependence on synthetic training data at realistic demo data volumes with zero predictive-quality evaluation; the cross-tenant data leak in the admin copilot; the unwired observability layer; and the absence of any prompt-injection/output-validation guardrail given the copilot can trigger real database writes.

## Recommendation: strongest realistic AI feature set for this portfolio

Given what already exists, the highest-leverage next steps are **not** new features but hardening what's built:

1. **Fix the admin copilot's business-scoping bug** (pass `request.user` through) — this single fix removes the most credibility-damaging AI finding in the whole audit and should happen before any new AI feature work.
2. **Add a real evaluation report for the no-show model** — precision/recall/calibration on a held-out split, explicitly documenting the synthetic-data fallback and its limitations. This is cheap (the pipeline already exists) and directly answers the audit brief's demand for "precision, recall, calibration, and business-threshold evaluation."
3. **Wire the existing observability module into the live request path** — it's already built and tested; connecting `log_tool_call`/`MetricsCollector` to `copilot.py`/`admin_copilot.py` is a small, high-credibility change ("AI observability" becomes a true claim).
4. Do **not** add a fourth or fifth AI capability (e.g., customer segmentation, campaign recommendation) before the above three — more surface area without fixing the existing authorization bug and missing evaluation would weaken, not strengthen, the portfolio's credibility under scrutiny.

This keeps the AI story focused on two genuinely strong, demonstrable capabilities (the booking copilot with its confirmation-gated safety design, and the recommendation/forecasting analytics pair) rather than diluting it across more features.
