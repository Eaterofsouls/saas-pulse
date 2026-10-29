# SaaS-Pulse Slide Verification & Metric Audit (CHECKS.md)

**Generated from Execution Run**: `20261030_0023`  
**Hardware Profile**: NVIDIA Tesla T4 (Kaggle Cloud GPU)  
**Base Model**: `Qwen/Qwen2.5-1.5B-Instruct` (4-bit NF4 + LoRA PEFT)  
**Total Claims Audited**: 18  
**Audit Result**: ALL CHECKS PASSED (100% Traceability)

---

## 1. Exhaustive Verification Table

| Category | Claim / Metric | Source of Truth | Expected Value | Found on Slide | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Dataset Split** | Frozen Test Set Size N=40 | `metrics.json:task_1_moats.num_test_examples` | 40 | 40 | **PASS** |
| **RQ1 Modeling** | Zero-Shot Accuracy == 0.325 | `metrics.json:zero_shot.accuracy` | 0.325 | 0.325 | **PASS** |
| **RQ1 Modeling** | Zero-Shot Macro-F1 == 0.260 | `metrics.json:zero_shot.macro_f1` | 0.260 | 0.260 | **PASS** |
| **RQ1 Modeling** | Few-Shot Accuracy == 0.425 | `metrics.json:few_shot_cot.accuracy` | 0.425 | 0.425 | **PASS** |
| **RQ1 Modeling** | Few-Shot Macro-F1 == 0.404 | `metrics.json:few_shot_cot.macro_f1` | 0.404 | 0.404 | **PASS** |
| **RQ1 Modeling** | LoRA Accuracy == 0.250 | `metrics.json:lora.accuracy` | 0.250 | 0.250 | **PASS** |
| **RQ1 Modeling** | LoRA Macro-F1 == 0.067 | `metrics.json:lora.macro_f1` | 0.067 | 0.067 | **PASS** |
| **RQ1 Modeling** | Few-Shot gain over Zero-Shot == +14.4 pp | `(0.404 - 0.260)*100` | +14.4 | +14.4 | **PASS** |
| **Sanity Audit** | Absence of old unverified placeholder 0.482 | `PRESENTATION_SLIDES.md` | False | False | **PASS** |
| **Sanity Audit** | Absence of old unverified placeholder 0.654 | `PRESENTATION_SLIDES.md` | False | False | **PASS** |
| **Sanity Audit** | Absence of old unverified placeholder 0.835 | `PRESENTATION_SLIDES.md` | False | False | **PASS** |
| **RQ3 Financials** | Valid stock ticker count == 96 | `dataset/stock_performance.csv` | 96 | 96 | **PASS** |
| **RQ3 Financials** | IGV Benchmark return == 118.31% | `dataset/stock_performance.csv:igv_return_pct` | 118.31% | 118.31% | **PASS** |
| **RQ3 Financials** | Spearman rho == 0.351 | `metrics.json:econometric_linkage.spearman_rho_growth_vs_excess_return` | 0.351 | 0.351 | **PASS** |
| **Dataset Integrity** | Total Companies == 100 | `MANIFEST.csv:companies.csv` | 100 | 100 | **PASS** |
| **Dataset Integrity** | HN Comments Corpus == 7,829 | `MANIFEST.csv:hn_comments.jsonl` | 7829 | 7829 | **PASS** |
| **Dataset Integrity** | XBRL Revenue Facts == 538 | `MANIFEST.csv:revenue.csv` | 538 | 538 | **PASS** |
| **Dataset Integrity** | SEC 10-K Paragraphs == 190,655 | `MANIFEST.csv:filings_paragraphs.jsonl` | 190655 | 190655 | **PASS** |

---

## 2. Hardcoded Placeholders Check
We scanned `PRESENTATION_SLIDES.md` and `presentation.html` for any legacy draft placeholders (`0.482`, `0.654`, `0.835`).
- Any occurrences detected: None - all metrics trace 100% to live execution.

## 3. Discrepancy & Resolution Summary
- All empirical numbers in the presentation were dynamically extracted and synchronized from `metrics.json` via `update_slides_from_metrics.py`.
- No synthetic or hardcoded metrics exist.
