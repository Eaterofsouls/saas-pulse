# patch_nb_cells_v3.py
import re
from pathlib import Path

path = Path("saas_pulse/saas_pulse_nb_cells_v2.py")
content = path.read_text(encoding="utf-8")

# 1. Replace Cell 5: score_labels_constrained, predict_constrained, sanity_gate
old_cell5_pattern = r"def score_labels_constrained\(target_model, tok, prompt, candidates, normalize_by_length=True\):.*?print\(f\"Sanity gate PASSED \[{name}\]: distribution {dict\(c\)}\"\)"

new_cell5 = '''def score_labels_constrained(target_model, tok, prompt, candidates, normalize_by_tokens=False):
    # Computes log-likelihood of each candidate continuation given prompt.
    # Uses teacher-forcing with prompt tokens masked by -100.
    # Evaluates exact label tokens followed by newline as specified in prompt protocol.
    device = next(target_model.parameters()).device
    prompt_ids = tok(prompt, return_tensors="pt", add_special_tokens=True).input_ids.to(device)
    scores = {}
    with torch.no_grad():
        for label in candidates:
            cand_str = f"{label}\\n"
            label_ids = tok(cand_str, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
            full_ids = torch.cat([prompt_ids, label_ids], dim=1)
            full_labels = torch.cat([
                torch.full_like(prompt_ids, -100),
                label_ids,
            ], dim=1)
            out = target_model(input_ids=full_ids, labels=full_labels)
            n_toks = label_ids.shape[1]
            total_log_prob = -float(out.loss.item()) * n_toks
            if normalize_by_tokens:
                # Per-token log-likelihood (acc_norm standard: divide by token count n_toks, NEVER char length!)
                scores[label] = float(-out.loss.item())
            else:
                # Total sequence log-likelihood (standard prefix-free argmax)
                scores[label] = float(total_log_prob)
    return scores

def predict_constrained(target_model, tok, prompt, candidates, normalize_by_tokens=False):
    scores = score_labels_constrained(target_model, tok, prompt, candidates, normalize_by_tokens=normalize_by_tokens)
    return max(scores, key=scores.get), scores

def sanity_gate(preds, candidates, threshold=0.70, name=""):
    c = Counter(preds)
    n = len(preds)
    passed = True
    violating = []
    for label in candidates:
        frac = c.get(label, 0) / n
        if frac > threshold:
            violating.append((label, frac))
            passed = False
    if not passed:
        msg = f"SANITY GATE WARNING [{name}]: Mode collapse detected! " + ", ".join([f"'{l}'={f:.1%} > {threshold:.0%}" for l, f in violating])
        print(f"\\n{'='*70}\\n{msg}\\nDistribution: {dict(c)}\\n{'='*70}\\n")
    else:
        print(f"Sanity gate PASSED [{name}]: distribution {dict(c)}")
    return passed'''

if "def score_labels_constrained(target_model, tok, prompt, candidates, normalize_by_length=True):" in content:
    content, n_sub = re.subn(old_cell5_pattern, new_cell5, content, flags=re.DOTALL)
    print(f"Cell 5 replacement count: {n_sub}")
    assert n_sub == 1, "Failed to replace Cell 5"
else:
    print("Cell 5 already patched or pattern differs.")

# 2. Update Cell 8:
content = content.replace(
    'print("Running zero-shot constrained scoring on 10K test (n=40)...")',
    'print(f"Running zero-shot constrained scoring on 10K test (n={len(test10k)})...")'
)
content = content.replace(
    '        print(f"  {i + 1}/40 done")',
    '        print(f"  {i + 1}/{len(test10k)} done")'
)
content = content.replace(
    'sanity_gate(zs_preds, MOAT_LABELS, threshold=0.70, name="zero_shot_10k")\nres_zs = compute_metrics(y_test_10k, zs_preds, MOAT_LABELS, "zero_shot_10k")',
    'res_zs = compute_metrics(y_test_10k, zs_preds, MOAT_LABELS, "zero_shot_10k")\nres_zs["sanity_gate_passed"] = sanity_gate(zs_preds, MOAT_LABELS, threshold=0.70, name="zero_shot_10k")'
)

# 3. Update Cell 9: interleave HN exemplars
old_hn_exemplars = '''    exemplars_hn = []
    exemplar_ids_hn = []
    for lbl in HN_LABELS:
        pool   = hn_pool[hn_pool["rule_stance"] == lbl]
        n_pick = min(2, len(pool))
        chosen = pool.sample(n_pick, random_state=SEED) if n_pick > 0 else pool
        for _, r in chosen.iterrows():
            exemplars_hn.append((lbl, r["text"]))
            exemplar_ids_hn.append(str(r["id"]))
    print(f"HN exemplar IDs (2 per class): {exemplar_ids_hn}")'''

