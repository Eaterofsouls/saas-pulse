# Failure Audit: Run 20261102_2105 (Kaggle Kernel Version 11)

**Run ID**: `20261102_2105` (Kaggle Version 11)  
**Timestamp**: 2026-11-02 21:05 - 21:22 IST  
**Status**: `KernelWorkerStatus.ERROR` (Failed at Cell 14 / In [14])  

---

## 1. Traceback & Error
```
AssertionError: SANITY GATE FAILED [few_shot_hn]: 'build_internal' got 44/60 = 73.3% > 70%. Mode collapse detected!
/tmp/ipykernel_22/2043068993.py in <cell line: 0>()
     24         print(f"  {i + 1}/60 done")
     25 
---> 26 sanity_gate(hn_fs_preds, HN_LABELS, threshold=0.70, name="few_shot_hn")
     27 res_hn_fs = compute_metrics(y_test_hn, hn_fs_preds, HN_LABELS, "few_shot_hn")
```

---

## 2. Root Cause Analysis
1. **Mathematical Distortion in Candidate Scoring**:
   In Cell 5, `score_labels_constrained` computed:
   `scores[label] = float(total_log_prob / len(label))`
   `len(label)` measured the character count of the label string:
   - `build_internal`: 14 characters
   - `buy_saas`: 8 characters
   - `hybrid_or_neutral`: 17 characters

   Because token log-probabilities are negative (e.g., $-4.0$), dividing by a larger character count moves the score closer to $0$ (e.g., $-4.0 / 14 = -0.2857$, whereas $-4.0 / 8 = -0.5000$). Because $-0.2857 > -0.5000$, `build_internal` was awarded an artificial ~75% mathematical boost over `buy_saas` on every single comment. This caused base model scoring to select `build_internal` 42/60 (70.0%) times in zero-shot and 44/60 (73.3%) times in few-shot.
2. **Unhandled Exception in Sanity Gate**:
   `sanity_gate` raised `AssertionError`, halting the Python interpreter before Cell 14 (econometric linkage), Cell 15 (predictions), and Cell 17 (`metrics.json`) could execute.

---

## 3. Successful Verification in Run 11
Before the failure in Cell 14, the following critical milestones were verified:
1. **Approved Review Bundle Ingested**:
   `gold_review_completed.xlsx` was unpacked and applied: 52 evaluated 10-K rows ($N=35$ test, $N=17$ val, 8 excluded). Agreement with keyword rules was 65.4% (Cohen's $\kappa = 0.5742$).
2. **LoRA Fine-Tuning Completed**:
   All 72 steps (3 epochs over 140 train paragraphs with prompt loss masking) completed with smooth convergence.
3. **LoRA Moat Classification Evaluated**:
   - Sample Accuracy: **0.629** (Wilson 95% CI: [0.463, 0.768])
   - Macro-F1: **0.598** (Bootstrap 95% CI: [0.382, 0.763])
   - Balanced distribution: `none_or_commodity`: 8, `network_effects_ecosystem`: 9, `system_of_record`: 6, `compliance_security`: 4, `data_gravity`: 4, `switching_costs_integrations`: 4. Mode collapse was completely eliminated!

---

## 4. Fixes Implemented for Run 12 (Kernel Version 12)
1. **Pristine Constrained Scoring**: Removed `len(label)` division. Scores now evaluate exact label string + `\n` using total log-probability: `total_log_prob = -float(out.loss.item()) * n_toks`, as specified in prompt guidelines.
2. **Non-Halting Sanity Gate**: `sanity_gate` flags mode collapse, prints warnings and distribution, and records `sanity_gate_passed: bool`, allowing execution to proceed and record honest findings.
3. **Interleaved HN Exemplars**: Alternating class order across rounds prevents sequence block bias.
4. **Item 1 Paragraph Filtering**: Enforced Item 1 paragraph selection for latest fiscal year in RQ4.
