#!/usr/bin/env python3
"""
patch_nb_cells.py
Updates saas_pulse_nb_cells_v2.py with the approved review labels logic and self-containment.
"""

from pathlib import Path

def main():
    path = Path("saas_pulse_nb_cells_v2.py")
    content = path.read_text(encoding="utf-8")
    
    # 1. Update Cell 2 find_file logic
    old_c2 = """SEARCH_ROOTS = ["/kaggle/input", "../input", ".", "..", "/kaggle/working"]

def find_file(name, roots=SEARCH_ROOTS):
    for root in roots:
        hits = glob.glob(f"{root}/**/{name}", recursive=True)
        if hits:
            return hits[0]
    return None"""

    new_c2 = """SEARCH_ROOTS = ["/kaggle/working", ".", "..", "/kaggle/input", "../input"]

def find_file(name, roots=SEARCH_ROOTS):
    for d in ["/kaggle/working", "/kaggle/input/saas-pulse-dataset", ".", ".."]:
        cand = os.path.join(d, name)
        if os.path.exists(cand):
            return cand
    for root in roots:
        cand = os.path.join(root, name)
        if os.path.exists(cand):
            return cand
        hits = glob.glob(f"{root}/**/{name}", recursive=True)
        if hits:
            return hits[0]
    return None"""
    assert old_c2 in content, "old_c2 not found in saas_pulse_nb_cells_v2.py"
    content = content.replace(old_c2, new_c2)

    # 2. Update Cell 3 review processing logic
    old_c3_start = 'REVIEW_PATH = find_file("gold_review_completed.xlsx")'
    old_c3_end = 'METRICS["label_source_note"] = (\n    "human_reviewed" if REVIEW_PATH\n    else "keyword_rule — no human review; gold_review_completed.xlsx not present"\n)'
    
    # Let's find the section between old_c3_start and old_c3_end
    idx1 = content.find(old_c3_start)
    idx2 = content.find(old_c3_end)
    assert idx1 != -1 and idx2 != -1, f"indices: {idx1}, {idx2}"
    
    new_c3_block = """REVIEW_PATH = find_file("gold_review_completed.xlsx")
if REVIEW_PATH:
    print(f"\\nReview file FOUND: {REVIEW_PATH} — applying student-approved labels...")
    xls = pd.read_excel(REVIEW_PATH, sheet_name=None)
    if "10K_review" in xls:
        rev = xls["10K_review"].copy()
        rev["your_clean"] = rev["your_label"].fillna("").astype(str).str.strip().str.lower()
        rev_valid = rev[rev["your_clean"] != "exclude"].copy()
        rev_valid["final_label"] = rev_valid["your_clean"].where(
            rev_valid["your_clean"] != "",
            rev_valid["suggested_label"]
        )
        exclude_ids = set(rev.loc[rev["your_clean"] == "exclude", "para_id"])
        reviewed_ids = set(rev_valid["para_id"])
        lookup_10k = dict(zip(rev_valid["para_id"], rev_valid["final_label"]))
        
        df10k = df10k[~df10k["para_id"].isin(exclude_ids)].copy()
        df10k["label_source"] = df10k["para_id"].apply(
            lambda pid: "llm_reviewed_student_approved" if pid in reviewed_ids else "keyword_rule"
        )
        df10k["final_label"] = df10k["para_id"].apply(
            lambda pid: lookup_10k.get(pid, df10k.loc[df10k["para_id"] == pid, "predicted_moat"].values[0])
        )
        n_changed   = (rev_valid["final_label"] != rev_valid["suggested_label"]).sum()
        agree_rate  = (rev_valid["final_label"] == rev_valid["suggested_label"]).mean()
        print(f"  10K review: {len(rev_valid)} rows evaluated, {len(exclude_ids)} excluded")
        print(f"  Labels changed vs rule: {n_changed}")
        print(f"  Rule<->Approved agreement rate: {agree_rate:.3f}")
        METRICS["review_10k_n_rows"]     = len(rev_valid)
        METRICS["review_10k_n_excluded"] = len(exclude_ids)
        METRICS["review_10k_n_changed"]  = int(n_changed)
        METRICS["review_10k_agree_rate"] = round(float(agree_rate), 4)

    # HN review was NOT reviewed per student instructions. Stance labels remain rule-generated.
    dfhn["label_source"] = "keyword_rule"
    dfhn["final_label"]  = dfhn["predicted_stance"] if "predicted_stance" in dfhn.columns else dfhn["user_corrected_label"]
    print("  HN review: unreviewed per protocol. Stance labels reported as keyword_rule.")

    METRICS["label_source_note"] = "llm_reviewed_student_approved (Claude Opus 5.5 + Daksh Chauhan approval)"
else:
    print("\\nReview file NOT found. Using pre-existing label_source / final_label from CSVs.")
    if "label_source" not in df10k.columns:
        df10k["label_source"] = "keyword_rule"
    if "final_label" not in df10k.columns:
        df10k["final_label"] = df10k["user_corrected_label"]
    if "label_source" not in dfhn.columns:
        dfhn["label_source"] = "keyword_rule"
    if "final_label" not in dfhn.columns:
        dfhn["final_label"] = dfhn["user_corrected_label"]
    METRICS["label_source_note"] = "keyword_rule — no human review; gold_review_completed.xlsx not present" """

    content = content[:idx1] + new_c3_block + content[idx2 + len(old_c3_end):]

    # 3. Update Rule baseline note in Cell 7
    old_rule_note = 'res_rule["note"] = "Rule preds == gold labels. Identity by construction, NOT a model evaluation."'
    new_rule_note = 'res_rule["note"] = "Heuristic keyword rule baseline evaluated against student-approved gold labels."'
    if old_rule_note in content:
        content = content.replace(old_rule_note, new_rule_note)

    old_rule_call = 'rule_preds = list(test10k["user_corrected_label"])'
    new_rule_call = 'rule_preds = list(test10k["rule_label"] if "rule_label" in test10k.columns else test10k["predicted_moat"])'
    if old_rule_call in content:
        content = content.replace(old_rule_call, new_rule_call)

    path.write_text(content, encoding="utf-8")
    print("Successfully patched saas_pulse_nb_cells_v2.py")

if __name__ == "__main__":
    main()