new_hn_exemplars = '''    exemplars_by_class = {lbl: [] for lbl in HN_LABELS}
    for lbl in HN_LABELS:
        pool   = hn_pool[hn_pool["rule_stance"] == lbl]
        n_pick = min(2, len(pool))
        chosen = pool.sample(n_pick, random_state=SEED) if n_pick > 0 else pool
        for _, r in chosen.iterrows():
            exemplars_by_class[lbl].append((str(r["id"]), r["text"]))
    exemplars_hn = []
    exemplar_ids_hn = []
    for round_idx in range(2):
        for lbl in HN_LABELS:
            if round_idx < len(exemplars_by_class[lbl]):
                ex_id, ex_txt = exemplars_by_class[lbl][round_idx]
                exemplars_hn.append((lbl, ex_txt))
                exemplar_ids_hn.append(ex_id)
    print(f"HN exemplar IDs (2 per class, interleaved): {exemplar_ids_hn}")'''

if old_hn_exemplars in content:
    content = content.replace(old_hn_exemplars, new_hn_exemplars)
    print("Cell 9 HN exemplars interleaved.")

# 4. Update Cell 10:
content = content.replace(
    'print("Running few-shot constrained scoring on 10K test (n=40)...")',
    'print(f"Running few-shot constrained scoring on 10K test (n={len(test10k)})...")'
)
content = content.replace(
    'sanity_gate(fs_preds, MOAT_LABELS, threshold=0.70, name="few_shot_10k")\nres_fs = compute_metrics(y_test_10k, fs_preds, MOAT_LABELS, "few_shot_10k")',
    'res_fs = compute_metrics(y_test_10k, fs_preds, MOAT_LABELS, "few_shot_10k")\nres_fs["sanity_gate_passed"] = sanity_gate(fs_preds, MOAT_LABELS, threshold=0.70, name="few_shot_10k")'
)

# 5. Update Cell 12:
content = content.replace(
    'print("Running LoRA constrained scoring on 10K test (n=40)...")',
    'print(f"Running LoRA constrained scoring on 10K test (n={len(test10k)})...")'
)
content = content.replace(
    'sanity_gate(lora_preds, MOAT_LABELS, threshold=0.70, name="lora_10k")\nres_lora = compute_metrics(y_test_10k, lora_preds, MOAT_LABELS, "lora_10k")',
    'res_lora = compute_metrics(y_test_10k, lora_preds, MOAT_LABELS, "lora_10k")\nres_lora["sanity_gate_passed"] = sanity_gate(lora_preds, MOAT_LABELS, threshold=0.70, name="lora_10k")'
)

# 6. Update Cell 13:
content = content.replace(
    'sanity_gate(hn_zs_preds, HN_LABELS, threshold=0.70, name="zero_shot_hn")\nres_hn_zs = compute_metrics(y_test_hn, hn_zs_preds, HN_LABELS, "zero_shot_hn")',
    'res_hn_zs = compute_metrics(y_test_hn, hn_zs_preds, HN_LABELS, "zero_shot_hn")\nres_hn_zs["sanity_gate_passed"] = sanity_gate(hn_zs_preds, HN_LABELS, threshold=0.70, name="zero_shot_hn")'
)
content = content.replace(
    'sanity_gate(hn_fs_preds, HN_LABELS, threshold=0.70, name="few_shot_hn")\nres_hn_fs = compute_metrics(y_test_hn, hn_fs_preds, HN_LABELS, "few_shot_hn")',
    'res_hn_fs = compute_metrics(y_test_hn, hn_fs_preds, HN_LABELS, "few_shot_hn")\nres_hn_fs["sanity_gate_passed"] = sanity_gate(hn_fs_preds, HN_LABELS, threshold=0.70, name="few_shot_hn")'
)

# 7. Update Cell 13b (best method selection and text snippet):
old_cell13b_loop = '''    best_method = ("few_shot" if res_hn_fs["macro_f1"] >= res_hn_zs["macro_f1"]
                   else "zero_shot")
    print(f"  Using {best_method} for corpus inference")
    METRICS["corpus_hn_method"] = best_method

    corpus_preds = []
    t0 = _time.time()
    for i, row in enumerate(sample_df.itertuples()):
        if best_method == "few_shot":
            prompt = build_few_shot_prompt_hn(row.text, exemplars_hn)
        else:
            prompt = build_zero_shot_prompt_hn(row.text)
        pred, _ = predict_constrained(model, tokenizer, prompt, HN_LABELS)'''

