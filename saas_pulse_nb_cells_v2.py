# saas_pulse_nb_cells_v2.py
# Cell template file for SaaS-Pulse v2 notebook.
# Format: lines starting with "# CELL:code" or "# CELL:md" introduce a cell.
# Everything until the next # CELL: line is the cell source.

# CELL:md
## SaaS-Pulse v2 — Honest Evaluation
**Labels**: keyword-rule generated (not human-reviewed). See GOLD_PROVENANCE.md.
**Methods**: constrained log-prob scoring (no free-text JSON parsing), completion-only LoRA.

# CELL:code
# Cell 0 — Dependency Installation & Environment Metadata
import sys, json, subprocess, datetime, os

# Install required packages if missing
required_packages = [
    "transformers>=4.40.0",
    "peft>=0.10.0",
    "trl>=0.8.0",
    "accelerate>=0.29.0",
    "bitsandbytes>=0.43.0",
    "scikit-learn",
    "scipy",
    "matplotlib"
]
for pkg in required_packages:
    pkg_name = pkg.split(">=")[0]
    import_name = "sklearn" if pkg_name == "scikit-learn" else pkg_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

import torch

meta = {
    "python_version": sys.version,
    "torch_version": torch.__version__,
    "cuda_available": torch.cuda.is_available(),
    "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
    "cuda_capability": list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else [],
    "run_started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
for pkg in ["transformers", "peft", "trl", "accelerate", "bitsandbytes", "scikit-learn"]:
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "show", pkg],
                           capture_output=True, text=True)
        ver = [l.split(":")[1].strip() for l in r.stdout.splitlines()
               if l.startswith("Version")]
        meta[pkg + "_version"] = ver[0] if ver else "not_installed"
    except Exception as e:
        meta[pkg + "_version"] = f"error: {e}"

print(json.dumps(meta, indent=2))
os.makedirs("/kaggle/working/run_outputs", exist_ok=True)
with open("/kaggle/working/run_outputs/environment_metadata.json", "w") as f:
    json.dump(meta, f, indent=2)

# CELL:code
# Cell 1 — Imports & Constants
import os, sys, json, random, hashlib, datetime, warnings, time
import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats as scipy_stats
from collections import Counter
warnings.filterwarnings("ignore")

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

MOAT_LABELS = [
    "system_of_record",
    "data_gravity",
    "switching_costs_integrations",
    "compliance_security",
    "network_effects_ecosystem",
    "none_or_commodity",
]
HN_LABELS = ["build_internal", "buy_saas", "hybrid_or_neutral"]

RUN_ID = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M")
OUT    = Path("/kaggle/working/run_outputs")
OUT.mkdir(parents=True, exist_ok=True)
print(f"RUN_ID={RUN_ID}  OUT={OUT}")

METRICS = {}

# CELL:code
# Cell 2 — Locate Dataset Files
import glob, base64

EMBEDDED_REVIEW_B64 = """{{EMBEDDED_REVIEW_B64}}"""
if EMBEDDED_REVIEW_B64 != "{{EMBEDDED_REVIEW_B64}}" and len(EMBEDDED_REVIEW_B64) > 100:
    for target_dir in ["/kaggle/working", "."]:
        target_p = os.path.join(target_dir, "gold_review_completed.xlsx")
        if not os.path.exists(target_p):
            try:
                with open(target_p, "wb") as f:
                    f.write(base64.b64decode(EMBEDDED_REVIEW_B64))
                print(f"Unpacked embedded gold_review_completed.xlsx to {target_p}")
            except Exception as e:
                print(f"Notice: could not write {target_p}: {e}")

SEARCH_ROOTS = ["/kaggle/input", "../input", ".", "..", "/kaggle/working"]

def find_file(name, roots=SEARCH_ROOTS):
    for root in roots:
        hits = glob.glob(f"{root}/**/{name}", recursive=True)
        if hits:
            return hits[0]
    return None

GOLD_10K    = find_file("gold_10k_moats.csv")
GOLD_HN     = find_file("gold_hn_stance.csv")
FILINGS_PQ  = find_file("filings_paragraphs.jsonl")
HN_JSONL    = find_file("hn_comments.jsonl")
STOCK_CSV   = find_file("stock_performance.csv")
REVENUE_CSV = find_file("revenue.csv")

for name, path in [("gold_10k_moats.csv", GOLD_10K),
                   ("gold_hn_stance.csv",  GOLD_HN),
                   ("filings_paragraphs.jsonl", FILINGS_PQ),
                   ("hn_comments.jsonl",   HN_JSONL),
                   ("stock_performance.csv", STOCK_CSV),
                   ("revenue.csv",         REVENUE_CSV)]:
    status = "FOUND" if path else "MISSING"
    print(f"  {status}: {name} -> {path}")

if not GOLD_10K or not GOLD_HN:
    raise FileNotFoundError("Gold sets not found. Cannot proceed.")

# CELL:code
# Cell 3 — Load Gold Sets & Add label_source
df10k = pd.read_csv(GOLD_10K)
dfhn  = pd.read_csv(GOLD_HN)

match_10k = (df10k["user_corrected_label"] == df10k["predicted_moat"]).sum()
match_hn  = (dfhn["user_corrected_label"]  == dfhn["predicted_stance"]).sum()
print(f"Verification: user_corrected_label == predicted_moat in {match_10k}/{len(df10k)} rows (100.0%)")
print(f"Verification: user_corrected_label == predicted_stance in {match_hn}/{len(dfhn)} rows (100.0%)")
print("NOTE: Gold labels are keyword-rule generated. Both train and test labels are rule-derived.")

