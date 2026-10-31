# SaaS-Pulse Live Status & Progress Tracker

**Repository**: [https://github.com/Eaterofsouls/saas-pulse](https://github.com/Eaterofsouls/saas-pulse)  
**Last Updated**: 2026-10-31 15:10:30 IST  
**Current Step**: RUNNING — Kernel Version 8 Active on Kaggle GPU  
**Kaggle Kernel URL**: [https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment](https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment)  
**Kaggle Dataset URL**: [https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset](https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset)

---

## 1. Current Execution Status: Run 8 (v2 Honest Re-Evaluation)
- **Phase**: RUNNING (`KernelWorkerStatus.RUNNING`).
- **Core Improvements in Version 8**:
  1. **Human Review Ingested**: `gold_review_completed.xlsx` ingested and audited (60 10-K, 60 HN rows). 100% agreement with keyword-rule filter confirmed; anchoring risk acknowledged.
  2. **Constrained Scoring**: Replaced unconstrained generation and brittle JSON parsing with teacher-forced, length-normalized log-prob scoring across all methods.
  3. **Completion-Only LoRA**: Applied `DataCollatorForCompletionOnlyLM` targeting `<|im_start|>assistant\n` to prevent mode collapse.
  4. **Sanity Gate**: Automatically aborts if any class receives >70% of test predictions.
  5. **RQ4 Econometric Moat Linkage**: Per-company moat scoring across 92 software companies and Spearman rank correlation with excess equity return vs. IGV.
- **Heartbeat Log**:
  - `2026-10-31 15:02 IST`: Human review spreadsheet `gold_review_sheet.xlsx` received in Downloads.
  - `2026-10-31 15:04 IST`: Review sheet copied to `dataset/review/gold_review_completed.xlsx`. Audit script executed: 60/60 agreement, Cohen's kappa 1.000, 0 exclusions. Full report written to `dataset/review/HUMAN_REVIEW_AUDIT.md`.
  - `2026-10-31 15:07 IST`: Provenance documents updated (`GOLD_PROVENANCE.md`, `GOLD_REVIEW.md`, `HN_STANCE_METHOD.md`, `FIX_LOG.md`). Staged, secret-checked, committed, and pushed to `main` (`a3330d0`).
  - `2026-10-31 15:09 IST`: Notebook generator v2 finalized with embedded review spreadsheet for standalone reliability.
  - `2026-10-31 15:10 IST`: [Heartbeat] Kernel Version 8 pushed to Kaggle. Status: `KernelWorkerStatus.RUNNING` on NVIDIA Tesla T4 GPU.

---

## 2. Milestone Audit

| Step | Milestone | Status | Details / Artifacts |
| :--- | :--- | :---: | :--- |
| **0** | **Human Review & Provenance** | **PASSED** | Review ingested; 100% agreement audited; anchoring acknowledged in `GOLD_PROVENANCE.md`. |
| **1** | **Constrained Log-Prob Scoring** | **READY** | Teacher-forced scoring + length normalization in v2 notebook. |
| **2** | **Completion-Only LoRA SFT** | **READY** | `DataCollatorForCompletionOnlyLM` with response template `<|im_start|>assistant\n`. |
| **3** | **Sanity Gate (>70% threshold)** | **READY** | Built into evaluation pipeline. |
| **4** | **HN Stance Constrained Eval** | **READY** | Constrained scoring for HN test (N=60) + 1500 corpus sample. |
| **5** | **RQ4 Moat-Score Equity Linkage** | **READY** | 92 companies * up to 30 paragraphs; Spearman vs excess returns. |
| **6** | **Kaggle T4 Execution (Run 8)** | **RUNNING** | Active on Tesla T4. |
| **7** | **Slide Verification & CHECKS.md** | **PENDING** | To be regenerated upon Run 8 completion. |

---

## 3. Run History & Failure Audits
1. **Run 1 (`runs/20261029_2322/`)**: Failed (`FileNotFoundError` path glob).
2. **Run 2 (`runs/20261029_2328/`)**: Failed (`AttributeError: shape` on `BatchEncoding`).
3. **Run 3 (`runs/20261029_2334/`)**: Failed (`TypeError: max_seq_length` in `SFTConfig`).
4. **Run 4 (`runs/20261029_2347/`)**: Failed (`ValueError: redundant peft_config` in `SFTTrainer`).
5. **Run 5 (`runs/20261029_2358/`)**: Failed (`NotImplementedError: GradScaler unscale on BFloat16` on Turing T4).
6. **Run 6 (`runs/20261030_0014/`)**: Failed (GradScaler unscale on BFloat16 during backprop).
7. **Run 7 (`runs/20261030_0023/`)**: Succeeded technically but mode-collapsed LoRA (`none_or_commodity`) and had audit flaws identified by reviewer.
8. **Run 8 (`running`)**: Version 8 executing on Tesla T4 with all 5 audit fixes applied.
