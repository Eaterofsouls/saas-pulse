# Hacker News Stance Classification Methodology

This document details how developer sentiment towards building internal tools versus buying commercial SaaS was extracted, measured, and verified for **SaaS-Pulse**.

---

## 1. Corpus Scope & Pacing
- **Source**: Hacker News via Algolia REST API (`hn.algolia.com/api/v1/search_by_date`).
- **Temporal Coverage**: 2023-01-01 to 2026-10-28.
- **Search Query Seeds**:
  - `"internal tools AI"`
  - `"replace Salesforce with"`
  - `"vibe coded internal tool"`
  - `"build vs buy AI"`
  - Mentions of popular low-code / internal tooling stacks: Appsmith, Budibase, Retool, Supabase.
- **Total Deduplicated Records**: 7,829 comments/stories ($\ge 80$ characters).
- **Privacy Protocol**: Author usernames pseudonymized using SHA-256 (`author_hash = sha256(username)`).

---

## 2. Stance Taxonomy Definitions
Each comment is evaluated against three mutually exclusive stances:
1. `build_internal`: The author advocates, reports, or plans the replacement of a commercial SaaS product with a custom in-house build, an LLM-assisted tool ("vibe coding"), or an open-source low-code framework.
2. `buy_saas`: The author argues against in-house builds, citing maintenance debt, non-core distractions, regulatory compliance, billing/tax complexity, or vendor security guarantees.
3. `hybrid_or_neutral`: The author presents a nuanced trade-off analysis, recommends selective hybrid adoption, or poses questions without taking a firm side.

---

## 3. Quantitative Counts & Baseline Metrics
- **Corpus-Level Keyword Distribution**:
  - Discarding general inquiries, comments taking a decisive stance show high developer propensity toward building internal tools for non-core workflows (CRUD, internal admin, simple ticketing) while strongly defending buying for billing, auth, and regulated logs.
- **Gold Benchmark Dataset (`dataset/gold_hn_stance.csv`)**:
  - Sample Size: $N=60$ comments.
  - Stratification: Exactly 20 `build_internal`, 20 `buy_saas`, 20 `hybrid_or_neutral`.
- **System Prompt Used for LLM Evaluation**:
```json
{
  "system_prompt": "You are an expert software engineering researcher analyzing developer discourse on Hacker News.\nClassify the author's stance regarding buying SaaS vs. building internal tools.\nTaxonomy:\n- build_internal\n- buy_saas\n- hybrid_or_neutral\n\nRespond ONLY with a JSON object: {\"rationale\": \"<explanation>\", \"stance\": \"<selected_stance>\"}"
}
```
- **Realized Benchmark Results**:
  - Evaluated on Kaggle GPU using `Qwen2.5-1.5B-Instruct`.
  - Exact performance numbers are dynamically exported to `metrics.json` and mirrored in the runs directory.
