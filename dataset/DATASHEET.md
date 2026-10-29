# Dataset Datasheet: SaaS-Pulse

## Motivation
- **Purpose**: Academic Generative-AI dataset exploring how artificial intelligence is transforming modern SaaS companies: what they say in annual disclosures (SEC 10-K filings), how they monetize and charge (public pricing pages), and how the engineering / tech community reacts (Hacker News discussions).
- **Creators / Contact**: Daksh Chauhan (`me@buildwithdaksh.com`).
- **Domain**: Cloud Software / Software-as-a-Service (SaaS).

## Dataset Composition & Sources
1. **SEC EDGAR Annual Filings (10-K)**
   - **Source URL**: `https://www.sec.gov/edgar/searchedgar/companysearch` & `https://data.sec.gov/submissions/`
   - **License / Terms**: US Federal Government work product, public domain.
   - **Record Count**: 190,655 paragraphs extracted across 464 annual 10-K filings (443 successfully parsed quality gate).
   - **Fields**: `ticker`, `company`, `cik`, `fiscal_year`, `filing_date`, `accession`, `section` (Item 1 / Item 1A), `para_id`, `text`, `mentions_ai` (boolean regex indicator).
   - **Filtering Rules**: Only primary HTML 10-K filings for fiscal years 2022–2025. Item 1 and Item 1A located using heading heuristics bypassing TOC. Paragraphs minimum 150 characters.

2. **SEC XBRL Revenue**
   - **Source URL**: `https://data.sec.gov/api/xbrl/companyfacts/`
   - **License / Terms**: Public domain.
   - **Record Count**: 538 annual revenue records across 100 companies.
   - **Fields**: `ticker`, `fiscal_year`, `revenue_usd`, `tag_used`, `revenue_growth_pct`.
   - **Filtering Rules**: Official US-GAAP revenue concepts (`RevenueFromContractWithCustomerExcludingAssessedTax`, `Revenues`, `SalesRevenueNet`, `RevenueFromContractWithCustomerIncludingAssessedTax`), annual duration (Form 10-K, fp FY). Growth computed strictly between consecutive fiscal years ($FY_{curr} == FY_{prev} + 1$); no interpolation or synthetic data.

3. **Hacker News Community Discussions**
   - **Source URL**: Algolia HN Search API (`https://hn.algolia.com/api/v1/search_by_date`)
   - **License / Terms**: Public posts collected for academic, non-commercial coursework analysis.
   - **Record Count**: 7,829 unique items.
   - **Fields**: `id`, `type`, `created_at`, `author_hash` (SHA-256 pseudonymized hash), `points`, `story_id`, `query`, `text`.
   - **Filtering Rules**: Monthly time windows across 2022-01-01 to 2026-10-29. Target queries: "SaaS is dead", "AI agents replace SaaS", "seat-based pricing", "usage-based pricing AI", "AI wrapper", "SaaS AI features", "vibe coding SaaS", "build vs buy AI". Stripped HTML formatting, minimum 80 characters, deduplicated by object ID.

4. **Product Pricing Pages (Live & Historical Wayback)**
   - **Source URL**: Live company websites + Internet Archive Wayback Machine (`https://web.archive.org/`)
   - **License / Terms**: Website pages are copyrighted by respective companies. Captured solely as fair-use snapshots for non-commercial university coursework analysis. No commercial redistribution.
   - **Record Count**: 147 snapshot records and 15 JPEG visual screenshots.
   - **Fields**: `product`, `domain`, `source` ("live" or "wayback"), `url`, `captured_at`, `status`, `text`, `html_sha256`, `snapshot_date` (for Wayback).
   - **Filtering Rules**: Respects `robots.txt` on all live domains. No CAPTCHA / bot wall bypass (records `blocked`). Historical snapshots targeted at 2022-06-15 and 2024-06-15 via Wayback `id_` raw rendering in Playwright (1280x2000, quality 60, < 300 KB).

## Known Limitations & Biases
1. **Survivorship Bias**: The company cohort consists of public SaaS filers with continuous 10-K filings between FY2022 and FY2025. Private companies that shut down, went bankrupt, or were taken private before 2024 without filing 10-Ks are excluded from the SEC corpus.
2. **SEC Parsing Variations**: While the parser utilizes multiple heading anchors and fallbacks, varying HTML/inline XBRL styling across filers can occasionally cause truncation in complex multi-column tables.
3. **Temporal Granularity of Pricing**: Web pages are point-in-time snapshots (live vs mid-2022 vs mid-2024); intra-year pricing experiments or localized A/B tests may not be captured.
4. **HN Community Representativeness**: Discussions on Hacker News reflect the opinions of tech early adopters, founders, and software engineers, and do not necessarily mirror enterprise buyer procurement sentiment.

## Privacy & Ethical Considerations
- **Pseudonymization**: Raw Hacker News usernames are never stored; all author identities are irreversibly hashed with SHA-256 (`author_hash`).
- **Politeness & Rate Limits**: Rigorously respected SEC limits (< 8 req/sec), Algolia HN limits (< 5 req/sec), live site robots.txt, and Archive.org pacing (< 1 req/sec).

---
*Generated automatically on 2026-10-29 for the SaaS-Pulse Project.*
