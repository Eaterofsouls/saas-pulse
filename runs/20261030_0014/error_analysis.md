# Run 20261030_0014 Failure Audit

- **Timestamp**: 2026-10-30 00:14 IST
- **Status**: Failed (KernelWorkerStatus.ERROR during LoRA training epoch 1)
- **Exit Code / Error**: `NotImplementedError: "_amp_foreach_non_finite_check_and_unscale_cuda" not implemented for 'BFloat16'`
- **Execution Progress Before Error**:
  - Environment setup: Passed (Tesla T4 GPU with 14.56 GB VRAM detected).
  - Dataset ingestion: Passed.
  - Base model loading: Passed.
  - Task 1 Zero-Shot & Few-Shot CoT benchmark: **100% COMPLETE** (all 40 test paragraphs evaluated successfully across both methods).
  - LoRA Adapter Creation: **PASSED** (`trainable params: 4,358,144 || all params: 1,548,072,448 || trainable%: 0.2815`).
  - SFTTrainer initialization: **PASSED**.
  - LoRA forward pass: **PASSED**.
  - Error occurred in `accelerator.unscale_gradients()` / `torch.amp.grad_scaler.unscale_()`.
- **Root Cause**:
  When `fp16=True` is enabled in `SFTConfig`, PyTorch Trainer instantiates an AMP `GradScaler`. On Turing T4 GPUs, calling `_amp_foreach_non_finite_check_and_unscale_` throws `NotImplementedError` if any Qwen2.5 internal module outputs BFloat16 gradients during backprop.
- **Resolution for Run 7**:
  Set `fp16=False` and `bf16=False` in `SFTConfig`. For QLoRA, the base model is 4-bit frozen while the small LoRA adapters (only 4.3M parameters = ~34 MB VRAM) are updated directly in FP32. This completely bypasses the AMP `GradScaler` and eliminates the CUDA unscaling failure while fitting effortlessly inside the 16 GB T4 VRAM.