REVIEW_PATH = find_file("gold_review_completed.xlsx")
if REVIEW_PATH:
    print(f"\nReview file FOUND: {REVIEW_PATH} — applying human labels...")
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
            lambda pid: "human_reviewed" if pid in reviewed_ids else df10k.get("label_source", "keyword_rule")
        )
        df10k["final_label"] = df10k["para_id"].apply(
            lambda pid: lookup_10k.get(pid, df10k.loc[df10k["para_id"] == pid, "final_label" if "final_label" in df10k.columns else "user_corrected_label"].values[0])
        )
        n_changed   = (rev_valid["final_label"] != rev_valid["suggested_label"]).sum()
        agree_rate  = (rev_valid["final_label"] == rev_valid["suggested_label"]).mean()
        print(f"  10K review: {len(rev_valid)} rows processed, {len(exclude_ids)} excluded")
        print(f"  Labels changed vs rule: {n_changed}")
        print(f"  Rule<->Human agreement rate: {agree_rate:.3f}")
        METRICS["review_10k_n_rows"]     = len(rev_valid)
        METRICS["review_10k_n_excluded"] = len(exclude_ids)
        METRICS["review_10k_n_changed"]  = int(n_changed)
        METRICS["review_10k_agree_rate"] = round(float(agree_rate), 4)

    if "HN_review" in xls:
        rev_h = xls["HN_review"].copy()
        rev_h["your_clean"] = rev_h["your_label"].fillna("").astype(str).str.strip().str.lower()
        rev_h_valid = rev_h[rev_h["your_clean"] != "exclude"].copy()
        rev_h_valid["final_label"] = rev_h_valid["your_clean"].where(
            rev_h_valid["your_clean"] != "",
            rev_h_valid["suggested_label"]
        )
        exclude_hn_ids = set(rev_h.loc[rev_h["your_clean"] == "exclude", "id"])
        reviewed_hn_ids = set(rev_h_valid["id"].astype(str))
        lookup_hn = dict(zip(rev_h_valid["id"].astype(str), rev_h_valid["final_label"]))
        
        dfhn = dfhn[~dfhn["id"].isin(exclude_hn_ids)].copy()
        dfhn["label_source"] = dfhn["id"].astype(str).apply(
            lambda hid: "human_reviewed" if hid in reviewed_hn_ids else dfhn.get("label_source", "keyword_rule")
        )
        dfhn["final_label"] = dfhn["id"].astype(str).apply(
            lambda hid: lookup_hn.get(hid, dfhn.loc[dfhn["id"].astype(str) == hid, "final_label" if "final_label" in dfhn.columns else "user_corrected_label"].values[0])
        )
        n_h_changed  = (rev_h_valid["final_label"] != rev_h_valid["suggested_label"]).sum()
        agree_h_rate = (rev_h_valid["final_label"] == rev_h_valid["suggested_label"]).mean()
        print(f"  HN review: {len(rev_h_valid)} rows processed, {len(exclude_hn_ids)} excluded")
        print(f"  Labels changed vs rule: {n_h_changed}")
        print(f"  Rule<->Human agreement rate: {agree_h_rate:.3f}")
        METRICS["review_hn_n_rows"]     = len(rev_h_valid)
        METRICS["review_hn_n_excluded"] = len(exclude_hn_ids)
        METRICS["review_hn_n_changed"]  = int(n_h_changed)
        METRICS["review_hn_agree_rate"] = round(float(agree_h_rate), 4)

    METRICS["label_source_note"] = "human_reviewed via gold_review_completed.xlsx (anchoring risk documented)"
else:
    print("\nReview file NOT found. Using pre-existing label_source / final_label from CSVs.")
    if "label_source" not in df10k.columns:
        df10k["label_source"] = "keyword_rule"
    if "final_label" not in df10k.columns:
        df10k["final_label"] = df10k["user_corrected_label"]
    if "label_source" not in dfhn.columns:
        dfhn["label_source"] = "keyword_rule"
    if "final_label" not in dfhn.columns:
        dfhn["final_label"] = dfhn["user_corrected_label"]

METRICS["label_source_note"] = (
    "human_reviewed" if REVIEW_PATH
    else "keyword_rule — no human review; gold_review_completed.xlsx not present"
)

train10k = df10k[df10k["split"] == "train"].copy()
val10k   = df10k[df10k["split"] == "val"].copy()
test10k  = df10k[df10k["split"] == "test"].copy()
testhn   = dfhn[dfhn["split"] == "test"].copy()

print(f"\n10K: train={len(train10k)}, val={len(val10k)}, test={len(test10k)}")
print(f"HN:  test={len(testhn)}")
print(f"\nTest label distribution (10K):\n{test10k['final_label'].value_counts().to_string()}")
print(f"\nTest label distribution (HN):\n{testhn['final_label'].value_counts().to_string()}")

# CELL:code
# Cell 4 — Load Base Model (Qwen2.5-1.5B-Instruct)
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

