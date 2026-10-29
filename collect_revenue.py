import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests

USER_AGENT = "Daksh Chauhan me@buildwithdaksh.com"
HEADERS = {"User-Agent": USER_AGENT}

COMPANIES_CSV = Path("saas_pulse/dataset/companies.csv")
FACTS_DIR = Path("saas_pulse/raw/companyfacts")
FACTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = Path("saas_pulse/dataset/revenue.csv")

TAG_CANDIDATES = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax"
]

def fetch_company_facts(cik: str):
    cache_path = FACTS_DIR / f"{cik}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    time.sleep(0.15)  # SEC limit: <= 8 req/sec
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 404:
        return None
    res.raise_for_status()
    data = res.json()
    cache_path.write_text(json.dumps(data), encoding="utf-8")
    return data

def extract_annual_revenues(ticker: str, data: dict):
    if not data or "facts" not in data or "us-gaap" not in data["facts"]:
        return []

    us_gaap = data["facts"]["us-gaap"]
    
    # Check tag priority
    selected_tag = None
    units = []
    for tag in TAG_CANDIDATES:
        if tag in us_gaap and "units" in us_gaap[tag] and "USD" in us_gaap[tag]["units"]:
            candidate_units = us_gaap[tag]["units"]["USD"]
            # Check if has annual 10-K entries for fiscal year >= 2021
            has_annual = any(
                u.get("form") == "10-K" and u.get("fp") == "FY" and int(u.get("end", "0000")[:4]) >= 2021
                for u in candidate_units
            )
            if has_annual:
                selected_tag = tag
                units = candidate_units
                break

    if not selected_tag:
        return []

    year_entries = {}
    for item in units:
        if item.get("form") != "10-K" or item.get("fp") != "FY":
            continue

        val = item.get("val")
        if val is None:
            continue

        start_str = item.get("start")
        end_str = item.get("end")
        
        # Verify ~annual duration if start and end are provided
        if start_str and end_str:
            try:
                s_dt = datetime.strptime(start_str, "%Y-%m-%d")
                e_dt = datetime.strptime(end_str, "%Y-%m-%d")
                days = (e_dt - s_dt).days
                if days < 300 or days > 400:
                    continue  # not a full annual period
            except Exception:
                pass

        # Determine fiscal year
        if end_str:
            fy = int(end_str[:4])
        elif item.get("fy"):
            fy = int(item["fy"])
        else:
            continue

        # Filter to relevant years (2021 to 2026)
        if fy < 2021 or fy > 2026:
            continue

        filed = item.get("filed", "")
        # Keep latest filed entry for this fiscal year
        if fy not in year_entries or filed > year_entries[fy]["filed"]:
            year_entries[fy] = {
                "ticker": ticker,
                "fiscal_year": fy,
                "revenue_usd": val,
                "tag_used": selected_tag,
                "filed": filed
            }

    sorted_years = sorted(year_entries.keys())
    results = []
    for i, fy in enumerate(sorted_years):
        entry = year_entries[fy]
        growth = ""
        if i > 0 and sorted_years[i-1] == fy - 1:
            prev_rev = year_entries[fy - 1]["revenue_usd"]
            if prev_rev and prev_rev > 0:
                growth_pct = ((entry["revenue_usd"] - prev_rev) / prev_rev) * 100.0
                growth = f"{growth_pct:.2f}"
        
        results.append({
            "ticker": ticker,
            "fiscal_year": fy,
            "revenue_usd": entry["revenue_usd"],
            "tag_used": entry["tag_used"],
            "revenue_growth_pct": growth
        })

    return results

def main():
    df = pd.read_csv(COMPANIES_CSV, dtype={"cik": str})
    print(f"Loaded {len(df)} companies from {COMPANIES_CSV}")

    all_rows = []
    missing_companies = []

    for idx, row in df.iterrows():
        ticker = row["ticker"]
        cik = str(row["cik"]).zfill(10)
        facts = fetch_company_facts(cik)
        rows = extract_annual_revenues(ticker, facts)
        if rows:
            all_rows.extend(rows)
        else:
            missing_companies.append(ticker)

    out_df = pd.DataFrame(all_rows, columns=["ticker", "fiscal_year", "revenue_usd", "tag_used", "revenue_growth_pct"])
    out_df.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(out_df)} revenue records to {OUT_CSV}")
    print(f"Companies with revenue collected: {len(df) - len(missing_companies)}/{len(df)}")
    if missing_companies:
        print(f"Missing revenue for: {missing_companies}")

if __name__ == "__main__":
    main()
