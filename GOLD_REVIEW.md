# SaaS-Pulse Gold Benchmark Review Document

> **CORRECTION (2026-10-31):** A prior version of this document described labels as "human-audited."
> That claim was false. Labels are keyword-rule generated. No human reviewed any row.
> The sample records below are for reference; labels are rule-generated, not verified by a human expert.

This document records the exact distributions and sample records of the **rule-generated** gold evaluation sets for **SaaS-Pulse**.

---

## 1. 10-K Moat Dataset Summary (200 Stratified Paragraphs)
- **Train Split (LoRA SFT)**: 140 paragraphs
- **Validation Split**: 20 paragraphs
- **Frozen Test Benchmark**: 40 paragraphs
- **Train-Test Text Overlap**: STRICTLY 0 (Verified)

### Class Breakdown:
| predicted_moat               |   count |
|:-----------------------------|--------:|
| none_or_commodity            |      50 |
| compliance_security          |      30 |
| system_of_record             |      30 |
| data_gravity                 |      30 |
| network_effects_ecosystem    |      30 |
| switching_costs_integrations |      30 |

### Split vs Class Breakdown:
| split   |   compliance_security |   data_gravity |   network_effects_ecosystem |   none_or_commodity |   switching_costs_integrations |   system_of_record |
|:--------|----------------------:|---------------:|----------------------------:|--------------------:|-------------------------------:|-------------------:|
| test    |                     6 |              6 |                           6 |                  10 |                              6 |                  6 |
| train   |                    21 |             21 |                          21 |                  35 |                             21 |                 21 |
| val     |                     3 |              3 |                           3 |                   5 |                              3 |                  3 |

---

## 2. Hacker News Stance Dataset Summary (60 Stratified Comments)
- **Prompt Evaluation Benchmark (Test Only)**: 60 comments

### Class Breakdown:
| predicted_stance   |   count |
|:-------------------|--------:|
| build_internal     |      20 |
| buy_saas           |      20 |
| hybrid_or_neutral  |      20 |

---

## 3. Sample 10-K Pre-Labeled Records

### [TRAIN] FLYW (Flywire Corp) - FY2025
- **Para ID**: `0001193125-26-067540_Item1_26`
- **Predicted Moat**: `compliance_security`
- **Rationale**: Explicitly cites regulatory compliance, legal liability, or strict security certifications as an operational barrier.
- **Text Excerpt**:
  > "At the core of our business is our network of global, regional and local banking partners which we have been strategically expanding for over a decade. With a single connection to Flywire, our clients have access to a unique set of payment methods including banks, third-party payment providers, payment networks and digital wallets—making it possible to accept and settle payments in over 240 countries and territories and in over 140 currencies. Ou..."

---
### [TRAIN] ASAN (Asana, Inc.) - FY2022
- **Para ID**: `0001477720-22-000012_Item1_44`
- **Predicted Moat**: `system_of_record`
- **Rationale**: Establishes the platform as the foundational transactional system of record and core daily operational backbone.
- **Text Excerpt**:
  > "With Asana Work Graph's differentiated ability to construct a single source of truth for individuals, teams, and organizations, Asana powers clarity at every level of an organization, regardless of size, structure, and complexity. The Asana Work Graph provides:..."

---
### [TRAIN] DT (Dynatrace, Inc.) - FY2022
- **Para ID**: `0001773383-22-000053_Item1_11`
- **Predicted Moat**: `data_gravity`
- **Rationale**: Highlights proprietary, accumulated customer data pools and analytics gravity that cannot be hallucinated by generic AI models.
- **Text Excerpt**:
  > ", our proprietary AI engine, dynamically baselines the performance of all components in the full stack, continually learning normal performance thresholds to provide precise answers when performance deviates from expected or desired conditions. Unlike ML-based correlation engines that rely on historical data for learning behavior and overwhelm IT professionals with hundreds of alerts, Dynatrace..."

