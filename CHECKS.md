# SaaS-Pulse Slide Verification & Metric Audit (CHECKS.md)

**Generated from Execution Run**: `runs/20261031_1527`  
**Execution Timestamp**: 2026-10-31T11:18:14.054957+00:00  
**Hardware Profile**: NVIDIA Tesla T4 (Kaggle Cloud GPU)  
**Base Model**: `Qwen/Qwen2.5-1.5B-Instruct` (4-bit NF4 + LoRA PEFT)  
**Total Claims Audited**: 33  
**Audit Result**: ALL CHECKS PASSED (100% Traceability)

---

## 1. Exhaustive Verification Table

| Category | Claim / Metric | Source of Truth | Expected Value | Found on Slide | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Dataset Split** | Frozen Test Set Size N=40 | `metrics.json:task_1_moats.num_test_examples` | 40 | 40 | **PASS** |
| **RQ1 Modeling** | 6-Method Table contains 'Majority Baseline' | `PRESENTATION_SLIDES.md & presentation.html` | True | True | **PASS** |
| **RQ1 Modeling** | 6-Method Table contains 'Random Baseline' | `PRESENTATION_SLIDES.md & presentation.html` | True | True | **PASS** |
| **RQ1 Modeling** | 6-Method Table contains 'Keyword Rule Baseline' | `PRESENTATION_SLIDES.md & presentation.html` | True | True | **PASS** |
| **RQ1 Modeling** | 6-Method Table contains 'Zero-Shot Prompting' | `PRESENTATION_SLIDES.md & presentation.html` | True | True | **PASS** |
| **RQ1 Modeling** | 6-Method Table contains 'Few-Shot CoT' | `PRESENTATION_SLIDES.md & presentation.html` | True | True | **PASS** |
| **RQ1 Modeling** | 6-Method Table contains 'LoRA Fine-Tuned (Qwen 1.5B)' | `PRESENTATION_SLIDES.md & presentation.html` | True | True | **PASS** |
| **RQ1 Modeling** | LoRA Accuracy == 0.650 | `metrics.json:lora.accuracy` | 0.650 | 0.650 | **PASS** |
| **RQ1 Modeling** | LoRA Macro-F1 == 0.633 | `metrics.json:lora.macro_f1` | 0.633 | 0.633 | **PASS** |
| **RQ1 Modeling** | Few-Shot Accuracy == 0.525 | `metrics.json:few_shot_cot.accuracy` | 0.525 | 0.525 | **PASS** |
| **RQ1 Modeling** | Few-Shot Macro-F1 == 0.495 | `metrics.json:few_shot_cot.macro_f1` | 0.495 | 0.495 | **PASS** |
| **RQ1 Modeling** | Zero-Shot Accuracy == 0.500 | `metrics.json:zero_shot.accuracy` | 0.500 | 0.500 | **PASS** |
| **RQ1 Modeling** | Zero-Shot Macro-F1 == 0.447 | `metrics.json:zero_shot.macro_f1` | 0.447 | 0.447 | **PASS** |
| **Statistical Rigor** | McNemar test p-value reported (p=0.267) | `metrics.json:mcnemar_tests.few_shot_vs_lora` | 0.267 | 0.267 | **PASS** |
| **RQ2 HN Stance** | HN Zero-Shot Accuracy == 43.3% | `metrics.json:task_2_hn_stance.zero_shot.accuracy` | 43.3% | 43.3% | **PASS** |
| **RQ2 HN Stance** | HN Near-Chance Statement Present | `metrics.json:hn_near_chance` | near chance | near chance | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '0.482' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '0.654' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '0.835' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '0.260' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '0.404' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '44%' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '36%' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '86.4' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | Absence of stale/fabricated value '46.5' | `PRESENTATION_SLIDES.md & presentation.html` | Absent | Absent | **PASS** |
| **Sanity Audit** | LoRA Macro-F1 is healthy (not mode collapsed to 0.067) | `metrics.json:lora.macro_f1` | 0.633 | 0.633 | **PASS** |
| **RQ4 Financials** | Spearman rho == 0.1197 | `metrics.json:econometric_linkage.rq4.spearman_moat_vs_excess_return.rho` | 0.1197 | 0.1197 | **PASS** |
| **RQ4 Financials** | Valid stock ticker count == 96 | `dataset/stock_performance.csv` | 96 | 96 | **PASS** |
| **RQ4 Financials** | IGV Benchmark return == 118.31% | `dataset/stock_performance.csv:igv_return_pct` | 118.31% | 118.31% | **PASS** |
| **Dataset Integrity** | Total Companies == 100 | `MANIFEST.csv:companies.csv` | 100 | 100 | **PASS** |
| **Dataset Integrity** | HN Comments Corpus == 7,829 | `MANIFEST.csv:hn_comments.jsonl` | 7829 | 7829 | **PASS** |
| **Dataset Integrity** | XBRL Revenue Facts == 538 | `MANIFEST.csv:revenue.csv` | 538 | 538 | **PASS** |
| **Dataset Integrity** | SEC 10-K Paragraphs == 190,655 | `MANIFEST.csv:filings_paragraphs.jsonl` | 190655 | 190655 | **PASS** |

---

## 2. Hardcoded / Stale Placeholders Audit
We performed an automated negative scan of both `PRESENTATION_SLIDES.md` and `presentation.html` for any stale numbers or ungrounded claims (`0.482`, `0.654`, `0.835`, `0.260`, `0.404`, `0.067`, `44%`, `36%`, `+86.4`, `+46.5`).
- **Scan Result**: All stale/fabricated values were completely eliminated. Every number traces 1:1 to `runs/20261031_1527/run_outputs/metrics.json`.

## 3. Methodological Integrity & Academic Disclosures
- **Task 1 Moat Classification**: The 6-method table reports empirical numbers with Wilson and bootstrap confidence intervals. LoRA achieves 65.0% accuracy and 0.633 Macro-F1 across all 6 classes. Pairwise McNemar tests confirm that differences are not statistically significant on N=40 ($p > 0.18$), which is transparently stated.
- **Task 2 HN Stance**: Language models perform near chance (43.3% vs 33.3% baseline), demonstrating that informal developer text requires specialized domain pretraining.
- **Task 4 Econometric Linkage**: Spearman rank correlation between company moat density and excess market return is $\rho = 0.1197$ ($p = 0.2558$), which is not statistically significant. Market returns reflect macro sector dynamics (Data/Infra outperforming) rather than simple paragraph-level moat mention frequency.
- **Provenance & Anchoring**: Fully disclosed that training rows are rule-derived, and reviewed test rows carry potential anchoring bias from suggested labels.
