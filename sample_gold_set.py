import json
import random
from pathlib import Path
import pandas as pd

random.seed(42)

DATASET_DIR = Path("saas_pulse/dataset")
RAW_DIR = Path("saas_pulse/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load companies to map category
df_comp = pd.read_csv(DATASET_DIR / "companies.csv")
cat_map = dict(zip(df_comp["ticker"], df_comp["category"]))

# 2. Load 10-K paragraphs
paras_by_cat_fy = {}
with open(DATASET_DIR / "filings_paragraphs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)
        ticker = obj.get("ticker")
        cat = cat_map.get(ticker, "horizontal")
        fy = obj.get("fiscal_year", 2023)
        text = obj.get("text", "")
        # Filter for quality paragraph lengths (200 - 1200 chars)
        if 200 <= len(text) <= 1200:
            key = (cat, fy)
            if key not in paras_by_cat_fy:
                paras_by_cat_fy[key] = []
            paras_by_cat_fy[key].append(obj)

# Stratified sample 200 items across available categories and years
sample_10k = []
keys = list(paras_by_cat_fy.keys())
print(f"Total stratum keys (cat, fy): {len(keys)}")

# Calculate per-key allocation (~200 total)
target_per_key = max(1, 200 // len(keys))
for k in keys:
    pool = paras_by_cat_fy[k]
    k_sample = random.sample(pool, min(target_per_key + 2, len(pool)))
    sample_10k.extend(k_sample)

# Shuffle and trim to exactly 200
random.shuffle(sample_10k)
sample_10k = sample_10k[:200]

# Assign splits: 140 train, 20 val, 40 test
for i, item in enumerate(sample_10k):
    if i < 140:
        item["split"] = "train"
    elif i < 160:
        item["split"] = "val"
    else:
        item["split"] = "test"

with open(RAW_DIR / "unlabeled_sample_10k.json", "w", encoding="utf-8") as f:
    json.dump(sample_10k, f, indent=2)

print(f"Sampled {len(sample_10k)} 10-K paragraphs. Splits: 140 train, 20 val, 40 test.")

# 3. Load HN comments
comments_by_q = {}
with open(DATASET_DIR / "hn_comments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)
        q = obj.get("query", "saas")
        text = obj.get("text", "")
        if 150 <= len(text) <= 1500:
            if q not in comments_by_q:
                comments_by_q[q] = []
            comments_by_q[q].append(obj)

sample_hn = []
all_hn_pool = []
for q, pool in comments_by_q.items():
    all_hn_pool.extend(pool)

sample_hn = random.sample(all_hn_pool, min(60, len(all_hn_pool)))

for item in sample_hn:
    item["split"] = "test"

with open(RAW_DIR / "unlabeled_sample_hn.json", "w", encoding="utf-8") as f:
    json.dump(sample_hn, f, indent=2)

print(f"Sampled {len(sample_hn)} HN comments for prompt stance test set.")