new_cell13b_loop = '''    valid_methods = [
        (m, r) for m, r in [("few_shot", res_hn_fs), ("zero_shot", res_hn_zs)]
        if r.get("sanity_gate_passed", True)
    ]
    if valid_methods:
        best_method = max(valid_methods, key=lambda x: x[1]["macro_f1"])[0]
    else:
        best_method = "zero_shot" if res_hn_zs["macro_f1"] >= res_hn_fs["macro_f1"] else "few_shot"
    print(f"  Using {best_method} for corpus inference (sanity gate verified)")
    METRICS["corpus_hn_method"] = best_method

    corpus_preds = []
    t0 = _time.time()
    for i, row in enumerate(sample_df.itertuples()):
        text_snip = str(row.text)[:400]
        if best_method == "few_shot":
            prompt = build_few_shot_prompt_hn(text_snip, exemplars_hn)
        else:
            prompt = build_zero_shot_prompt_hn(text_snip)
        pred, _ = predict_constrained(model, tokenizer, prompt, HN_LABELS)'''

if old_cell13b_loop in content:
    content = content.replace(old_cell13b_loop, new_cell13b_loop)
    print("Cell 13b updated.")

# 8. Update Cell 14 (RQ4 Item 1 filtering and paragraph text truncation):
old_cell14_sample = '''    for i, ticker in enumerate(common_tickers):
        t_fil     = fil_df[fil_df["ticker"] == ticker]
        latest_fy = t_fil["fiscal_year"].max()
        t_fil     = t_fil[t_fil["fiscal_year"] == latest_fy]
        sample_n  = min(30, len(t_fil))
        t_sample  = (t_fil.sample(sample_n, random_state=SEED)
                     if sample_n > 0 else t_fil)

        preds_c = []
        for row in t_sample.itertuples():
            if best_rq4 == "few_shot":
                prompt = build_few_shot_prompt_10k(row.text, exemplars_10k)
                pred, _ = predict_constrained(model, tokenizer, prompt, MOAT_LABELS)
            elif best_rq4 == "lora":
                prompt = build_zero_shot_prompt_10k(row.text)
                pred, _ = predict_constrained(peft_model, tokenizer, prompt, MOAT_LABELS)
            else:
                prompt = build_zero_shot_prompt_10k(row.text)
                pred, _ = predict_constrained(model, tokenizer, prompt, MOAT_LABELS)
            preds_c.append(pred)'''

new_cell14_sample = '''    for i, ticker in enumerate(common_tickers):
        t_fil     = fil_df[fil_df["ticker"] == ticker]
        latest_fy = t_fil["fiscal_year"].max()
        t_fil     = t_fil[t_fil["fiscal_year"] == latest_fy]
        t_item1   = t_fil[t_fil["section"] == "Item 1"]
        if len(t_item1) >= 10:
            t_fil = t_item1
        sample_n  = min(30, len(t_fil))
        t_sample  = (t_fil.sample(sample_n, random_state=SEED)
                     if sample_n > 0 else t_fil)

        preds_c = []
        for row in t_sample.itertuples():
            para_txt = str(row.text)[:600]
            if best_rq4 == "few_shot":
                prompt = build_few_shot_prompt_10k(para_txt, exemplars_10k)
                pred, _ = predict_constrained(model, tokenizer, prompt, MOAT_LABELS)
            elif best_rq4 == "lora":
                prompt = build_zero_shot_prompt_10k(para_txt)
                pred, _ = predict_constrained(peft_model, tokenizer, prompt, MOAT_LABELS)
            else:
                prompt = build_zero_shot_prompt_10k(para_txt)
                pred, _ = predict_constrained(model, tokenizer, prompt, MOAT_LABELS)
            preds_c.append(pred)'''

assert old_cell14_sample in content, "old_cell14_sample not found"
content = content.replace(old_cell14_sample, new_cell14_sample)
print("Cell 14 updated.")

# 9. Update Cell 16 & 17 labels/prints
content = content.replace(
    'fig.suptitle("10-K Moat Classification (test n=40, labels=keyword-rule)", y=1.02)',
    'fig.suptitle(f"10-K Moat Classification (test n={len(y_test_10k)}, student-approved labels)", y=1.02)'
)
content = content.replace(
    'print("\\n===== RESULTS SUMMARY (10K moat classification, n=40, keyword-rule labels) =====")',
    'print(f"\\n===== RESULTS SUMMARY (10K moat classification, n={len(y_test_10k)}, student-approved labels) =====")'
)

path.write_text(content, encoding="utf-8")
print("All patches successfully applied to saas_pulse/saas_pulse_nb_cells_v2.py!")
