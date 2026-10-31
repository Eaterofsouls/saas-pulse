# SaaS-Pulse Live Status & Progress Tracker

**Repository**: [https://github.com/Eaterofsouls/saas-pulse](https://github.com/Eaterofsouls/saas-pulse)  
**Last Updated**: 2026-10-31 16:58:00 IST  
**Current Step**: COMPLETE — Kaggle Run 10 Fully Executed, Downloaded, Synchronized & Verified  
**Kaggle Kernel URL**: [https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment](https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment)  
**Kaggle Dataset URL**: [https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset](https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset)

---

## 1. Current Execution Status: Run 10 (COMPLETE)
- **Status**: `KernelWorkerStatus.COMPLETE` on Kaggle Tesla T4 GPU.
- **Output Archive**: `runs/20261031_1527/` (all metrics, predictions, confusion matrices, loss curves, and logs).
- **Audit Verification**: `CHECKS.md` passes **33 / 33 checks (100% Traceability)**.

### Heartbeat & Milestone Log:
- `2026-10-31 15:02 IST`: Human review spreadsheet `gold_review_sheet.xlsx` received in Downloads.
- `2026-10-31 15:04 IST`: Review sheet copied to `dataset/review/gold_review_completed.xlsx`. Audit executed: 60/60 agreement, Cohen's kappa 1.000, 0 exclusions. Full report written to `dataset/review/HUMAN_REVIEW_AUDIT.md`.
- `2026-10-31 15:07 IST`: Provenance documents updated (`GOLD_PROVENANCE.md`, `GOLD_REVIEW.md`, `HN_STANCE_METHOD.md`, `FIX_LOG.md`). Staged, secret-checked, committed, and pushed to `main`.
- `2026-10-31 15:10 IST`: Kernel Version 8 pushed. Returned error (missing `bitsandbytes`). Archived in `runs/20261031_1510/`.
- `2026-10-31 15:17 IST`: Kernel Version 9 pushed. Successfully ran Zero-Shot (Acc=0.500, F1=0.447) and Few-Shot (Acc=0.525, F1=0.495). Failed at Cell 11 due to removal of `DataCollatorForCompletionOnlyLM` in `trl 1.17.1`. Archived in `runs/20261031_1517/`.
- `2026-10-31 15:26 IST`: Replaced `trl.SFTTrainer` with standard `transformers.Trainer` and custom `MoatSFTDataset` (exact `-100` label masking on prompt tokens).
- `2026-10-31 15:27 IST`: Kernel Version 10 pushed to Kaggle. Status: `KernelWorkerStatus.RUNNING` on NVIDIA Tesla T4 GPU.
- `2026-10-31 16:48 IST`: Kernel completed successfully (`KernelWorkerStatus.COMPLETE`).
- `2026-10-31 16:50 IST`: All run outputs downloaded to `runs/20261031_1527/`.
- `2026-10-31 16:56 IST`: Presentation slides (`PRESENTATION_SLIDES.md`, `presentation.html`) updated with 6-method table, exact empirical metrics, and honest disclosures. `CHECKS.md` regenerated (33/33 checks PASS).

---

## 2. Milestone Audit

| Step | Milestone | Status | Details / Artifacts |
| :--- | :--- | :---: | :--- |
| **0** | **Human Review & Provenance** | **PASSED** | Review ingested; 100% agreement audited; anchoring acknowledged in `GOLD_PROVENANCE.md`. |
| **1** | **Constrained Log-Prob Scoring** | **PASSED** | Teacher-forced scoring eliminated mode collapse across all methods. |
| **2** | **Completion-Only LoRA SFT** | **PASSED** | Custom `MoatSFTDataset` + PyTorch `-100` masking trained cleanly for 72 steps without collapse. |
| **3** | **Sanity Gate (>70% threshold)** | **PASSED** | All modeling methods passed sanity gate (balanced prediction distributions). |
| **4** | **HN Stance Constrained Eval** | **PASSED** | Constrained scoring evaluated on N=60 gold + 1500 corpus sample; near chance reported. |
| **5** | **RQ4 Moat-Score Equity Linkage** | **PASSED** | 92 companies scored; Spearman rank correlation calculated ($\rho = 0.1197, p = 0.2558$). |
| **6** | **Kaggle T4 Execution (Run 10)** | **PASSED** | Complete run archived in `runs/20261031_1527/`. |
| **7** | **Slide Verification & CHECKS.md** | **PASSED** | 33 / 33 verification checks passed; all stale/fabricated claims eliminated. |

---

## 3. Empirical Results Summary (Run 10)

### Task 1: Moat Classification (Frozen Test Set, $N=40$)
- **Majority Baseline**: Acc = 0.250 [0.142, 0.402], Macro-F1 = 0.067 [0.037, 0.095]
- **Random Baseline**: Acc = 0.200 [0.105, 0.348], Macro-F1 = 0.194 [0.085, 0.302]
- **Keyword Rule Baseline**: Acc = 1.000, Macro-F1 = 1.000 (Identity by construction; rule generation baseline)
- **Zero-Shot Prompting**: Acc = 0.500 [0.352, 0.648], Macro-F1 = 0.447 [0.306, 0.554]
- **Few-Shot CoT**: Acc = 0.525 [0.375, 0.671], Macro-F1 = 0.495 [0.329, 0.621]
- **LoRA Fine-Tuned (Qwen 1.5B)**: **Acc = 0.650 [0.495, 0.779]**, **Macro-F1 = 0.633 [0.475, 0.768]**
- **McNemar Tests**: LoRA vs Few-Shot $p = 0.267$; LoRA vs Zero-Shot $p = 0.181$ (not statistically significant on $N=40$).

### Task 2: Developer Stance on Hacker News ($N=60$ Benchmark)
- **Zero-Shot**: Acc = 0.433 [0.316, 0.559], Macro-F1 = 0.411 [0.286, 0.533]
- **Few-Shot**: Acc = 0.433 [0.316, 0.559], Macro-F1 = 0.409 [0.278, 0.531]
- **Status**: Near-chance classification (baseline chance = 33.3%, Wilson CIs span chance).
- **Corpus Skew (N=1,500)**: 87.5% `build_internal` reflects classifier bias on informal developer text.

### Task 4: Econometric Linkage (96 Public SaaS Companies)
- **Moat Density vs. Excess Return vs IGV**: Spearman $\rho = 0.1197$, $p = 0.2558$ ($N=92$). Not statistically significant at $\alpha = 0.05$.
- **Moat Density vs. Revenue Growth**: Spearman $\rho = 0.0514$, $p = 0.6264$ ($N=92$). Not statistically significant.
- **Top Sector**: Data & Infrastructure (+42.15% excess vs. IGV); **Lagging**: Fintech & HR (-131.16% vs. IGV).
- **Conclusion**: Market returns over 2023–2026 reflect macro/sector momentum rather than fine-grained 10-K paragraph moat mention frequency.

---

## 4. Run History & Failure Audits
1. **Run 1 (`runs/20261029_2322/`)**: Failed (`FileNotFoundError` path glob).
2. **Run 2 (`runs/20261028_2328/`)**: Failed (`AttributeError: shape` on `BatchEncoding`).
3. **Run 3 (`runs/20261028_2334/`)**: Failed (`TypeError: max_seq_length` in `SFTConfig`).
4. **Run 4 (`runs/20261028_2347/`)**: Failed (`ValueError: redundant peft_config` in `SFTTrainer`).
5. **Run 5 (`runs/20261028_2358/`)**: Failed (`NotImplementedError: GradScaler unscale on BFloat16` on Turing T4).
6. **Run 6 (`runs/20261030_0014/`)**: Failed (GradScaler unscale on BFloat16 during backprop).
7. **Run 7 (`runs/20261030_0023/`)**: Succeeded technically but mode-collapsed LoRA (`none_or_commodity`) and had audit flaws identified by reviewer.
8. **Run 8 (`runs/20261031_1510/`)**: Failed (`ImportError: bitsandbytes not installed`). Archived with `error_analysis.md` and full logs.
9. **Run 9 (`runs/20261031_1517/`)**: Zero-shot & few-shot passed with 0.500 & 0.525 acc; failed at Cell 11 (`DataCollatorForCompletionOnlyLM` removed from `trl 1.17`). Archived with `error_analysis.md` and full logs.
10. **Run 10 (`runs/20261031_1527/`)**: **SUCCESSFUL EXECUTION**. Acc 0.650 / F1 0.633. Balanced distribution across all 6 classes. Complete synchronization and 100% verified traceability in `CHECKS.md`.