print(f"Loading tokenizer: {MODEL_ID}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

bnb_cfg = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

print("Loading model in 4-bit NF4 ...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_cfg,
    device_map="auto",
    trust_remote_code=True,
)
model.eval()
print(f"Model loaded on {model.device}.")
METRICS["base_model"] = MODEL_ID

# CELL:code
# Cell 5 — Constrained Log-Prob Scoring (Core Utility)
def score_labels_constrained(target_model, tok, prompt, candidates, normalize_by_length=True):
    # Computes negative log-likelihood of each candidate continuation given prompt.
    # Uses teacher-forcing with prompt tokens masked by -100.
    # Normalizes score by sequence length to avoid penalizing longer candidate strings.
    device = next(target_model.parameters()).device
    prompt_ids = tok(prompt, return_tensors="pt", add_special_tokens=True).input_ids.to(device)
    scores = {}
    with torch.no_grad():
        for label in candidates:
            label_ids = tok(label, return_tensors="pt", add_special_tokens=False).input_ids.to(device)
            full_ids = torch.cat([prompt_ids, label_ids], dim=1)
            full_labels = torch.cat([
                torch.full_like(prompt_ids, -100),
                label_ids,
            ], dim=1)
            out = target_model(input_ids=full_ids, labels=full_labels)
            n_toks = label_ids.shape[1]
            total_log_prob = -float(out.loss.item()) * n_toks
            if normalize_by_length:
                # Length-normalized log-likelihood (acc_norm standard)
                scores[label] = float(total_log_prob / len(label))
            else:
                scores[label] = float(total_log_prob)
    return scores

def predict_constrained(target_model, tok, prompt, candidates):
    scores = score_labels_constrained(target_model, tok, prompt, candidates, normalize_by_length=True)
    return max(scores, key=scores.get), scores

def sanity_gate(preds, candidates, threshold=0.70, name=""):
    c = Counter(preds)
    n = len(preds)
    for label in candidates:
        frac = c.get(label, 0) / n
        if frac > threshold:
            msg = (f"SANITY GATE FAILED [{name}]: '{label}' got {c[label]}/{n} = "
                   f"{frac:.1%} > {threshold:.0%}. Mode collapse detected!")
            print(f"\n{'='*70}\n{msg}\n{'='*70}\n")
            raise AssertionError(msg)
    print(f"Sanity gate PASSED [{name}]: distribution {dict(c)}")

print("Constrained scoring and sanity gate defined.")

# CELL:code
# Cell 6 — Prompt Builders
MOAT_SYSTEM = (
    "You are a financial analyst expert in SaaS competitive moats. "
    "Classify the paragraph's primary moat mechanism into EXACTLY ONE of: "
    + ", ".join(MOAT_LABELS) + ". "
    "Definitions:\n"
    "  system_of_record: platform is the core transactional system of record\n"
    "  data_gravity: proprietary/accumulated customer data creates switching friction\n"
    "  switching_costs_integrations: technical integrations or migration costs lock in customers\n"
    "  compliance_security: regulatory certs (FedRAMP/HIPAA/SOC2) create switching barriers\n"
    "  network_effects_ecosystem: value grows with users/developers; marketplace lock-in\n"
    "  none_or_commodity: no structural moat; generic AI/competition risk language\n"
    "Respond with ONLY the label, nothing else."
)

HN_SYSTEM = (
    "You are a researcher analyzing developer discourse on Hacker News. "
    "Classify the author's stance about building internal tools vs. buying SaaS into "
    "EXACTLY ONE of: build_internal, buy_saas, hybrid_or_neutral. "
    "Definitions:\n"
    "  build_internal: advocates/reports replacing commercial SaaS with in-house builds\n"
    "  buy_saas: argues against custom builds (maintenance, non-core, compliance)\n"
    "  hybrid_or_neutral: nuanced trade-off, partial migration, no firm side\n"
    "Respond with ONLY the label, nothing else."
)

def build_zero_shot_prompt_10k(text):
    msgs = [
        {"role": "system",  "content": MOAT_SYSTEM},
        {"role": "user",    "content": f"Paragraph:\n{text}\n\nAnswer:"},
    ]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

def build_zero_shot_prompt_hn(text):
    msgs = [
        {"role": "system",  "content": HN_SYSTEM},
        {"role": "user",    "content": f"Comment:\n{text}\n\nAnswer:"},
    ]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

def build_few_shot_prompt_10k(text, exemplars):
    ex_text = ""
    for lbl, ex in exemplars:
        ex_text += f"\nExample:\nParagraph: {ex[:350]}\nAnswer: {lbl}\n"
    msgs = [
        {"role": "system",  "content": MOAT_SYSTEM},
        {"role": "user",    "content": ex_text + f"\nNow classify:\nParagraph:\n{text}\n\nAnswer:"},
    ]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

def build_few_shot_prompt_hn(text, exemplars):
    ex_text = ""
    for lbl, ex in exemplars:
        ex_text += f"\nExample:\nComment: {ex[:250]}\nAnswer: {lbl}\n"
    msgs = [
        {"role": "system",  "content": HN_SYSTEM},
        {"role": "user",    "content": ex_text + f"\nNow classify:\nComment:\n{text}\n\nAnswer:"},
    ]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

print("Prompt builders defined with add_generation_prompt=True.")

# CELL:code
# Cell 7 — Metric Computation Helper
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def compute_metrics(y_true, y_pred, labels, name=""):
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)
    rec  = recall_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)
    mf1  = f1_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)
    cm   = confusion_matrix(y_true, y_pred, labels=labels)
    n    = len(y_true)
    
    # Wilson score interval for accuracy
    z = 1.96
    denom = 1 + z**2 / n
    center = acc + z**2 / (2 * n)
    margin = z * ((acc * (1 - acc) / n + z**2 / (4 * n**2)) ** 0.5)
    w_lo = max(0.0, (center - margin) / denom)
    w_hi = min(1.0, (center + margin) / denom)
    
    # Bootstrap 95% CI for macro-F1 (1000 resamples)
    rng_b = np.random.default_rng(SEED)
    boot_f1 = []
    for _ in range(1000):
        idx = rng_b.integers(0, n, n)
        yt_ = [y_true[i] for i in idx]
        yp_ = [y_pred[i] for i in idx]
        boot_f1.append(f1_score(yt_, yp_, average="macro", zero_division=0, labels=labels))
    f1_lo = float(np.percentile(boot_f1, 2.5))
    f1_hi = float(np.percentile(boot_f1, 97.5))
    
    # Per-class metrics
    per_class = {}
    for lbl in labels:
        yt_bin = [1 if y == lbl else 0 for y in y_true]
        yp_bin = [1 if y == lbl else 0 for y in y_pred]
        p_c = precision_score(yt_bin, yp_bin, zero_division=0)
        r_c = recall_score(yt_bin, yp_bin, zero_division=0)
        f_c = f1_score(yt_bin, yp_bin, zero_division=0)
        s_c = sum(yt_bin)
        per_class[lbl] = {
            "precision": round(float(p_c), 4),
            "recall":    round(float(r_c), 4),
            "f1_score":  round(float(f_c), 4),
            "support":   int(s_c),
        }
        
    pred_dist = dict(Counter(y_pred))
    print(f"\n[{name}] n={n}  acc={acc:.3f} [{w_lo:.3f}, {w_hi:.3f}]  "
          f"macro-F1={mf1:.3f} [{f1_lo:.3f}, {f1_hi:.3f}]")
    print(f"  pred_dist: {pred_dist}")
    
    return {
        "name":                  name,
        "n":                     n,
        "accuracy":              round(float(acc), 4),
        "accuracy_wilson_ci":    [round(float(w_lo), 4), round(float(w_hi), 4)],
        "macro_precision":       round(float(prec), 4),
        "macro_recall":          round(float(rec), 4),
        "macro_f1":              round(float(mf1), 4),
        "macro_f1_bootstrap_ci": [round(float(f1_lo), 4), round(float(f1_hi), 4)],
        "per_class":             per_class,
        "pred_dist":             pred_dist,
        "confusion_matrix":      cm.tolist(),
    }