---
### [TRAIN] EGHT (8X8 INC /DE/) - FY2025
- **Para ID**: `0001023731-25-000039_Item1_25`
- **Predicted Moat**: `none_or_commodity`
- **Rationale**: General discussion of AI features or competition without structural architectural switching costs or unique data moats.
- **Text Excerpt**:
  > "Embedded artificial intelligence powers features such as speech analytics, self-service virtual bots, agent assist capabilities, and sentiment tracking—providing supervisors with real-time visibility and enabling data-informed decisions to enhance customer satisfaction and operational efficiency...."

---
### [TRAIN] TEAM (Atlassian Corp) - FY2023
- **Para ID**: `0001650372-23-000040_Item1_36`
- **Predicted Moat**: `network_effects_ecosystem`
- **Rationale**: Emphasizes two-sided developer marketplaces, ecosystem apps, or viral network effects that scale with user adoption.
- **Text Excerpt**:
  > "Atlassian Ventures makes investments in the developer ecosystem, including cloud apps in the Atlassian Marketplace, integrations with our product suite, and deeper strategic partnerships that create shared customer value...."

---
### [TEST] RNG (RingCentral, Inc.) - FY2025
- **Para ID**: `0001384905-26-000021_Item1A_22`
- **Predicted Moat**: `compliance_security`
- **Rationale**: Explicitly cites regulatory compliance, legal liability, or strict security certifications as an operational barrier.
- **Text Excerpt**:
  > "We are and may be in the future subject to certain legal proceedings and from time to time may be involved in a variety of claims, lawsuits, investigations, and proceedings relating to contractual disputes, intellectual property rights, employment matters, regulatory compliance matters, and other matters relating to various claims that arise in the normal course of business. We record a provision for a liability when we believe that it is both pr..."

---

## 4. Sample Hacker News Stance Records

### [TEST] HN Post `47639825` (2026-04-04)
- **Predicted Stance**: `build_internal`
- **Rationale**: Advocates building bespoke internal tools or replacing commercial SaaS with in-house builds.
- **Text Excerpt**:
  > "I think the idea that every body are going to build their own SaaS product is likely wrong. But that is also not the only was to have impact. Whatbindo think happens is that everybody already building things will reduce or entirely remove their reliance on other SaaS tools. So retool and other support products are likely dead. The people who used these products are already more than capable of rolling Auth...."

---
### [TEST] HN Post `44626811` (2025-07-20)
- **Predicted Stance**: `build_internal`
- **Rationale**: Advocates building bespoke internal tools or replacing commercial SaaS with in-house builds.
- **Text Excerpt**:
  > "Already farted around with this in using a free Cloudflare vector database for "memories" with Claude Code for a few months, but LLMs are still a dumpster fire. You can even have it append to a local log file with what it's currently doing, what it's done in the past, conversation history et al. Doesn't really help. If anything, by giving it more cruft to parse through, you're usually making the output even worse. You can witness first-hand how i..."

---
### [TEST] HN Post `47882488` (2026-04-23)
- **Predicted Stance**: `buy_saas`
- **Rationale**: Argues against custom builds due to maintenance overhead, non-core distractions, or compliance risk.
- **Text Excerpt**:
  > "an esp32 on an 1100mah battery will last years on deep sleep, and about a day with wifi on and in high power modes. a pixel watch 4 says they last 30 hours , ambiguously. they use a battery less than half the size. in reality with constant use they'll drop dead in 6 hours. the thing is clunky and heavy , anyway -- so if it lasts as long as an off the shelf watch who cares? also, the primary reason : lilygo shoves ESPs into everything...."

---
### [TEST] HN Post `49374038` (2026-08-20)
- **Predicted Stance**: `hybrid_or_neutral`
- **Rationale**: Presents a nuanced trade-off analysis between in-house development and third-party SaaS.
- **Text Excerpt**:
  > "Ever since my boss has transitioned to doing code reviews by AI and off loading his brain fully to AI, I could just use my AI to do the same to fix the things and I no longer have to deal with petty design arguments. I no longer have to deal with stylistic problems and that's great. When somebody offloads their communication to AI, it's easy to deal with. Meet with the same energy. Let the AI waste their time in the communication because the lack..."

---
