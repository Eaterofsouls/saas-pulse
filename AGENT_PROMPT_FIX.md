# TASK: Fix the SaaS-Pulse evaluation, make every claim honest, and re-run on Kaggle

Work inside saas_pulse/ and keep mirroring to the GitHub repo (Eaterofsouls/saas-pulse, branch main) exactly as before: commit small and often, keep STATUS.md updated with a heartbeat at least every 5 minutes while a Kaggle run is active, and never commit secrets (kaggle.json, KAGGLE API credentials, GitHub or HF tokens, .env). Check `git diff --cached` for secrets before every push. Keep every failed run in its own runs/<timestamp>/ folder.

A reviewer audited run 20261030_0023. These are the problems you must fix. Do not argue with them; verify each one yourself first and record your finding in FIX_LOG.md.

1. gold_10k_moats.csv and gold_hn_stance.csv: `user_corrected_label` equals `predicted_moat` / `predicted_stance` in 100% of rows, and there are only 6 distinct rationales. The labels are keyword-rule labels. GOLD_PROVENANCE.md claims human audit of all rows. That claim is false.
2. The LoRA run predicted `none_or_commodity` for all 40 test paragraphs. That is a pipeline bug (likely loss over the whole prompt and fragile free-text parsing), not a scientific finding.
3. HN stance eval got accuracy 0.333, macro-F1 0.167 (predicted `hybrid_or_neutral` for all 60). The slides do not report this, and slide 9's "44% build / 36% buy" has no source in any run.
4. Slide 10 reports a Spearman of revenue growth vs excess return. That does not test moats. The line "moat density ... +86.4 pp" has no source in any metrics file.
5. Few-shot predictions are heavily skewed (21 of 40 = `network_effects_ecosystem`).

## STEP 0. Read the human review (if present)
If `dataset/review/gold_review_completed.xlsx` exists (sheets `10K_review`, optionally `HN_review`):
- For each row, final label = `your_label` if not blank, else `suggested_label`. Rows with `your_label == "exclude"` are dropped from evaluation (record how many).
- Write `label_source` = `human_reviewed` for those rows and `keyword_rule` for all other rows (the 140 train rows stay rule-generated). Add `rule_label` (original) and `final_label`.
- Compute and record: number of rows changed, agreement rate between rule label and human label, Cohen's kappa, and the confusion between them on the reviewed 10-K rows (60) and HN rows (60 if present).
- If the file does not exist yet, STOP after steps 1-2 below and write in STATUS.md that you are waiting for it. Do not fabricate reviewed labels.
- Rewrite GOLD_PROVENANCE.md truthfully: train labels are keyword-rule generated; only the val/test rows listed were human reviewed, with the suggested label visible during review (possible anchoring); give the counts above. Delete every sentence claiming that all 200 / 60 rows were human audited. Same for GOLD_REVIEW.md, HN_STANCE_METHOD.md and DATASHEET.md.

## STEP 1. Fair, constrained evaluation (replaces free-text parsing)
For every method, predict by scoring each candidate label, not by parsing generated text:
- Build the prompt ending in `Answer:` and compute the model's total log-probability of each label string (use the exact label tokens followed by EOS or newline) given the prompt. Prediction = argmax. This guarantees a valid label every time.
- Methods: (a) zero-shot with the taxonomy definitions from `dataset/review` Taxonomy wording, (b) few-shot with exactly one training exemplar per class (6 exemplars, fixed seed 42, drawn only from train), (c) LoRA, (d) baselines: majority class, uniform random (seed 42), and the original keyword rule applied to the test paragraph text. Report (d) honestly: the keyword rule vs human labels shows how noisy the rules are.
- Optional CoT row: only if you also report the fraction of outputs with a parseable final label. Otherwise drop CoT and say so.
- Report on val (final labels) and test (final labels): accuracy with Wilson CI, macro-F1 with 1000-sample bootstrap CI (seed 42), per-class P/R/F1, confusion matrix, prediction distribution, McNemar exact binomial p for each method pair on test. n is 40 or fewer: write that in the output.
- SANITY GATE: print the prediction distribution of each method. If any method puts more than 70% of predictions in one class, treat it as a bug, debug it, and do not report that number as a result.