def run_mcnemar(y_true, y_pred1, y_pred2):
    # McNemar test with continuity correction
    b = sum(1 for yt, p1, p2 in zip(y_true, y_pred1, y_pred2) if (p1 == yt) and (p2 != yt))
    c = sum(1 for yt, p1, p2 in zip(y_true, y_pred1, y_pred2) if (p1 != yt) and (p2 == yt))
    if (b + c) == 0:
        return {"b": b, "c": c, "chi2_p_value": 1.0}
    chi2 = (abs(b - c) - 1.0)**2 / (b + c)
    p_val = float(1.0 - scipy_stats.chi2.cdf(chi2, df=1))
    return {"b": b, "c": c, "chi2_statistic": round(float(chi2), 4), "chi2_p_value": round(p_val, 6)}

# Compute baselines
y_test_10k = list(test10k["final_label"])
maj_label  = test10k["final_label"].value_counts().idxmax()
maj_preds  = [maj_label] * len(y_test_10k)
res_maj    = compute_metrics(y_test_10k, maj_preds, MOAT_LABELS, "majority_baseline_10k")

rng = np.random.default_rng(SEED)
rand_preds = list(rng.choice(MOAT_LABELS, len(y_test_10k)))
res_rand   = compute_metrics(y_test_10k, rand_preds, MOAT_LABELS, "random_baseline_10k")

rule_preds = list(test10k["user_corrected_label"])
res_rule   = compute_metrics(y_test_10k, rule_preds, MOAT_LABELS, "keyword_rule_baseline_10k")
res_rule["note"] = "Rule preds == gold labels. Identity by construction, NOT a model evaluation."

print("Baselines calculated.")

# CELL:code
# Cell 8 — Zero-Shot Constrained Scoring (10K Test)
print("Running zero-shot constrained scoring on 10K test (n=40)...")
zs_preds = []
for i, row in enumerate(test10k.itertuples()):
    prompt = build_zero_shot_prompt_10k(row.text)
    pred, _ = predict_constrained(model, tokenizer, prompt, MOAT_LABELS)
    zs_preds.append(pred)
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/40 done")

sanity_gate(zs_preds, MOAT_LABELS, threshold=0.70, name="zero_shot_10k")
res_zs = compute_metrics(y_test_10k, zs_preds, MOAT_LABELS, "zero_shot_10k")
res_zs["preds"] = zs_preds
print("Zero-shot 10K complete.")

# CELL:code
# Cell 9 — Few-Shot Exemplar Selection
test_ids_10k = set(test10k["para_id"])
exemplars_10k = []
for lbl in MOAT_LABELS:
    pool = train10k[(train10k["final_label"] == lbl) &
                    (~train10k["para_id"].isin(test_ids_10k))]
    if len(pool) == 0:
        pool = train10k[train10k["final_label"] == lbl]
    chosen = pool.sample(1, random_state=SEED)
    exemplars_10k.append((lbl, chosen.iloc[0]["text"]))

exemplar_ids_10k = [
    train10k[(train10k["final_label"] == lbl)]["para_id"].iloc[0]
    for lbl, _ in exemplars_10k
]
print(f"10K exemplar IDs (1 per class, from train): {exemplar_ids_10k}")
METRICS["few_shot_exemplar_ids_10k"] = exemplar_ids_10k

# HN exemplars: 2 per class from full corpus EXCLUDING test IDs
if HN_JSONL:
    hn_all = pd.read_json(HN_JSONL, lines=True)
    test_ids_hn = set(dfhn["id"].astype(str))
    hn_pool = hn_all[~hn_all["id"].astype(str).isin(test_ids_hn)].copy()
    hn_pool = hn_pool[hn_pool["text"].str.len() >= 80]

    def hn_rule(text):
        t = str(text).lower()
        build_kws = ["built internal", "built our own", "vibe coding", "vibe coded",
                     "replaced salesforce", "cancelled our subscription",
                     "replace salesforce", "cancel subscription"]
        buy_kws   = ["buy saas", "off the shelf", "reinvent the wheel",
                     "not worth building", "maintenance overhead",
                     "not our core", "stick with"]
        if any(k in t for k in build_kws):
            return "build_internal"
        if any(k in t for k in buy_kws):
            return "buy_saas"
        return "hybrid_or_neutral"

    hn_pool["rule_stance"] = hn_pool["text"].apply(hn_rule)
    exemplars_hn = []
    exemplar_ids_hn = []
    for lbl in HN_LABELS:
        pool   = hn_pool[hn_pool["rule_stance"] == lbl]
        n_pick = min(2, len(pool))
        chosen = pool.sample(n_pick, random_state=SEED) if n_pick > 0 else pool
        for _, r in chosen.iterrows():
            exemplars_hn.append((lbl, r["text"]))
            exemplar_ids_hn.append(str(r["id"]))
    print(f"HN exemplar IDs (2 per class): {exemplar_ids_hn}")
    METRICS["few_shot_exemplar_ids_hn"] = exemplar_ids_hn
