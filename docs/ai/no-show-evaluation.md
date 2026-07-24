# No-Show Model Evaluation

Evaluation date: 2026-07-24

Command:

```powershell
python manage.py shell -c "from dataclasses import asdict; from apps.ai.no_show import evaluate_no_show_model; print(asdict(evaluate_no_show_model()))"
```

## Holdout result

| Metric | Value |
|---|---:|
| Data provenance | **Synthetic** |
| Training samples | 800 |
| Test samples | 200 |
| Positive rate | 0.4850 |
| Classification threshold | 0.5000 |
| Precision | 0.4773 |
| Recall | 0.6495 |
| F1 score | 0.5502 |
| Brier score | 0.2735 |
| Expected calibration error | 0.1321 |

## Interpretation and limitations

These numbers are **not production-performance claims**. The demo database does not contain at least 100 labeled appointments across both classes, so `evaluate_no_show_model()` explicitly reports `data_source="synthetic"` and evaluates a deterministic synthetic holdout.

The current label also uses cancellation as a proxy for no-show. Cancellation and no-show are operationally different outcomes, so a real deployment should add an explicit attendance outcome before training or presenting business metrics.

At the default threshold, recall is higher than precision: the model catches more synthetic high-risk cases but produces many false positives. It must not trigger punitive or customer-visible actions. Appropriate use is a low-stakes reminder recommendation with human oversight.

Before production use:

1. Collect consent-appropriate, business-scoped attendance outcomes.
2. Train and evaluate on temporally separated real data.
3. Report confidence intervals, per-business performance, calibration plots, and threshold cost analysis.
4. Monitor drift and false-positive impact.
5. Retrain only after the minimum real-data and class-balance requirements are met.
