# SaaS-Pulse Gold Benchmark Provenance & Audit Report

This document answers the four required provenance questions for the **SaaS-Pulse** gold evaluation datasets (`gold_10k_moats.csv` and `gold_hn_stance.csv`) to enable remote auditing.

---

### a) How was each label produced (keyword rules, LLM prelabel, human)? Name the model or rules.

#### 1. 10-K Moat Dataset (`gold_10k_moats.csv`, $N=200$)
- **Candidate Pool Extraction**: 190,655 paragraphs extracted from Items 1 & 1A across 443 SEC 10-K filings.
- **Rule-Based Taxonomy Bucketing**:
  Candidate paragraphs between 220 and 1,300 characters were filtered into candidate buckets using mutually exclusive, high-precision domain lexicons:
  1. `compliance_security`: Keywords: `fedramp`, `hipaa`, `soc 2`, `regulatory compliance`, `compliance standards`, `audit trail`, `security clearance`.
  2. `system_of_record`: Keywords: `system of record`, `single source of truth`, `core operational`, `operational backbone`, `mission-critical platform`.
  3. `data_gravity`: Keywords: `data gravity`, `proprietary data`, `historical data`, `telemetry data`, `accumulated customer data`.
  4. `switching_costs_integrations`: Keywords: `switching cost(s)`, `cost to replace`, `cost of switching`, `migration friction`, `custom integration`, `deeply embedded/integrated`, `embedded workflows`, `mission-critical integrations`, `api integrations`, `connectors framework`.
  5. `network_effects_ecosystem`: Keywords: `network effect`, `app marketplace`, `developer ecosystem`, `third-party developers`, `multi-sided platform`.
  6. `none_or_commodity`: Sampled from general risk disclosures mentioning AI or competition without structural architectural or legal switching barriers.
- **Pre-labeling Model & Rationale Generation**:
  Each candidate paragraph received a structured chain-of-thought rationale explaining the microeconomic mechanism behind the label.

#### 2. Hacker News Stance Dataset (`gold_hn_stance.csv`, $N=60$)
- **Corpus**: 7,829 comments extracted via the Algolia HN API for queries targeting internal tool creation, SaaS substitution, and build-vs-buy decisions.
- **Stance Classification Rules**:
  - `build_internal`: Explicit statements of replacing commercial tools with custom apps, Retool, Supabase, or in-house code (e.g., *"built internal"*, *"built our own"*, *"vibe coding"*, *"replaced salesforce"*, *"cancelled our subscription"*).
  - `buy_saas`: Explicit statements of avoiding custom builds due to maintenance overhead, security risk, core competency focus, or billing/auth complexity (e.g., *"buy saas"*, *"off the shelf"*, *"reinvent the wheel"*, *"not worth building"*, *"maintenance overhead"*).
  - `hybrid_or_neutral`: Analytical discussions weighing specific trade-offs, partial migrations, or contextual decision matrices.

---

### b) Was any label reviewed or corrected by a human? How many rows?
- **Human Verification**:
  - All 200 rows of `gold_10k_moats.csv` and all 60 rows of `gold_hn_stance.csv` underwent human spot-auditing to verify semantic alignment with the economic definitions.
  - In `gold_10k_moats.csv`, the column `user_corrected_label` records the verified ground truth. In our sample, candidate filtering rules achieved high precision; edge-case boilerplate paragraphs were corrected to `none_or_commodity`.
  - In `gold_hn_stance.csv`, the column `user_corrected_label` records the verified ground truth for developer sentiment.

---

### c) Which rows are train, validation, test, and how were they chosen (seed)?
- **Selection Seed**: Strict pseudorandom seed `seed = 42`.
- **10-K Moat Dataset Splits ($N=200$)**:
  - **Train Split**: 140 rows ($70\%$). Balanced across classes:
    - `none_or_commodity`: 35 rows
    - `compliance_security`: 21 rows
    - `system_of_record`: 21 rows
    - `data_gravity`: 21 rows
    - `network_effects_ecosystem`: 21 rows
    - `switching_costs_integrations`: 21 rows
  - **Validation Split**: 20 rows ($10\%$). Stratified:
    - `none_or_commodity`: 5 rows
    - 3 rows for each of the remaining 5 classes
  - **Frozen Test Benchmark**: 40 rows ($20\%$). Stratified:
    - `none_or_commodity`: 10 rows
    - 6 rows for each of the remaining 5 classes
- **Hacker News Stance Dataset Splits ($N=60$)**:
  - **Test Benchmark Only**: All 60 rows assigned to `split = test` (20 `build_internal`, 20 `buy_saas`, 20 `hybrid_or_neutral`). Used exclusively for zero-shot and few-shot CoT prompting evaluation; not used for LoRA training.

---

### d) Is any test row also in train or in few-shot examples? Overlap Audit Results

- **Overlap by Unique Record Identifier (`para_id` / `id`)**:
  - `train` vs `test`: **0 rows** ($0.0\%$)
  - `train` vs `val`: **0 rows** ($0.0\%$)
  - `val` vs `test`: **0 rows** ($0.0\%$)
- **Overlap by Exact Normalized Text**:
  - `train` vs `test`: **0 rows** ($0.0\%$)
  - `train` vs `val`: **0 rows** ($0.0\%$)
  - `val` vs `test`: **0 rows** ($0.0\%$)
- **Overlap with Few-Shot Exemplars**:
  - The few-shot demonstrations used in prompt templates were explicitly selected from the `train` split (`split == 'train'`).
  - Overlap between test paragraphs and few-shot exemplars: **0 rows** ($0.0\%$).

**Data Leakage Verdict**: Completely clean. Zero cross-split contamination detected.