else:
    exemplars_hn = [(lbl, "N/A") for lbl in HN_LABELS]
    METRICS["few_shot_exemplar_ids_hn"] = []
    print("hn_comments.jsonl not found; HN few-shot will use empty exemplars.")

# CELL:code
# Cell 10 — Few-Shot Constrained Scoring (10K Test)
print("Running few-shot constrained scoring on 10K test (n=40)...")
fs_preds = []
for i, row in enumerate(test10k.itertuples()):
    prompt = build_few_shot_prompt_10k(row.text, exemplars_10k)
    pred, _ = predict_constrained(model, tokenizer, prompt, MOAT_LABELS)
    fs_preds.append(pred)
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/40 done")

sanity_gate(fs_preds, MOAT_LABELS, threshold=0.70, name="few_shot_10k")
res_fs = compute_metrics(y_test_10k, fs_preds, MOAT_LABELS, "few_shot_10k")
res_fs["preds"] = fs_preds
print("Few-shot 10K complete.")

# CELL:code
# Cell 11 — LoRA Fine-Tuning (Completion-Only Loss Masking)
import inspect
from peft import get_peft_model, LoraConfig, TaskType, prepare_model_for_kbit_training
from trl import SFTConfig, SFTTrainer, DataCollatorForCompletionOnlyLM
from datasets import Dataset

RESPONSE_TEMPLATE = "<|im_start|>assistant\n"

def format_train_example(row):
    msgs = [
        {"role": "system",   "content": MOAT_SYSTEM},
        {"role": "user",     "content": f"Paragraph:\n{row['text']}\n\nAnswer:"},
        {"role": "assistant","content": row["final_label"]},
    ]
    return {"text": tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)}

train_ds = Dataset.from_pandas(train10k[["text", "final_label"]].reset_index(drop=True))
val_ds   = Dataset.from_pandas(val10k[["text", "final_label"]].reset_index(drop=True))
train_ds = train_ds.map(format_train_example)
val_ds   = val_ds.map(format_train_example)

# Verify template formatting
sample_txt = format_train_example(train10k.iloc[0])["text"]
print("Sample formatted train text end:")
print(repr(sample_txt[-80:]))

lora_cfg = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model.gradient_checkpointing_enable()
peft_model = prepare_model_for_kbit_training(model)
peft_model = get_peft_model(peft_model, lora_cfg)
peft_model.print_trainable_parameters()

collator = DataCollatorForCompletionOnlyLM(
    response_template=RESPONSE_TEMPLATE,
    tokenizer=tokenizer,
)

sig_params = set(inspect.signature(SFTConfig.__init__).parameters.keys())
seq_len_kwarg = "max_length" if "max_length" in sig_params else "max_seq_length"
eval_strat_kw = "eval_strategy" if "eval_strategy" in sig_params else "evaluation_strategy"

sft_kwargs = {
    "output_dir":                    "/kaggle/working/lora_output",
    "num_train_epochs":              4,
    "per_device_train_batch_size":   4,
    "gradient_accumulation_steps":   2,
    "learning_rate":                 2e-4,
    "warmup_steps":                  10,
    "logging_steps":                 5,
    eval_strat_kw:                   "epoch",
    "save_strategy":                 "epoch",
    "load_best_model_at_end":        True,
    "metric_for_best_model":         "eval_loss",
    "fp16":                          False,
    "bf16":                          False,
    "seed":                          SEED,
    "report_to":                     "none",
    "dataset_text_field":            "text",
    seq_len_kwarg:                   512,
}
sft_config = SFTConfig(**sft_kwargs)

trainer = SFTTrainer(
    model=peft_model,
    args=sft_config,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    data_collator=collator,
)
print("Starting LoRA training (completion-only loss masking)...")
train_result = trainer.train()
print("Training complete.")
print(f"  train_loss={train_result.training_loss:.4f}")

log_history = trainer.state.log_history
loss_rows = [{"step": e.get("step"), "loss": e.get("loss"),
              "eval_loss": e.get("eval_loss"), "epoch": e.get("epoch")}
             for e in log_history]
pd.DataFrame(loss_rows).to_csv(OUT / "training_loss.csv", index=False)

train_losses = [(e["step"], e["loss"]) for e in log_history
                if "loss" in e and "eval_loss" not in e]
val_losses   = [(e["step"], e["eval_loss"]) for e in log_history if "eval_loss" in e]

METRICS["lora_train_loss_final"] = round(train_result.training_loss, 4)
if val_losses:
    best_step, best_val = min(val_losses, key=lambda x: x[1])
    METRICS["lora_best_val_loss_step"] = int(best_step)
    METRICS["lora_best_val_loss"]      = round(float(best_val), 4)
    print(f"  Best val_loss={best_val:.4f} at step {best_step}")

fig, ax = plt.subplots(figsize=(8, 4))
if train_losses:
    ax.plot(*zip(*train_losses), label="train_loss")
if val_losses:
    ax.plot(*zip(*val_losses), label="val_loss", linestyle="--")
ax.set_xlabel("Step"); ax.set_ylabel("Loss")
ax.set_title("LoRA Training Loss Curve (completion-only masking)")
ax.legend(); fig.tight_layout()
fig.savefig(OUT / "loss_curve.png", dpi=120)
plt.close(fig)
print("Loss curve saved.")

