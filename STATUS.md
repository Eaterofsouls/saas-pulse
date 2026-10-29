# SaaS-Pulse Live Status & Progress Tracker

**Repository**: [https://github.com/Eaterofsouls/saas-pulse](https://github.com/Eaterofsouls/saas-pulse)  
**Last Updated**: 2026-10-29 23:58:50 IST  
**Current Step**: Step 3 — Kaggle Kernel Version 5 Running on GPU T4  
**Kaggle Kernel URL**: [https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment](https://www.kaggle.com/code/notaveragehee/saas-pulse-experiment)  
**Kaggle Dataset URL**: [https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset](https://www.kaggle.com/datasets/notaveragehee/saas-pulse-dataset)

---

## 1. Current Execution Status
- **Phase**: Live Kaggle GPU T4 Execution (Run 5 / Version 5).
- **Active Task**: Executing `saas_pulse_experiment.ipynb` on NVIDIA Tesla T4 with clean `SFTTrainer` adapter binding.
- **Heartbeat Log**:
  - `2026-10-29 23:15 IST`: Git initialized, secrets scanned clean, initial commit pushed.
  - `2026-10-29 23:18 IST`: GitHub Release `v1.0.0` published with `saas_pulse_dataset.zip`.
  - `2026-10-29 23:21 IST`: Private Kaggle dataset `notaveragehee/saas-pulse-dataset` uploaded and verified `ready`.
  - `2026-10-29 23:22 IST`: Kernel Version 1 pushed. Error recorded (dataset path glob issue). Full logs and HTML archived in `runs/20261029_2322/`.
  - `2026-10-29 23:28 IST`: Kernel Version 2 pushed. Error recorded (`AttributeError: shape` on `BatchEncoding`). Full logs and HTML archived in `runs/20261029_2328/`.
  - `2026-10-29 23:34 IST`: Kernel Version 3 pushed. Zero-shot & Few-shot completed 100%; error at `SFTConfig.max_seq_length`. Full logs and HTML archived in `runs/20261029_2334/`.
  - `2026-10-29 23:47 IST`: Kernel Version 4 pushed. Zero-shot & Few-shot completed 100%; error at `SFTTrainer` redundant `peft_config`. Full logs and HTML archived in `runs/20261029_2347/`.
  - `2026-10-29 23:58 IST`: Kernel Version 5 pushed with clean adapter passing to `SFTTrainer`. Run status: **RUNNING**.

---

## 2. Milestone Audit

| Step | Milestone | Status | Details / Artifacts |
| :--- | :--- | :---: | :--- |
| **0** | **Secrets & Security Check** | **PASSED** | `.gitignore` verified, zero tokens/keys in repo. |
| **1** | **Dataset Curation & Packaging** | **PASSED** | 100/100 companies, 538 XBRL revenues, 190k paras, 7.8k HN posts. |
| **2** | **Gold Benchmark Deduplication** | **PASSED** | `gold_10k_moats.csv` strictly 0 text overlap across train/val/test. |
| **3** | **Methodology & Provenance** | **PASSED** | `GOLD_PROVENANCE.md` & `HN_STANCE_METHOD.md` published. |
| **4** | **Kaggle Dataset Upload** | **PASSED** | `notaveragehee/saas-pulse-dataset` is active and `ready`. |
| **5** | **Kaggle T4 Experiment Execution** | **RUNNING** | Run 5 active on Tesla T4 (`saas-pulse-experiment`). |
| **6** | **Remote Output Retrieval & Audit** | *Pending* | Downloading `metrics.json`, predictions, loss curve to `runs/`. |
| **7** | **Slide Verification & CHECKS.md** | *Pending* | Regenerating slides directly from execution `metrics.json`. |

---

## 3. Run History & Failure Audits
1. **Run 1 (`runs/20261029_2322/`)**:
   - Status: Failed (`FileNotFoundError`).
   - Cause: Search path only globbed current directory `.` instead of `/kaggle/input`.
   - Resolution: Recursive search across `[Path("/kaggle/input"), Path("../input"), Path("."), Path("..")]`.
2. **Run 2 (`runs/20261029_2328/`)**:
   - Status: Failed (`AttributeError: KeyError: 'shape'`).
   - Cause: Modern Hugging Face `apply_chat_template` returns a `BatchEncoding` dict which cannot be passed positionally to `model.generate()`.
   - Resolution: Two-step tokenization (`tokenizer.apply_chat_template(..., tokenize=False)` followed by `tokenizer(..., return_tensors="pt")`) and unpacking with `**inputs`.
3. **Run 3 (`runs/20261029_2334/`)**:
   - Status: Failed (`TypeError: max_seq_length` in `SFTConfig`). Zero-shot & Few-shot evaluation completed 100% (40/40 test paragraphs).
   - Cause: Recent `trl` version renamed `max_seq_length` to `max_length`.
   - Resolution: Dynamic parameter inspection via `inspect.signature(SFTConfig.__init__).parameters`.
4. **Run 4 (`runs/20261029_2347/`)**:
   - Status: Failed (`ValueError: You passed a PeftModel instance together with a peft_config to the trainer`).
   - Cause: Passing both an already-wrapped `peft_model` and `peft_config` into `SFTTrainer`.
   - Resolution: Omit redundant `peft_config` argument when passing `peft_model`.
5. **Run 5 (`runs/20261029_2358/`)**:
   - Status: Currently executing on GPU T4.
