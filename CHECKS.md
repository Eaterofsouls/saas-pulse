# Number Sources (CHECKS.md)

## Number sources

| Claim | Value | Source |
|---|---|---|
| Test set size | 35 | `metrics.json task_1_moats.methods.lora.n` |
| Companies | 100 | `MANIFEST.csv companies.csv` |
| 10-K filings indexed | 464 | `MANIFEST.csv filings_index.csv` |
| 10-K paragraphs | 190655 | `MANIFEST.csv filings_paragraphs.jsonl` |
| Revenue rows | 538 | `MANIFEST.csv revenue.csv` |
| HN items | 7829 | `MANIFEST.csv hn_comments.jsonl` |
| Pricing-page records | 147 | `MANIFEST.csv pricing_pages.jsonl` |
| Tickers with prices | 96 | `stock_performance.csv status==ok` |
| IGV return % | 118.31 | `stock_performance.csv igv_return_pct` |
| Train rows | 140 | `gold_10k_moats.csv split==train` |
| Review rows evaluated | 52 | `runs/20261102_2144\gold_review_completed.xlsx` |
| Review rows excluded | 8 | `runs/20261102_2144\gold_review_completed.xlsx` |
| Rule-vs-review agreement | 65.4% | `runs/20261102_2144\gold_review_completed.xlsx` |
| Cohen's kappa rule vs review | 0.574 | `runs/20261102_2144\gold_review_completed.xlsx (computed)` |
| Test rows where final label = rule label | 23 | `predictions.csv + review file` |
| Majority class accuracy | 0.457 | `metrics.json task_1_moats.methods.majority_baseline.accuracy` |
| Majority class macro-F1 | 0.105 | `metrics.json task_1_moats.methods.majority_baseline.macro_f1` |
| Random accuracy | 0.143 | `metrics.json task_1_moats.methods.random_baseline.accuracy` |
| Random macro-F1 | 0.122 | `metrics.json task_1_moats.methods.random_baseline.macro_f1` |
| Keyword rule* accuracy | 0.657 | `metrics.json task_1_moats.methods.keyword_rule_baseline.accuracy` |
| Keyword rule* macro-F1 | 0.667 | `metrics.json task_1_moats.methods.keyword_rule_baseline.macro_f1` |
| Zero-shot (Qwen 1.5B) accuracy | 0.371 | `metrics.json task_1_moats.methods.zero_shot.accuracy` |
| Zero-shot (Qwen 1.5B) macro-F1 | 0.305 | `metrics.json task_1_moats.methods.zero_shot.macro_f1` |
| Few-shot, 6 examples accuracy | 0.343 | `metrics.json task_1_moats.methods.few_shot_cot.accuracy` |
| Few-shot, 6 examples macro-F1 | 0.307 | `metrics.json task_1_moats.methods.few_shot_cot.macro_f1` |
| LoRA fine-tuned accuracy | 0.600 | `metrics.json task_1_moats.methods.lora.accuracy` |
| LoRA fine-tuned macro-F1 | 0.589 | `metrics.json task_1_moats.methods.lora.macro_f1` |
| Spearman moat vs excess return | 0.184 | `rq4_correlations.json` |
| Spearman p | 0.079 | `rq4_correlations.json` |
| Spearman n | 92 | `rq4_correlations.json` |
| Spearman moat vs revenue growth | -0.022 | `rq4_correlations.json` |
| HN zero-shot accuracy | 0.433 | `metrics.json task_2_hn_stance.zero_shot` |
| HN few-shot accuracy | 0.433 | `metrics.json task_2_hn_stance.few_shot` |
| LoRA epochs | 4.0 | `training_loss.csv epoch max` |
