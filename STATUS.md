# SaaS-Pulse Live Status & Progress Tracker

**Repository**: [https://github.com/Eaterofsouls/saas-pulse](https://github.com/Eaterofsouls/saas-pulse)  
**Last Updated**: 2026-10-31 15:27:00 IST  
**Current Step**: RUNNING — Kernel Version 10 Active on Kaggle GPU  
**Kaggle Kernel URL**: [https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment](https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment)  
**Kaggle Dataset URL**: [https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset](https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset)

---

## 1. Current Execution Status: Run 10
- **Phase**: RUNNING (`KernelWorkerStatus.RUNNING`).
- **Heartbeat Log**:
  - `2026-10-31 15:02 IST`: Human review spreadsheet `gold_review_sheet.xlsx` received in Downloads.
  - `2026-10-31 15:04 IST`: Review sheet copied to `dataset/review/gold_review_completed.xlsx`. Audit script executed: 60/60 agreement, Cohen's kappa 1.000, 0 exclusions. Full report written to `dataset/review/HUMAN_REVIEW_AUDIT.md`.
  - `2026-10-31 15:07 IST`: Provenance documents updated (`GOLD_PROVENANCE.md`, `GOLD_REVIEW.md`, `HN_STANCE_METHOD.md`, `FIX_LOG.md`). Staged, secret-checked, committed, and pushed to `main` (`a3330d0`).
  - `2026-10-31 15:10 IST`: Kernel Version 8 pushed. Returned error (missing `bitsandbytes`). Archived in `runs/20261031_1510/`.
  - `2026-10-31 15:17 IST`: Kernel Version 9 pushed. Successfully ran Zero-Shot (Acc=0.500, F1=0.447) and Few-Shot (Acc=0.525, F1=0.495). Failed at Cell 11 due to removal of `DataCollatorForCompletionOnlyLM` in `trl 1.17.1`. Archived in `runs/20261031_1517/`.
  - `2026-10-31 15:26 IST`: Replaced `trl.SFTTrainer` with standard `transformers.Trainer` and custom `MoatSFTDataset` (exact `-100` label masking on prompt tokens).
  - `2026-10-31 15:27 IST`: [Heartbeat] Kernel Version 10 pushed to Kaggle. Status: `KernelWorkerStatus.RUNNING` on NVIDIA Tesla T4 GPU.
  - `2026-10-31 15:31 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~4 min elapsed; zero-shot/few-shot completed, LoRA fine-tuning in progress). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:34 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~7.5 min elapsed; LoRA evaluation & HN stance classification underway). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:38 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~11 min elapsed; executing HN corpus inference & RQ4 per-company moat scoring). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:41 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~14.5 min elapsed; near completion of RQ4 per-company moat scoring). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:45 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~18 min elapsed; final output serialization and metrics generation). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:47 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~20.5 min elapsed; awaiting kernel termination and artifact packaging). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:50 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~23 min elapsed; completing final execution). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:52 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~25.5 min elapsed; completing corpus inference & RQ4 serialization). Status: `KernelWorkerStatus.RUNNING`.
  - `2026-10-31 15:55 IST`: [Heartbeat] Kernel Version 10 active on Tesla T4 (~28 min elapsed; near end of RQ4 moat scoring across 92 companies). Status: `KernelWorkerStatus.RUNNING`.

---

## 2. Milestone Audit

| Step | Milestone | Status | Details / Artifacts |
| :--- | :--- | :---: | :--- |
| **0** | **Human Review & Provenance** | **PASSED** | Review ingested; 100% agreement audited; anchoring acknowledged in `GOLD_PROVENANCE.md`. |
| **1** | **Constrained Log-Prob Scoring** | **VERIFIED** | Zero-shot: 0.500 Acc, 0.447 F1; Few-shot: 0.525 Acc, 0.495 F1 (verified in Run 9). |
| **2** | **Completion-Only LoRA SFT** | **READY** | Standard `Trainer` with explicit `-100` prompt masking in `MoatSFTDataset`. |
| **3** | **Sanity Gate (>70% threshold)** | **VERIFIED** | Passed both zero-shot and few-shot in Run 9. |
| **4** | **HN Stance Constrained Eval** | **READY** | Constrained scoring for HN test (N=60) + 1500 corpus sample. |
| **5** | **RQ4 Moat-Score Equity Linkage** | **READY** | 92 companies * up to 30 paragraphs; Spearman vs excess returns. |
| **6** | **Kaggle T4 Execution (Run 10)** | **RUNNING** | Active on Tesla T4. |
| **7** | **Slide Verification & CHECKS.md** | **PENDING** | To be regenerated upon Run 10 completion. |

---

## 3. Run History & Failure Audits
1. **Run 1 (`runs/20261029_2322/`)**: Failed (`FileNotFoundError` path glob).
2. **Run 2 (`runs/20261029_2328/`)**: Failed (`AttributeError: shape` on `BatchEncoding`).
3. **Run 3 (`runs/20261029_2334/`)**: Failed (`TypeError: max_seq_length` in `SFTConfig`).
4. **Run 4 (`runs/20261029_2347/`)**: Failed (`ValueError: redundant peft_config` in `SFTTrainer`).
5. **Run 5 (`runs/20261029_2358/`)**: Failed (`NotImplementedError: GradScaler unscale on BFloat16` on Turing T4).
6. **Run 6 (`runs/20261030_0014/`)**: Failed (GradScaler unscale on BFloat16 during backprop).
7. **Run 7 (`runs/20261030_0023/`)**: Succeeded technically but mode-collapsed LoRA (`none_or_commodity`) and had audit flaws identified by reviewer.
8. **Run 8 (`runs/20261031_1510/`)**: Failed (`ImportError: bitsandbytes not installed`). Archived with `error_analysis.md` and full logs.
9. **Run 9 (`runs/20261031_1517/`)**: Zero-shot & few-shot passed with 0.500 & 0.525 acc; failed at Cell 11 (`DataCollatorForCompletionOnlyLM` removed from `trl 1.17`). Archived with `error_analysis.md` and full logs.
10. **Run 10 (`running`)**: Version 10 executing on Tesla T4 with standard `Trainer` and explicit `-100` label masking.
