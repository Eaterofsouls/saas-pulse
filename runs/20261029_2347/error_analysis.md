# Run 20261029_2347 Failure Audit

- **Timestamp**: 2026-10-29 23:47 IST
- **Status**: Failed (KernelWorkerStatus.ERROR at step 6 / cell 7)
- **Exit Code / Error**: `ValueError: You passed a PeftModel instance together with a peft_config to the trainer.`
- **Execution Progress Before Error**:
  - Environment setup: Passed (Tesla T4 GPU with 14.56 GB VRAM detected).
  - Dataset ingestion: Passed (100 companies, 538 XBRL revenues, 200 gold 10-K moats, 60 HN stance comments loaded from `/kaggle/input`).
  - Base model loading: Passed (`Qwen2.5-1.5B-Instruct` loaded in 4-bit NF4 precision).
  - Task 1 Zero-Shot & Few-Shot CoT benchmark: **100% COMPLETE** (all 40 test paragraphs evaluated successfully across both methods).
  - LoRA Adapter Creation: **PASSED** (`trainable params: 4,358,144 || all params: 1,548,072,448 || trainable%: 0.2815`).
  - Failure occurred when instantiating `SFTTrainer` because both `peft_model` and `peft_config` were provided simultaneously.
- **Root Cause**:
  `trl.SFTTrainer` expects either:
  1. An already-wrapped `PeftModel` without passing `peft_config`, OR
  2. A raw base model with `peft_config` passed for automatic wrapping.
  Passing both caused `is_peft_model(model)` check to trigger a `ValueError`.
- **Resolution for Run 5**:
  Omit `peft_config` from `trainer_kwargs` since `peft_model` is already explicitly instantiated via `get_peft_model(peft_model, peft_config)`.