## STEP 2. Fix the LoRA training
- Format each example as prompt + label completion. Compute loss ONLY on the completion tokens (set labels to -100 for the prompt). Completion is just the label string plus EOS (no rationale).
- Qwen2.5-1.5B-Instruct, 4-bit NF4 base, LoRA r=16, alpha=32, dropout 0.05, target q,k,v,o. Learning rate 2e-4, batch 4 with grad accumulation 4, up to 5 epochs. Keep adapters in fp32 and fp16/bf16 off on T4 (this avoided the GradScaler crash before). Evaluate on val every epoch; use the epoch with the best val macro-F1 for the test report. Save the loss and val-F1 per epoch to CSV and plot them.
- Train on the 140 train rows only (rule labels). State on the slide that training labels are rule-generated, so the LoRA mainly learns the rules plus whatever generalises.
- If LoRA test accuracy is below few-shot, report exactly that.

## STEP 3. HN stance (honest)
Run zero-shot and few-shot (constrained scoring as above) on the 60 HN comments using final labels. Few-shot exemplars: 6 comments (2 per class) taken from `hn_comments.jsonl`, NOT in the 60-row set (check by id), chosen by the keyword rule with seed 42, and listed in the output. Report distributions and the sanity gate. No LoRA for HN. If the result is near chance, say so; do not invent a corpus-level build/buy percentage. If you want a corpus-level share, run the best method over a random 1,500-comment sample (seed 42) and report the predicted shares with a bootstrap CI and the measured test-set accuracy next to it.

## STEP 4. Make RQ3 test what it claims
- For each of the 96 tickers with stock data, take up to 30 Item 1 paragraphs (seed 42) from that company's latest fiscal year, predict their moat class with the best method by validation macro-F1, and compute per-company shares of each class. Company moat score = share of the five structural classes combined (everything except `none_or_commodity`).
- Report Spearman between moat score and excess return vs IGV, and between moat score and revenue growth, each with n, p and a 95% bootstrap CI. Also report the same correlation for the category-level grouping separately and label it "sector effect, not moat classifier". Do not claim causation. If the correlation is not significant, say so on the slide.
- Delete the "+86.4 pp moat density" line unless this step reproduces it from files you commit.
- Re-check the category table against stock_performance.csv and list median return and median excess for each category from the file itself (the earlier draft said Cybersecurity +46.5% excess; the latest run said -16.4%; the slides must show the number the file gives).

## STEP 5. Run on Kaggle and commit
Run the full pipeline on Kaggle T4 (GPU, Internet on). Commit under runs/<timestamp>/: executed notebook, HTML, log, metrics.json (written by the notebook), predictions.csv with per-method predictions and raw scores, loss/val curves CSV and PNG, environment metadata. Time budget: 90 minutes total; stop and report if the Kaggle part exceeds 45 minutes. Priority if time is short: STEP 0 > STEP 1 > STEP 2 > STEP 3 > STEP 4.

## STEP 6. Slides and checks
- Update PRESENTATION_SLIDES.md and presentation.html by script from metrics.json only. Slide 8 must show: baselines, zero-shot, few-shot, LoRA, with CIs and n. Add one limitation line: "Training labels rule-generated; test set human-reviewed (n = <count>); small n".
- Slide 9 uses only the HN numbers from STEP 3, with the measured accuracy next to them.
- Slide 10 uses STEP 4 outputs, titled to say exactly what it tests.
- Slide 12 limitations: rule-generated training labels, anchoring during review, small test set, HN selection bias, survivorship, correlation not causation.
- Regenerate CHECKS.md: for EVERY number on every slide, list the source file and key. Fail loudly (non-zero exit) if any number has no source. Grep for stale numbers: 0.482, 0.654, 0.835, 0.260, 0.404, 0.067, 44%, 36%, 86.4, 46.5.

## FINAL REPORT (reply with this, in this order)
1. Repo URL, final commit hash, final run folder.
2. Table: method, test accuracy (CI), macro-F1 (CI), prediction distribution.
3. Human-review stats (rows changed, kappa) or "waiting for review file".
4. Every problem you found or could not fix, including anything in this prompt you believe is wrong.
5. Do not describe results as good unless metrics.json supports it.
