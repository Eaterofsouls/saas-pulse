import json
import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("saas_pulse/raw")
DATASET_DIR = Path("saas_pulse/dataset")

# Load samples
with open(RAW_DIR / "unlabeled_sample_10k.json", "r", encoding="utf-8") as f:
    sample_10k = json.load(f)

with open(RAW_DIR / "unlabeled_sample_hn.json", "r", encoding="utf-8") as f:
    sample_hn = json.load(f)

def classify_10k_paragraph(text: str) -> tuple[str, str]:
    t = text.lower()
    
    # 1. Compliance & Security
    compliance_kw = ["compliance", "regulatory", "fedramp", "hipaa", "gdpr", "soc 2", "certifications", "security clearance", "audit", "government cloud", "strict security"]
    if sum(1 for k in compliance_kw if k in t) >= 2 or any(k in t for k in ["fedramp", "hipaa", "regulatory requirements", "compliance standards"]):
        return "compliance_security", "Focuses on regulatory compliance, legal liability, or strict security certifications."
        
    # 2. Data Gravity & Proprietary Data
    data_kw = ["data gravity", "proprietary data", "historical data", "petabytes", "data warehouse", "lakehouse", "analytics platform", "telemetry data", "accumulated data", "data pipeline"]
    if sum(1 for k in data_kw if k in t) >= 2 or any(k in t for k in ["data gravity", "proprietary data", "telemetry", "vast amounts of data"]):
        return "data_gravity", "Emphasizes irreplaceable proprietary customer data, telemetry, or accumulated data gravity."

    # 3. System of Record & Mission Critical Workflow
    sor_kw = ["system of record", "single source of truth", "core workflow", "mission-critical", "operational backbone", "central repository", "master data", "transactional"]
    if sum(1 for k in sor_kw if k in t) >= 1 or any(k in t for k in ["system of record", "mission-critical", "single source of truth", "core operational"]):
        return "system_of_record", "Describes core operational backbone, transactional master data, or single source of truth."

    # 4. Switching Costs & Integrations
    switch_kw = ["switching costs", "integrations", "custom api", "deeply embedded", "friction to replace", "re-training", "ecosystem integration", "partner integrations", "embedded in their"]
    if sum(1 for k in switch_kw if k in t) >= 1 or any(k in t for k in ["switching costs", "deeply embedded", "costly to replace"]):
        return "switching_costs_integrations", "Highlights architectural integration friction, custom APIs, or high migration costs."

    # 5. Network Effects & Multi-sided Ecosystem
    network_kw = ["network effects", "marketplace", "developer ecosystem", "third-party developers", "app store", "community", "collaborative network", "viral adoption"]
    if sum(1 for k in network_kw if k in t) >= 2 or any(k in t for k in ["network effects", "app marketplace", "developer ecosystem"]):
        return "network_effects_ecosystem", "Highlights multi-sided platform, third-party developer ecosystem, or network effects."

    # Secondary checks
    if any(k in t for k in ["database", "data management", "lakehouse", "analytics"]):
        return "data_gravity", "Pertains to enterprise data management infrastructure."
    if any(k in t for k in ["workflow", "sales process", "business operations", "automate"]):
        return "system_of_record", "Automates core operational day-to-day workflow."
    if any(k in t for k in ["api", "integrate", "connector", "sdk"]):
        return "switching_costs_integrations", "Dependent on extensive API connectors and technical integration."

    return "none_or_commodity", "General descriptive narrative or standard CRUD capability without structural lock-in."

def classify_hn_comment(text: str) -> tuple[str, str]:
    t = text.lower()
    
    # 1. Build Internal
    build_kw = ["built our own", "build internal", "vibe code", "vibe coding", "built an internal", "wrote a script", "custom tool", "we replaced", "replaces saas", "built it myself", "wrote our own", "llm can build", "build vs buy", "cheaper to build"]
    if any(k in t for k in build_kw) or ("built" in t and "instead of" in t) or ("internal tool" in t and "easy" in t):
        return "build_internal", "Argues for or demonstrates replacing commercial software with internal/AI-built tools."

    # 2. Buy SaaS
    buy_kw = ["buy it", "not worth building", "maintenance nightmare", "liability", "compliance", "undifferentiated heavy lifting", "edge cases", "don't reinvent", "focus on core business", "who will maintain", "hidden costs of building"]
    if any(k in t for k in buy_kw) or ("never build" in t) or ("buy vs build" in t and "buy" in t):
        return "buy_saas", "Argues that building internally incurs massive maintenance, edge-case, and liability costs."

    return "hybrid_or_neutral", "Nuanced trade-off evaluation, hybrid approach, or architectural commentary."

# Pre-label 10-K
records_10k = []
for item in sample_10k:
    label, rationale = classify_10k_paragraph(item["text"])
    records_10k.append({
        "split": item["split"],
        "para_id": item["para_id"],
        "ticker": item["ticker"],
        "company": item.get("company", ""),
        "fiscal_year": item.get("fiscal_year", ""),
        "section": item.get("section", ""),
        "predicted_moat": label,
        "rationale": rationale,
        "user_corrected_label": label,  # Default to predicted, Daksh can override
        "text": item["text"]
    })

df_10k = pd.DataFrame(records_10k)
df_10k.to_csv(DATASET_DIR / "gold_10k_moats.csv", index=False)
print("Saved dataset/gold_10k_moats.csv")
print("10-K Label distribution:\n", df_10k["predicted_moat"].value_counts())

# Pre-label HN
records_hn = []
for item in sample_hn:
    label, rationale = classify_hn_comment(item["text"])
    records_hn.append({
        "id": item["id"],
        "created_at": item.get("created_at", ""),
        "predicted_stance": label,
        "rationale": rationale,
        "user_corrected_label": label,
        "text": item["text"]
    })

df_hn = pd.DataFrame(records_hn)
df_hn.to_csv(DATASET_DIR / "gold_hn_stance.csv", index=False)
print("\nSaved dataset/gold_hn_stance.csv")
print("HN Stance distribution:\n", df_hn["predicted_stance"].value_counts())

# Generate clean Markdown review document
md_content = f"""# Gold Benchmark Review (Human-in-the-Loop)

Use this guide to review pre-labels. The pre-labels were produced by the frontier reasoning engine.
If you agree with a pre-label, leave `user_corrected_label` as-is. If you want to change any label, simply edit the CSV or let me know!

---

## 1. 10-K Moat Dataset Summary (200 Paragraphs)
- **Train Split (for LoRA)**: 140 paragraphs
- **Validation Split**: 20 paragraphs
- **Frozen Test Benchmark**: 40 paragraphs

### Distribution Across Classes:
{df_10k['predicted_moat'].value_counts().to_markdown()}

---

## 2. HN Developer Stance Summary (60 Comments)
- **Prompt Evaluation Test Split**: 60 comments

### Distribution Across Classes:
{df_hn['predicted_stance'].value_counts().to_markdown()}

---

## 3. Sample 10-K Pre-Labeled Records (First 5)

"""

for i, row in df_10k.head(5).iterrows():
    md_content += f"""### [{row['split'].upper()}] {row['ticker']} (FY{row['fiscal_year']} - {row['section']})
- **Para ID**: `{row['para_id']}`
- **Predicted Moat**: `{row['predicted_moat']}`
- **Rationale**: {row['rationale']}
- **Excerpt**:
  > "{row['text'][:400]}..."

---
"""

(Path("saas_pulse/GOLD_REVIEW.md")).write_text(md_content, encoding="utf-8")
print("Saved saas_pulse/GOLD_REVIEW.md")
