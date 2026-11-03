# SaaS-Pulse Gold Benchmark Review Document

> **STATUS (2026-11-02):**
> - **140 Train Rows**: Generated via keyword heuristic rules (`label_source = keyword_rule`).
> - **60 Val/Test Rows**: Reviewed by Claude Opus 5.5 and approved by student Daksh Chauhan (`label_source = llm_reviewed_student_approved`). 8 rows marked `exclude` (5 test, 3 val) are dropped from benchmark scoring, leaving 35 evaluated test rows and 17 evaluated val rows. Agreement on evaluated rows = 65.38% (Cohen's $\kappa = 0.5742$).
> - **Hacker News (60 Rows)**: Unreviewed; labels are keyword-rule generated (`label_source = keyword_rule`).

This document records the exact distributions and sample records of the gold evaluation sets for **SaaS-Pulse**.

---

## 1. 10-K Moat Dataset Summary (200 Stratified Paragraphs)
- **Train Split (LoRA SFT)**: 140 paragraphs (`label_source = keyword_rule`)
- **Validation Split**: 20 paragraphs (3 excluded -> 17 evaluated, `label_source = llm_reviewed_student_approved`)
- **Frozen Test Benchmark**: 40 paragraphs (5 excluded -> 35 evaluated, `label_source = llm_reviewed_student_approved`)
- **Train-Test Text Overlap**: STRICTLY 0 (Verified)

### Class Breakdown (Pre-Review Keyword Rules):
| predicted_moat               |   count |
|:-----------------------------|--------:|
| none_or_commodity            |      50 |
| compliance_security          |      30 |
| system_of_record             |      30 |
| data_gravity                 |      30 |
| network_effects_ecosystem    |      30 |
| switching_costs_integrations |      30 |

### Evaluated Test Set Class Breakdown (Final Approved Labels, N=35):
| final_label                  |   count |
|:-----------------------------|--------:|
| none_or_commodity            |      18 |
| network_effects_ecosystem    |       6 |
| system_of_record             |       5 |
| switching_costs_integrations |       3 |
| compliance_security          |       2 |
| data_gravity                 |       2 |

---

## 2. Hacker News Stance Dataset Summary (60 Stratified Comments)
- **Prompt Evaluation Benchmark (Test Only)**: 60 comments (`label_source = keyword_rule`)

### Class Breakdown:
| predicted_stance   |   count |
|:-------------------|--------:|
| build_internal     |      20 |
| buy_saas           |      20 |
| hybrid_or_neutral  |      20 |

---

## 3. Sample 10-K Records (With Approved Final Labels)

### [TRAIN] FLYW (Flywire Corp) - FY2025
- **Para ID**: `0001193125-26-067540_Item1_26`
- **Rule Label**: `compliance_security` | **Final Label**: `compliance_security` | **Source**: `keyword_rule`
- **Text Excerpt**:
  > "At the core of our business is our network of global, regional and local banking partners which we have been strategically expanding for over a decade. With a single connection to Flywire, our clients have access to a unique set of payment methods including banks, third-party payment providers, payment networks and digital wallets..."

---
### [TEST] RNG (RingCentral, Inc.) - FY2025
- **Para ID**: `0001384905-26-000021_Item1A_22`
- **Rule Label**: `compliance_security` | **Final Label**: `none_or_commodity` | **Source**: `llm_reviewed_student_approved`
- **Audit Note**: Reclassified from compliance to commodity because paragraph discusses generic legal boilerplate proceedings rather than proprietary regulatory compliance defensibility.
- **Text Excerpt**:
  > "We are and may be in the future subject to certain legal proceedings and from time to time may be involved in a variety of claims, lawsuits, investigations, and proceedings relating to contractual disputes, intellectual property rights, employment matters, regulatory compliance matters..."

---
### [TEST] HUBS (HubSpot, Inc.) - FY2024
- **Para ID**: `0001404655-24-000013_Item1_37`
- **Rule Label**: `network_effects_ecosystem` | **Final Label**: `network_effects_ecosystem` | **Source**: `llm_reviewed_student_approved`
- **Audit Note**: Confirmed ecosystem network effect due to active third-party app marketplace and developer integrations.
- **Text Excerpt**:
  > "Our platform is further enhanced by our App Marketplace, which features over 1,500 integrations built by third-party developers, enabling customers to easily connect HubSpot with their existing technology stack..."

---

## 4. Methodological Note on Inter-Annotator Agreement
- **Observed Agreement**: 65.38% on evaluated val/test items (34 agreed, 18 changed).
- **Cohen's Kappa**: $\kappa = 0.5742$ (moderate agreement).
- **Exclusions**: 8 rows dropped from evaluation (marked `exclude`).
- Full audit log available in `dataset/review/REVIEW_AUDIT.md`.