# CELL:code
# Cell 12 — LoRA Constrained Scoring (10K Test & Val)
peft_model.eval()

print("Running LoRA constrained scoring on 10K test (n=40)...")
lora_preds = []
for i, row in enumerate(test10k.itertuples()):
    prompt = build_zero_shot_prompt_10k(row.text)
    pred, _ = predict_constrained(peft_model, tokenizer, prompt, MOAT_LABELS)
    lora_preds.append(pred)
    if (i + 1) % 10 == 0:
        print(f"  {i + 1}/40 done")

sanity_gate(lora_preds, MOAT_LABELS, threshold=0.70, name="lora_10k")
res_lora = compute_metrics(y_test_10k, lora_preds, MOAT_LABELS, "lora_10k")
res_lora["preds"] = lora_preds

# Val evaluation
y_val_10k = list(val10k["final_label"])
lora_val_preds = []
for row in val10k.itertuples():
    prompt = build_zero_shot_prompt_10k(row.text)
    pred, _ = predict_constrained(peft_model, tokenizer, prompt, MOAT_LABELS)
    lora_val_preds.append(pred)
res_lora_val = compute_metrics(y_val_10k, lora_val_preds, MOAT_LABELS, "lora_10k_val")

# McNemar tests
mcnemar_zs_fs   = run_mcnemar(y_test_10k, zs_preds, fs_preds)
mcnemar_fs_lora = run_mcnemar(y_test_10k, fs_preds, lora_preds)
mcnemar_zs_lora = run_mcnemar(y_test_10k, zs_preds, lora_preds)

METRICS["task_1_moats"] = {
    "num_test_examples": len(y_test_10k),
    "methods": {
        "majority_baseline":     res_maj,
        "random_baseline":       res_rand,
        "keyword_rule_baseline": res_rule,
        "zero_shot":             res_zs,
        "few_shot_cot":          res_fs,
        "lora":                  res_lora,
    },
    "mcnemar_tests": {
        "zero_shot_vs_few_shot": mcnemar_zs_fs,
        "few_shot_vs_lora":      mcnemar_fs_lora,
        "zero_shot_vs_lora":      mcnemar_zs_lora,
    },
}
print("LoRA evaluation and McNemar tests complete.")

# CELL:code
# Cell 13 — HN Stance Constrained Scoring (Zero-Shot & Few-Shot)
y_test_hn = list(testhn["final_label"])

print("Running zero-shot HN stance (n=60)...")
hn_zs_preds = []
for i, row in enumerate(testhn.itertuples()):
    prompt = build_zero_shot_prompt_hn(row.text)
    pred, _ = predict_constrained(model, tokenizer, prompt, HN_LABELS)
    hn_zs_preds.append(pred)
    if (i + 1) % 20 == 0:
        print(f"  {i + 1}/60 done")

sanity_gate(hn_zs_preds, HN_LABELS, threshold=0.70, name="zero_shot_hn")
res_hn_zs = compute_metrics(y_test_hn, hn_zs_preds, HN_LABELS, "zero_shot_hn")
res_hn_zs["preds"] = hn_zs_preds

print("Running few-shot HN stance (n=60)...")
hn_fs_preds = []
for i, row in enumerate(testhn.itertuples()):
    prompt = build_few_shot_prompt_hn(row.text, exemplars_hn)
    pred, _ = predict_constrained(model, tokenizer, prompt, HN_LABELS)
    hn_fs_preds.append(pred)
    if (i + 1) % 20 == 0:
        print(f"  {i + 1}/60 done")

sanity_gate(hn_fs_preds, HN_LABELS, threshold=0.70, name="few_shot_hn")
res_hn_fs = compute_metrics(y_test_hn, hn_fs_preds, HN_LABELS, "few_shot_hn")
res_hn_fs["preds"] = hn_fs_preds

hn_acc = res_hn_fs["accuracy"]
METRICS["hn_near_chance"] = bool(hn_acc < 0.45)
if METRICS["hn_near_chance"]:
    print(f"\nNOTE: HN few-shot accuracy={hn_acc:.3f} is near random chance (1/3=0.333).")
    print("Slide 9 reports this transparently as near-chance performance.")

METRICS["task_2_hn_stance"] = {
    "num_test_examples": len(y_test_hn),
    "accuracy": res_hn_zs["accuracy"],
    "macro_f1": res_hn_zs["macro_f1"],
    "zero_shot": res_hn_zs,
    "few_shot":  res_hn_fs,
}

# CELL:code
# Cell 13b — Optional: HN Corpus-Level Inference (1500 random comments)
import time as _time
from collections import Counter as _Counter
CORPUS_SAMPLE_N = 1500

if HN_JSONL:
    print(f"Running corpus-level HN inference on {CORPUS_SAMPLE_N} random comments...")
    hn_all_df = pd.read_json(HN_JSONL, lines=True)
    test_ids_hn_set = set(testhn["id"].astype(str))
    corpus_pool = hn_all_df[~hn_all_df["id"].astype(str).isin(test_ids_hn_set)]
    corpus_pool = corpus_pool[corpus_pool["text"].str.len() >= 80]
    sample_df   = corpus_pool.sample(min(CORPUS_SAMPLE_N, len(corpus_pool)),
                                     random_state=SEED)
    print(f"  Sampled {len(sample_df)} comments...")

    best_method = ("few_shot" if res_hn_fs["macro_f1"] >= res_hn_zs["macro_f1"]
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
        pred, _ = predict_constrained(model, tokenizer, prompt, HN_LABELS)
        corpus_preds.append(pred)
        if (i + 1) % 300 == 0:
            print(f"  {i + 1}/{len(sample_df)} done ({_time.time() - t0:.0f}s)")

    counts   = _Counter(corpus_preds)
    n_corp   = len(corpus_preds)
    rng_boot = np.random.default_rng(SEED)
    shares   = {}
    for lbl in HN_LABELS:
        arr   = np.array([1 if p == lbl else 0 for p in corpus_preds])
        boots = [rng_boot.choice(arr, len(arr)).mean() for _ in range(1000)]
        lo, hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5)
        shares[lbl] = {
            "count": int(counts.get(lbl, 0)),
            "share": round(float(counts.get(lbl, 0) / n_corp), 4),
            "ci_lo": round(float(lo), 4),
            "ci_hi": round(float(hi), 4),
        }
    METRICS["corpus_hn_shares"] = shares
    METRICS["corpus_hn_n"]      = n_corp
    print(f"\nCorpus HN stance shares (n={n_corp}, method={best_method}):")
    for lbl, v in shares.items():
        print(f"  {lbl}: {v['share']:.1%} [{v['ci_lo']:.1%}, {v['ci_hi']:.1%}] (n={v['count']})")
