"""
generate_kaggle_notebook.py
Generates the complete, self-contained, reproducible Jupyter Notebook
for the SaaS-Pulse project (Adani University GenAI Project by Daksh Chauhan).
Designed for Kaggle T4 GPU with fallback support.
"""

import json
import os
from pathlib import Path

def create_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.12"
            },
            "accelerator": "GPU"
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    def add_md(text):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in text.strip().split("\n")]
        })

    def add_code(text):
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in text.strip().split("\n")]
        })

    # Cell 1: Header / Title Markdown
    add_md("""# SaaS-Pulse: Which SaaS Moats Actually Hold Against AI?
### An Empirical NLP & Econometric Study on AI Commoditization, Moat Defensibility, and the 'Build vs Buy' Paradigm Shift
**Student**: Daksh Chauhan (7th Semester CS, Adani University)  
**Academic Requirement**: GenAI Semester Project (Original Dataset Collection, Curation, and GenAI Modeling)  
**Base Model**: `Qwen/Qwen2.5-1.5B-Instruct` (Quantized 4-bit / FP16)  
**Hardware Target**: Kaggle Free Tier (1x NVIDIA Tesla T4 GPU, 16GB VRAM)  
**Dataset**: Frozen multi-modal dataset (EDGAR 10-K filings, XBRL financials, Hacker News developer discourse, historical pricing, market equity returns)

---
### Executive Summary & Research Questions
In the era of frontier LLMs and AI-assisted development ("vibe coding"), software barriers to entry are eroding. Off-the-shelf SaaS point solutions face mounting pressure as engineering teams evaluate building bespoke internal tools over paying recurring seat licenses. 

This notebook investigates three empirical research questions:
1. **RQ1 (Moat Identification)**: Can a lightweight open-weight LLM (Qwen2.5-1.5B-Instruct) reliably classify economic moat claims in SEC 10-K filings across 6 defensibility archetypes? Does parameter-efficient fine-tuning (LoRA) outperform Zero-Shot and Few-Shot Chain-of-Thought (CoT) baselines on dense financial-legal text?
2. **RQ2 (Developer Sentiment & Stance)**: How do engineering teams actually react to SaaS pricing and AI tool substitution on Hacker News? What software categories are most vulnerable to being replaced by internal builds?
3. **RQ3 (Financial Ground Truth)**: Do companies asserting high-defensibility moats (e.g., Data Gravity, Systems of Record, Compliance) demonstrate measurable financial resilience (excess stock returns vs. the IGV software index and revenue growth)?
""")

    # Cell 2: Setup & Environment
    add_md("""## 1. Environment Setup & Dependency Installation
We check the environment, install required libraries (`peft`, `trl`, `transformers`, `accelerate`, `bitsandbytes`, `scikit-learn`, `scipy`), and initialize seeds for strict experimental reproducibility.
""")

    add_code("""# Setup & Dependency Checks
import sys
import subprocess
import os

print("Python version:", sys.version)

# Automatically install required packages if running in Kaggle or fresh virtual env
required_packages = [
    "transformers>=4.40.0",
    "peft>=0.10.0",
    "trl>=0.8.0",
    "accelerate>=0.29.0",
    "bitsandbytes>=0.43.0",
    "scikit-learn",
    "scipy",
    "matplotlib",
    "seaborn",
    "tabulate"
]

for pkg in required_packages:
    pkg_name = pkg.split(">=")[0]
    try:
        __import__(pkg_name)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re
from pathlib import Path

# Set seeds
def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(42)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Execution Device: {device}")
if device == "cuda":
    print(f"GPU Model: {torch.cuda.get_device_name(0)}")
    print(f"VRAM Available: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
""")

    # Cell 3: Data Ingestion & Path Detection
    add_md("""## 2. Frozen Dataset Ingestion & Validation
The dataset has been pre-collected and frozen to guarantee 100% reproducibility. We locate the dataset root directory, verify all key files, and load the dataframes into memory.
""")

    add_code("""# Locate dataset directory
possible_dirs = [
    Path("../input/saas-pulse-dataset/dataset"),
    Path("../input/saas-pulse/dataset"),
    Path("./dataset"),
    Path("../dataset"),
    Path("saas_pulse/dataset")
]

DATASET_DIR = None
for p in possible_dirs:
    if p.exists() and (p / "companies.csv").exists():
        DATASET_DIR = p
        break

if DATASET_DIR is None:
    # Try finding anywhere in parent or cwd
    candidates = list(Path(".").glob("**/dataset/companies.csv"))
    if candidates:
        DATASET_DIR = candidates[0].parent

if DATASET_DIR is None:
    raise FileNotFoundError("Could not find SaaS-Pulse dataset directory. Please verify dataset upload.")

print(f"Loaded Dataset Directory: {DATASET_DIR.resolve()}")

# Load core tables
df_companies = pd.read_csv(DATASET_DIR / "companies.csv")
df_revenue = pd.read_csv(DATASET_DIR / "revenue.csv")
df_stock = pd.read_csv(DATASET_DIR / "stock_performance.csv")
df_gold_10k = pd.read_csv(DATASET_DIR / "gold_10k_moats.csv")
df_gold_hn = pd.read_csv(DATASET_DIR / "gold_hn_stance.csv")

print(f"1. Companies: {len(df_companies)} records across {df_companies['category'].nunique()} categories")
print(f"2. Revenue: {len(df_revenue)} annual records covering {df_revenue['ticker'].nunique()} companies")
print(f"3. Stock Performance: {len(df_stock)} tickers tracked with 2023-2026 excess returns")
print(f"4. Gold 10-K Moat Dataset: {len(df_gold_10k)} stratified paragraphs")
print(f"5. Gold HN Developer Stance: {len(df_gold_hn)} stratified comments")
""")

    # Cell 4: Dataset Verification & Exploratory Data Analysis
    add_md("""## 3. Dataset Characteristics & Distribution Analysis
Let's inspect the distribution of the 6 economic moat archetypes and the developer sentiment categories.

**The 6 Economic Moat Archetypes**:
1. `system_of_record`: Core transactional database or single source of truth (ERP, CRM, general ledger) that is mission-critical.
2. `data_gravity`: Proprietary historical domain datasets, behavioral telemetry, and private enterprise corpora.
3. `switching_costs_integrations`: Deeply woven API web, bespoke ERP/IT connectors, and high retraining friction.
4. `compliance_security`: Regulated workflows (HIPAA, FedRAMP, SOC2, FINRA, GDPR) requiring high-assurance audit trails.
5. `network_effects_ecosystem`: Multi-sided marketplaces, app exchanges, shared developer or user communities.
6. `none_or_commodity`: Standard operational UI, generic point-solution workflows, boilerplate risk factors.
""")

    add_code("""# Visualize Distributions
plt.figure(figsize=(14, 5))

# Subplot 1: 10-K Moat Classes
plt.subplot(1, 2, 1)
moat_counts = df_gold_10k['predicted_moat'].value_counts()
sns.barplot(x=moat_counts.values, y=moat_counts.index, palette="viridis")
plt.title("Gold 10-K Moat Distribution (N=200)", fontsize=12, fontweight='bold')
plt.xlabel("Sample Count")

# Subplot 2: HN Developer Stance
plt.subplot(1, 2, 2)
stance_counts = df_gold_hn['predicted_stance'].value_counts()
sns.barplot(x=stance_counts.values, y=stance_counts.index, palette="mako")
plt.title("Gold HN Developer Stance Distribution (N=60)", fontsize=12, fontweight='bold')
plt.xlabel("Sample Count")

plt.tight_layout()
plt.show()

# Display Split Breakdown for 10-K Moat Classification
print("10-K Split Distribution:")
print(df_gold_10k['split'].value_counts())
print("\n10-K Category Breakdown:")
print(df_gold_10k['category'].value_counts())
""")

    # Cell 5: Model Loading
    add_md("""## 4. LLM Setup: Qwen2.5-1.5B-Instruct
We utilize **Qwen2.5-1.5B-Instruct**, a high-efficiency small language model (SLM) that delivers strong reasoning capabilities within Kaggle's 16GB T4 VRAM budget. When a GPU is present, we load the base weights in 4-bit precision via `bitsandbytes` to minimize memory footprint (< 2.5 GB VRAM) while leaving ample headroom for LoRA activations.
""")

    add_code("""from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

if device == "cuda":
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
else:
    print("Running in CPU / Emulation mode. Loading float32...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="cpu",
        torch_dtype=torch.float32,
        trust_remote_code=True
    )

print("Model successfully loaded onto:", model.device)
""")

    # Cell 6: Task 1 - Zero-Shot & Few-Shot CoT Benchmarks
    add_md("""## 5. Task 1: Moat Classification Benchmark
We evaluate the frozen test set ($N=40$ stratified 10-K paragraphs) across three paradigms:
1. **Zero-Shot Prompting**: Direct classification given the taxonomy definitions.
2. **Few-Shot Chain-of-Thought (CoT)**: Demonstrating multi-step economic reasoning prior to emitting the label.
3. **LoRA Fine-Tuning**: Supervised fine-tuning on the 140 training examples.

### Taxonomy Definitions Provided in Prompt
- `system_of_record`: Core mission-critical database (e.g. ERP, CRM, General Ledger).
- `data_gravity`: Proprietary historical data, behavioral telemetry, high data volume.
- `switching_costs_integrations`: Deeply woven API integrations, customized workflows, migration friction.
- `compliance_security`: Regulated compliance, FedRAMP, HIPAA, SOC2, security audits.
- `network_effects_ecosystem`: Multi-sided marketplace, developer ecosystem, app exchanges.
- `none_or_commodity`: Generic SaaS features, commoditized point tools, boilerplate risk factors.
""")

    add_code("""# Extract test and train subsets
df_test = df_gold_10k[df_gold_10k['split'] == 'test'].copy().reset_index(drop=True)
df_train = df_gold_10k[df_gold_10k['split'] == 'train'].copy().reset_index(drop=True)
df_val = df_gold_10k[df_gold_10k['split'] == 'val'].copy().reset_index(drop=True)

VALID_LABELS = [
    'system_of_record',
    'data_gravity',
    'switching_costs_integrations',
    'compliance_security',
    'network_effects_ecosystem',
    'none_or_commodity'
]

SYSTEM_PROMPT = \"\"\"You are an expert financial and software industry analyst evaluating corporate 10-K filings.
Classify the primary economic moat or defensibility mechanism asserted in the provided 10-K paragraph.
Choose EXACTLY ONE label from the following taxonomy:
- system_of_record
- data_gravity
- switching_costs_integrations
- compliance_security
- network_effects_ecosystem
- none_or_commodity

Respond ONLY with a JSON object: {"rationale": "<brief explanation>", "label": "<selected_label>"}\"\"\"

def extract_label_from_text(raw_text):
    text = raw_text.strip()
    # Try parsing json
    try:
        match = re.search(r'\\{.*\\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            if 'label' in data and data['label'] in VALID_LABELS:
                return data['label']
    except Exception:
        pass
    
    # Fallback keyword matching
    for lbl in VALID_LABELS:
        if lbl in text:
            return lbl
    return 'none_or_commodity'

# Inference helper
def run_llm_inference(prompt_messages, max_new_tokens=120):
    input_ids = tokenizer.apply_chat_template(prompt_messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    input_ids = input_ids.to(model.device)
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id
        )
    generated_tokens = output[0][input_ids.shape[1]:]
    return tokenizer.decode(generated_tokens, skip_special_tokens=True)
""")

    # Cell 7: Running Zero-Shot & Few-Shot CoT
    add_md("""### Running Zero-Shot and Few-Shot CoT on Test Set""")
    add_code("""from tqdm import tqdm

# Prepare Few-Shot Demonstrations (drawn from df_train)
few_shot_examples = [
    {
        "role": "user",
        "content": f"Company: Salesforce | Category: horizontal\\nText: {df_train[df_train['predicted_moat']=='system_of_record'].iloc[0]['text'][:300]}..."
    },
    {
        "role": "assistant",
        "content": '{"rationale": "Acts as the enterprise central database for customer relationships and mission-critical workflows.", "label": "system_of_record"}'
    },
    {
        "role": "user",
        "content": f"Company: Snowflake | Category: data/infra\\nText: {df_train[df_train['predicted_moat']=='data_gravity'].iloc[0]['text'][:300]}..."
    },
    {
        "role": "assistant",
        "content": '{"rationale": "Data accumulation in petabyte-scale data lakes creates high egress costs and retention gravity.", "label": "data_gravity"}'
    },
    {
        "role": "user",
        "content": f"Company: CrowdStrike | Category: security\\nText: {df_train[df_train['predicted_moat']=='compliance_security'].iloc[0]['text'][:300]}..."
    },
    {
        "role": "assistant",
        "content": '{"rationale": "High-assurance security architecture protecting regulated enterprise infrastructure.", "label": "compliance_security"}'
    }
]

preds_zero_shot = []
preds_few_shot = []

print(f"Benchmarking Zero-Shot and Few-Shot CoT on {len(df_test)} test paragraphs...")

for idx, row in tqdm(df_test.iterrows(), total=len(df_test)):
    user_msg = f"Company: {row['company']} | Category: {row['category']}\\nText: {row['text']}"
    
    # 1. Zero-shot
    zs_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]
    out_zs = run_llm_inference(zs_messages, max_new_tokens=90)
    preds_zero_shot.append(extract_label_from_text(out_zs))
    
    # 2. Few-shot CoT
    fs_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *few_shot_examples,
        {"role": "user", "content": user_msg}
    ]
    out_fs = run_llm_inference(fs_messages, max_new_tokens=90)
    preds_few_shot.append(extract_label_from_text(out_fs))

df_test['pred_zero_shot'] = preds_zero_shot
df_test['pred_few_shot'] = preds_few_shot
print("Zero-shot & Few-shot evaluation complete.")
""")

    # Cell 8: Parameter-Efficient Fine-Tuning (LoRA)
    add_md("""## 6. Supervised Fine-Tuning via LoRA
We fine-tune Qwen2.5-1.5B on the 140 training paragraphs using Hugging Face `peft` and `trl.SFTTrainer`.
We configure Low-Rank Adaptation (LoRA) on the attention projection matrices (`q_proj`, `k_proj`, `v_proj`, `o_proj`) with:
- $r = 16$
- $\\alpha = 32$
- Dropout $= 0.05$
- Target modules: Attention projections
""")

    add_code("""from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import Dataset

# Format training and validation data into ChatML prompt strings
def format_chat_record(row):
    user_content = f"Company: {row['company']} | Category: {row['category']}\\nText: {row['text']}"
    assistant_content = json.dumps({"rationale": row['rationale'], "label": row['predicted_moat']})
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": assistant_content}
    ]
    return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}

train_dataset = Dataset.from_list([format_chat_record(row) for _, row in df_train.iterrows()])
val_dataset = Dataset.from_list([format_chat_record(row) for _, row in df_val.iterrows()])

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
)

# Training configurations
training_args = SFTConfig(
    output_dir="./qwen_moat_lora",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=(device == "cuda"),
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="no",
    report_to="none",
    dataset_text_field="text",
    max_seq_length=512
)

print("Configuring LoRA Fine-Tuning...")
if device == "cuda":
    model.gradient_checkpointing_enable()
    peft_model = prepare_model_for_kbit_training(model)
    peft_model = get_peft_model(peft_model, peft_config)
    peft_model.print_trainable_parameters()
    
    trainer = SFTTrainer(
        model=peft_model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        peft_config=peft_config,
        args=training_args,
    )
    print("Beginning LoRA Training (3 Epochs)...")
    trainer.train()
    print("LoRA Fine-Tuning Complete.")
    eval_model = peft_model
else:
    print("CPU mode: Skipping actual gradient updates; using base model for pipeline verification.")
    eval_model = model
""")

    # Cell 9: Evaluating LoRA on Test Set
    add_md("""### Evaluating LoRA Fine-Tuned Model on Test Set""")
    add_code("""preds_lora = []
print("Evaluating LoRA on Test Set...")

for idx, row in tqdm(df_test.iterrows(), total=len(df_test)):
    user_msg = f"Company: {row['company']} | Category: {row['category']}\\nText: {row['text']}"
    lora_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]
    input_ids = tokenizer.apply_chat_template(lora_messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(eval_model.device)
    with torch.no_grad():
        output = eval_model.generate(
            input_ids,
            max_new_tokens=90,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id
        )
    gen_text = tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
    preds_lora.append(extract_label_from_text(gen_text))

df_test['pred_lora'] = preds_lora
""")

    # Cell 10: Statistical Metrics, Confidence Intervals & Bootstrapping
    add_md("""## 7. Statistical Evaluation & Confidence Intervals
To adhere to rigorous academic standards, we report:
- **Macro-Averaged Precision, Recall, and F1-Score**
- **Wilson Score 95% Confidence Intervals** for Accuracy
- **1,000-Iteration Bootstrap Resampling** to compute empirical 95% Confidence Intervals for Macro-F1.
""")

    add_code("""from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import scipy.stats as stats

y_true = df_test['predicted_moat'].values

# Wilson Score Interval
def wilson_score_interval(correct, total, z=1.96):
    p = correct / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    spread = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denom
    return (max(0.0, centre - spread), min(1.0, centre + spread))

# Bootstrap 95% CI for Macro-F1
def bootstrap_macro_f1_ci(y_true, y_pred, n_bootstraps=1000, alpha=0.05):
    bootstrapped_f1s = []
    n = len(y_true)
    for _ in range(n_bootstraps):
        indices = np.random.choice(n, size=n, replace=True)
        sample_true = y_true[indices]
        sample_pred = y_pred[indices]
        bootstrapped_f1s.append(f1_score(sample_true, sample_pred, average='macro', zero_division=0))
    low = np.percentile(bootstrapped_f1s, (alpha / 2) * 100)
    high = np.percentile(bootstrapped_f1s, (1 - alpha / 2) * 100)
    return (low, high)

results = []
for name, col in [("Zero-Shot", "pred_zero_shot"), ("Few-Shot CoT", "pred_few_shot"), ("LoRA (Fine-Tuned)", "pred_lora")]:
    y_pred = df_test[col].values
    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    prec_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
    
    acc_ci = wilson_score_interval(int(acc * len(y_true)), len(y_true))
    f1_ci = bootstrap_macro_f1_ci(y_true, y_pred, n_bootstraps=1000)
    
    results.append({
        "Method": name,
        "Accuracy": f"{acc:.3f} [{acc_ci[0]:.2f}, {acc_ci[1]:.2f}]",
        "Macro-Precision": f"{prec_macro:.3f}",
        "Macro-Recall": f"{rec_macro:.3f}",
        "Macro-F1": f"{f1_macro:.3f} [{f1_ci[0]:.2f}, {f1_ci[1]:.2f}]"
    })

df_results = pd.DataFrame(results)
print("=== MOAT CLASSIFICATION BENCHMARK RESULTS (N=40 Test) ===")
print(df_results.to_markdown(index=False))

# Confusion Matrix for Best Model
best_preds = df_test['pred_lora'].values
cm = confusion_matrix(y_true, best_preds, labels=VALID_LABELS)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=VALID_LABELS, yticklabels=VALID_LABELS)
plt.title("Confusion Matrix: LoRA Model on 10-K Moats", fontsize=12, fontweight='bold')
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
""")

    # Cell 11: Task 2 - Hacker News Developer Stance Analysis
    add_md("""## 8. Task 2: Developer Stance on "Build vs Buy" (Hacker News)
We evaluate developer discussions ($N=60$ gold test comments) to quantify developer appetite for replacing commercial SaaS with internal tools ("vibe coded" or built with low-code/open-source tools like Appsmith, Supabase, Budibase).

**Stance Taxonomy**:
- `build_internal`: Replaced or actively building bespoke internal tooling instead of paying for commercial SaaS.
- `buy_saas`: Maintained commercial SaaS subscription due to compliance, security, maintenance overhead, or enterprise requirements.
- `hybrid_or_neutral`: Nuanced evaluation, weighing trade-offs, or partial tool migration.
""")

    add_code("""HN_SYSTEM_PROMPT = \"\"\"You are an expert software engineering researcher analyzing developer discourse on Hacker News.
Classify the author's stance regarding buying SaaS vs. building internal tools.
Taxonomy:
- build_internal
- buy_saas
- hybrid_or_neutral

Respond ONLY with a JSON object: {"rationale": "<explanation>", "stance": "<selected_stance>"}\"\"\"

VALID_STANCES = ['build_internal', 'buy_saas', 'hybrid_or_neutral']

def extract_stance_from_text(raw_text):
    text = raw_text.strip()
    try:
        match = re.search(r'\\{.*\\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            if 'stance' in data and data['stance'] in VALID_STANCES:
                return data['stance']
    except Exception:
        pass
    for s in VALID_STANCES:
        if s in text:
            return s
    return 'hybrid_or_neutral'

preds_hn_zs = []
for idx, row in tqdm(df_gold_hn.iterrows(), total=len(df_gold_hn)):
    messages = [
        {"role": "system", "content": HN_SYSTEM_PROMPT},
        {"role": "user", "content": f"Comment: {row['text']}"}
    ]
    gen_text = run_llm_inference(messages, max_new_tokens=60)
    preds_hn_zs.append(extract_stance_from_text(gen_text))

df_gold_hn['pred_stance'] = preds_hn_zs
y_true_hn = df_gold_hn['predicted_stance'].values
y_pred_hn = df_gold_hn['pred_stance'].values

acc_hn = accuracy_score(y_true_hn, y_pred_hn)
f1_hn = f1_score(y_true_hn, y_pred_hn, average='macro', zero_division=0)
print(f"Hacker News Stance Accuracy: {acc_hn:.3f}")
print(f"Hacker News Stance Macro-F1: {f1_hn:.3f}")
print("\\nClassification Report:")
print(classification_report(y_true_hn, y_pred_hn, target_names=VALID_STANCES))
""")

    # Cell 12: Econometric & Moat Linkage Analysis
    add_md("""## 9. Econometric Linkage: Do Moats Protect Market Value?
We link our qualitative moat findings with empirical financial data:
1. **Equity Returns**: 2023-2026 total return and excess return over the iShares Expanded Tech-Software Sector ETF (`IGV`, +118.31%).
2. **Revenue Growth**: Annual US-GAAP YoY revenue growth from official XBRL filings.
3. **Moat Concentration**: We compute the proportion of high-defensibility moats (Systems of Record, Data Gravity, Compliance) by sector.

### Statistical Caveat: Descriptive vs. Causal Link
*Correlation is not causation*. We compute the **Spearman Rank Correlation** ($\\rho$) to test monotonic association without assuming linearity or normality, while openly acknowledging survivorship bias and interest-rate confounders.
""")

    add_code("""# Merge Stock and Financial metrics with Company metadata
df_merged = df_companies.merge(df_stock, on='ticker', how='inner')
df_rev_latest = df_revenue.sort_values(by='fiscal_year').groupby('ticker').last().reset_index()
df_merged = df_merged.merge(df_rev_latest[['ticker', 'revenue_growth_pct', 'revenue_usd']], on='ticker', how='left')

# Filter valid tickers
df_valid_stocks = df_merged[df_merged['status'] == 'ok'].copy()

# Compute Category-Level Excess Return vs IGV
cat_perf = df_valid_stocks.groupby('category_x')['excess_return_vs_igv'].agg(['count', 'median', 'mean']).sort_values(by='median', ascending=False)
print("=== CATEGORY PERFORMANCE: EXCESS RETURN VS IGV (+118.31% BENCHMARK) ===")
print(cat_perf.to_markdown())

# Plot Category Median Excess Returns
plt.figure(figsize=(10, 5))
sns.boxplot(data=df_valid_stocks, x='category_x', y='excess_return_vs_igv', palette='Set2')
plt.title("2023-2026 Excess Return vs IGV Software Index Across SaaS Archetypes", fontsize=12, fontweight='bold')
plt.xlabel("SaaS Category")
plt.ylabel("Excess Return vs IGV (%)")
plt.ylim(-250, 400) # trim extreme outliers for visual clarity
plt.axhline(0, color='red', linestyle='--', label='IGV Software Benchmark (+118.31%)')
plt.legend()
plt.tight_layout()
plt.show()

# Spearman Rank Correlation between YoY Growth and Excess Return
corr, p_value = stats.spearmanr(df_valid_stocks['revenue_growth_pct'].dropna(), df_valid_stocks['excess_return_vs_igv'].dropna())
print(f"Spearman Rank Correlation (YoY Growth vs. Excess Return): rho = {corr:.3f}, p = {p_value:.4f}")
""")

    # Cell 13: Honest Limitations & Faculty Discussion
    add_md("""## 10. Academic Honesty & Methodological Limitations
To maintain high academic integrity during presentation defense, the following limitations are formally recognized:

1. **Self-Serving SEC 10-K PR Language**: 10-K Item 1 descriptions represent management's favorable framing of competitive moats rather than objective reality.
2. **Developer Selection Bias on Hacker News**: Hacker News disproportionately represents early-stage software engineers, infra architects, and indie builders who possess higher technical ability to build internal tools than the average non-technical enterprise employee.
3. **Survivorship Bias**: Our sample of 100 SaaS companies includes entities actively filing with the SEC between 2022 and 2025; distressed or acquired companies that failed post-2022 are underrepresented.
4. **Descriptive Correlation vs. Causation**: Macro factors (Fed interest rates, enterprise IT budget compression, multiple compression) confounded stock performance alongside AI commoditization fears.
5. **Sample Size Constraints**: The hand-audited test set ($N=40$) requires reporting Wilson score and bootstrap confidence intervals to avoid overclaiming statistical power.
""")

    # Save notebook
    out_path = Path("saas_pulse/saas_pulse_experiment.ipynb")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Successfully generated Kaggle notebook at: {out_path.resolve()}")

if __name__ == "__main__":
    create_notebook()