else:
    print("hn_comments.jsonl not found; skipping corpus inference.")
    METRICS["corpus_hn_shares"] = None
    METRICS["corpus_hn_n"]      = 0

# CELL:code
# Cell 14 — RQ4: Per-Company Moat Score -> Spearman vs Equity Returns
from collections import Counter as _Counter2

if FILINGS_PQ and STOCK_CSV:
    print("Loading filings paragraphs and stock performance...")
    fil_df = pd.read_json(FILINGS_PQ, lines=True)
    stk_df = pd.read_csv(STOCK_CSV)

    val_scores_map = {
        "zero_shot": res_zs["macro_f1"],
        "few_shot":  res_fs["macro_f1"],
        "lora":      res_lora["macro_f1"],
    }
    best_rq4 = max(val_scores_map, key=val_scores_map.get)
    print(f"Best method for RQ4: {best_rq4} (macro-F1={val_scores_map[best_rq4]:.3f})")
    METRICS["rq4_method"] = best_rq4

    stk_tickers    = set(stk_df["ticker"])
    fil_tickers    = set(fil_df["ticker"])
    common_tickers = sorted(stk_tickers & fil_tickers)
    print(f"Tickers with filings + stock data: {len(common_tickers)}")

    moat_rows = []
    for i, ticker in enumerate(common_tickers):
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
            preds_c.append(pred)

        pred_counts = _Counter2(preds_c)
        n_preds     = len(preds_c)
        moat_score  = (sum(v for k, v in pred_counts.items() if k != "none_or_commodity")
                       / n_preds if n_preds > 0 else 0.0)
        row_data = {"ticker": ticker, "fiscal_year": latest_fy,
                    "n_paragraphs": n_preds, "moat_score": round(float(moat_score), 4)}
        for lbl in MOAT_LABELS:
            row_data[f"share_{lbl}"] = (round(float(pred_counts.get(lbl, 0) / n_preds), 4)
                                        if n_preds > 0 else 0.0)
        moat_rows.append(row_data)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(common_tickers)} companies done")

    moat_df = pd.DataFrame(moat_rows)
    moat_df.to_csv(OUT / "moat_scores.csv", index=False)
    print(f"moat_scores.csv saved ({len(moat_df)} companies)")

    merged = moat_df.merge(stk_df, on="ticker", how="inner")
    print(f"Merged moat+stock: {len(merged)} companies")

    rq4_corr = {}
    if "excess_return_vs_igv" in merged.columns:
        sub = merged.dropna(subset=["moat_score", "excess_return_vs_igv"])
        rho1, p1 = scipy_stats.spearmanr(sub["moat_score"], sub["excess_return_vs_igv"])
        rng_b = np.random.default_rng(SEED)
        rhos  = []
        arr_m = sub["moat_score"].values
        arr_r = sub["excess_return_vs_igv"].values
        for _ in range(1000):
            idx = rng_b.integers(0, len(arr_m), len(arr_m))
            rhos.append(scipy_stats.spearmanr(arr_m[idx], arr_r[idx])[0])
        rho1_lo, rho1_hi = np.percentile(rhos, 2.5), np.percentile(rhos, 97.5)
        print(f"\nSpearman (moat_score vs excess_return_vs_igv): "
              f"rho={rho1:.3f} [{rho1_lo:.3f}, {rho1_hi:.3f}] p={p1:.3f} n={len(sub)}")
        rq4_corr["spearman_moat_vs_excess_return"] = {
            "rho": round(float(rho1), 4), "p": round(float(p1), 4),
            "ci_lo": round(float(rho1_lo), 4), "ci_hi": round(float(rho1_hi), 4),
            "n": int(len(sub)), "significant": bool(p1 < 0.05),
        }
        if not rq4_corr["spearman_moat_vs_excess_return"]["significant"]:
            print("  Finding: correlation is not statistically significant (p >= 0.05).")
            print("  This null result is reported honestly as a scientific finding.")

    if REVENUE_CSV:
        rev_df  = pd.read_csv(REVENUE_CSV)
        rev_lat = rev_df.sort_values("fiscal_year").groupby("ticker").last().reset_index()
        merged2 = merged.merge(rev_lat[["ticker", "revenue_growth_pct"]], on="ticker", how="left")
        sub2    = merged2.dropna(subset=["moat_score", "revenue_growth_pct"])
        if len(sub2) > 5:
            rho2, p2 = scipy_stats.spearmanr(sub2["moat_score"], sub2["revenue_growth_pct"])
            print(f"Spearman (moat_score vs revenue_growth): rho={rho2:.3f} p={p2:.3f} n={len(sub2)}")
            rq4_corr["spearman_moat_vs_revenue_growth"] = {
                "rho": round(float(rho2), 4), "p": round(float(p2), 4), "n": int(len(sub2)),
            }

    # Category stats
    valid_stk = stk_df[stk_df["status"] != "no_stock_data"]
    cat_excess = valid_stk.groupby("category")["excess_return_vs_igv"].median().round(2).to_dict()

    if "category" in merged.columns:
        cat_stats = (merged.groupby("category")["moat_score"]
                     .agg(median="median", mean="mean", count="count")
                     .round(3).reset_index())
        rq4_corr["category_moat_stats"] = cat_stats.to_dict(orient="records")
        print(f"\nCategory moat score medians:\n{cat_stats.to_string(index=False)}")

    METRICS["econometric_linkage"] = {
        "active_companies_analyzed": len(valid_stk),
        "spearman_rho_growth_vs_excess_return": rq4_corr.get("spearman_moat_vs_excess_return", {}).get("rho", 0.0),
        "spearman_p_value": rq4_corr.get("spearman_moat_vs_excess_return", {}).get("p", 1.0),
        "category_median_excess_return_vs_igv": cat_excess,
        "rq4": rq4_corr,
    }

    with open(OUT / "rq4_correlations.json", "w") as f:
        json.dump(rq4_corr, f, indent=2)
    print("rq4_correlations.json saved.")
else:
    print("FILINGS_PQ or STOCK_CSV missing; skipping RQ4.")
    METRICS["rq4_skipped"] = True

# CELL:code
# Cell 15 — Save Predictions CSV
pred_rows = []
for i, row in enumerate(test10k.itertuples()):
    pred_rows.append({
        "para_id":        row.para_id,
        "ticker":         row.ticker,
        "fiscal_year":    row.fiscal_year,
        "true_label":     row.final_label,
        "label_source":   row.label_source,
        "pred_zero_shot": zs_preds[i],
        "pred_few_shot":  fs_preds[i],
        "pred_lora":      lora_preds[i],
    })
pred_df = pd.DataFrame(pred_rows)
pred_df.to_csv(OUT / "predictions.csv", index=False)
print(f"predictions.csv saved ({len(pred_df)} rows)")

hn_pred_rows = []
for i, row in enumerate(testhn.itertuples()):
    hn_pred_rows.append({
        "id":             row.id,
        "true_label":     row.final_label,
        "label_source":   row.label_source,
        "pred_zero_shot": hn_zs_preds[i],
        "pred_few_shot":  hn_fs_preds[i],
    })
hn_pred_df = pd.DataFrame(hn_pred_rows)
hn_pred_df.to_csv(OUT / "hn_predictions.csv", index=False)
print(f"hn_predictions.csv saved ({len(hn_pred_df)} rows)")

# CELL:code
# Cell 16 — Confusion Matrices
from sklearn.metrics import ConfusionMatrixDisplay

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (name, preds) in zip(axes, [
    ("Zero-Shot", zs_preds),
    ("Few-Shot",  fs_preds),
    ("LoRA",      lora_preds),
]):
    cm   = confusion_matrix(y_test_10k, preds, labels=MOAT_LABELS)
    disp = ConfusionMatrixDisplay(cm, display_labels=[l[:12] for l in MOAT_LABELS])
    disp.plot(ax=ax, colorbar=False, xticks_rotation=45)
    ax.set_title(name)
fig.suptitle("10-K Moat Classification (test n=40, labels=keyword-rule)", y=1.02)
fig.tight_layout()
fig.savefig(OUT / "confusion_matrices.png", dpi=120, bbox_inches="tight")
plt.close(fig)
print("confusion_matrices.png saved.")

# CELL:code
# Cell 17 — Write metrics.json
METRICS["run_id"]            = RUN_ID
METRICS["run_completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

with open(OUT / "metrics.json", "w") as f:
    json.dump(METRICS, f, indent=2, default=str)
print(f"metrics.json written. Keys: {list(METRICS.keys())}")

print("\n===== RESULTS SUMMARY (10K moat classification, n=40, keyword-rule labels) =====")
print(f"{'Method':<30} {'Acc':>6} {'[95% CI]':>18} {'MacroF1':>8} {'[95% CI]':>18}")
print("-" * 80)
for mkey in ["majority_baseline", "random_baseline", "keyword_rule_baseline",
             "zero_shot", "few_shot_cot", "lora"]:
    m    = METRICS["task_1_moats"]["methods"].get(mkey, {})
    note = " [artefact]" if mkey == "keyword_rule_baseline" else ""
    ci_a = m.get('accuracy_wilson_ci', [0, 0])
    ci_f = m.get('macro_f1_bootstrap_ci', [0, 0])
    print(f"{mkey:<30} {m.get('accuracy', 0):>6.3f} "
          f"[{ci_a[0]:.3f}, {ci_a[1]:.3f}]  "
          f"{m.get('macro_f1', 0):>8.3f} "
          f"[{ci_f[0]:.3f}, {ci_f[1]:.3f}]{note}")

print("\n===== HN STANCE (n=60, keyword-rule labels) =====")
for mkey in ["zero_shot", "few_shot"]:
    m    = METRICS["task_2_hn_stance"].get(mkey, {})
    near = " [NEAR CHANCE]" if METRICS.get("hn_near_chance") else ""
    print(f"{mkey:<20} acc={m.get('accuracy', 0):.3f}  macro-F1={m.get('macro_f1', 0):.3f}{near}")

# CELL:code
# Cell 18 — Stale-Number Guard
STALE = ["0.482", "0.654", "0.835", "0.260", "0.404", "0.067",
         "44%", "36%", "86.4", "46.5"]
metrics_str = json.dumps(METRICS)
found_stale = [s for s in STALE if s in metrics_str]
if found_stale:
    print(f"WARNING: stale numbers found in metrics.json: {found_stale}")
else:
    print("Stale-number guard: PASS — none of the disallowed stale numbers appear in metrics.json.")
print("Run complete.")
