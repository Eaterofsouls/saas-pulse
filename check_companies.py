import json
import time
import requests
from pathlib import Path

USER_AGENT = "Daksh Chauhan me@buildwithdaksh.com"
HEADERS = {"User-Agent": USER_AGENT}

SUBMISSIONS_DIR = Path("saas_pulse/raw/submissions")
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

tickers_path = Path("saas_pulse/raw/company_tickers.json")
if not tickers_path.exists():
    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    res.raise_for_status()
    tickers_path.write_text(res.text, encoding="utf-8")

tickers_data = json.loads(tickers_path.read_text(encoding="utf-8"))
sec_map = {}
for item in tickers_data.values():
    t = item["ticker"].upper()
    cik_str = str(item["cik_str"]).zfill(10)
    sec_map[t] = {
        "cik": cik_str,
        "name": item["title"],
        "ticker": t
    }

def get_submission(cik):
    cache_file = SUBMISSIONS_DIR / f"{cik}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    time.sleep(0.15)  # Rate limit: max ~6.6 req/s (< 8/s)
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 404:
        return None
    res.raise_for_status()
    data = res.json()
    cache_file.write_text(json.dumps(data), encoding="utf-8")
    return data

def get_all_10ks(cik, sub_data):
    ten_ks = []
    if not sub_data or "filings" not in sub_data:
        return ten_ks
    
    recent = sub_data["filings"]["recent"]
    for acc, fd, rd, form, doc in zip(recent["accessionNumber"], recent["filingDate"], recent["reportDate"], recent["form"], recent["primaryDocument"]):
        if form == "10-K":
            ten_ks.append({"accession": acc, "filingDate": fd, "reportDate": rd, "doc": doc})
            
    # Also check additional filing files if needed
    files = sub_data["filings"].get("files", [])
    for f_info in files:
        # Check if file date range overlaps 2022-2026
        f_from = f_info.get("filingFrom", "")
        f_to = f_info.get("filingTo", "")
        if f_to >= "2022-01-01":
            f_name = f_info["name"]
            f_cache = SUBMISSIONS_DIR / f"{cik}_{f_name}"
            if f_cache.exists():
                f_data = json.loads(f_cache.read_text(encoding="utf-8"))
            else:
                time.sleep(0.15)
                f_res = requests.get(f"https://data.sec.gov/submissions/{f_name}", headers=HEADERS)
                if f_res.status_code == 200:
                    f_data = f_res.json()
                    f_cache.write_text(json.dumps(f_data), encoding="utf-8")
                else:
                    f_data = None
            if f_data:
                for acc, fd, rd, form, doc in zip(f_data["accessionNumber"], f_data["filingDate"], f_data["reportDate"], f_data["form"], f_data["primaryDocument"]):
                    if form == "10-K":
                        ten_ks.append({"accession": acc, "filingDate": fd, "reportDate": rd, "doc": doc})
    return ten_ks

# Seed list from prompt
seed_list = [
    "CRM", "ADBE", "NOW", "WDAY", "INTU", "ADSK", "TEAM", "HUBS", "SNOW", "DDOG",
    "CRWD", "ZS", "OKTA", "TWLO", "ZM", "DOCU", "BOX", "DBX", "ASAN", "ESTC",
    "MDB", "NET", "PATH", "PLTR", "VEEV", "PCTY", "PAYC", "BILL", "FIVN", "RNG",
    "EGHT", "BRZE", "AMPL", "SPT", "SEMR", "WK", "APPF", "GWRE", "MANH", "PEGA",
    "TYL", "FRSH", "DOMO", "YEXT", "PD", "DT", "S", "QLYS", "TENB", "RPD",
    "VRNS", "GTLB", "CFLT", "DOCN", "FSLY", "NCNO", "ALKT", "QTWO", "JAMF", "PRO",
    "BLKB", "ZI", "BL", "PRGS", "CVLT", "NTNX", "SPSC", "KVYO", "IOT", "PCOR",
    "INST", "OTEX", "FROG", "TOST", "RAMP", "CWAN", "ENFN",
    "SMAR", "MNDY", "WIX", "ZUO", "COUP"
]

# High quality additional SaaS candidates
additional_candidates = [
    "PANW", "FTNT", "AKAM", "PTC", "ANSS", "CDNS", "SNPS", "CXM", "DUOL", "APP",
    "GEN", "VRNT", "DSGX", "BLND", "TASK", "LAW", "COUR", "PWSC", "FLYW", "PAY",
    "OLO", "GLBE", "YOU", "ENV", "CALX", "CSGP", "BAND", "MKTX", "TWST", "BILL",
    "VERX", "AGYS", "MANH", "ALRM", "APPN", "SPSX", "BLZE", "EBIX", "MODN", "KNBE",
    "FOUR", "MQ", "AVDX", "BRZE", "PAYO", "RELY", "SPT", "HUBS"
]

candidates = []
seen = set()
for t in seed_list + additional_candidates:
    t = t.upper().strip()
    if t not in seen:
        seen.add(t)
        candidates.append(t)

print(f"Total unique candidates to test: {len(candidates)}")

results = []
for ticker in candidates:
    if ticker not in sec_map:
        results.append({"ticker": ticker, "status": "not_in_sec_tickers"})
        continue
    cik = sec_map[ticker]["cik"]
    name = sec_map[ticker]["name"]
    try:
        sub = get_submission(cik)
        ten_ks = get_all_10ks(cik, sub)
        # Determine 10-Ks for FY 2022-2025
        # A 10-K for FY2022-2025 has reportDate generally between 2022-01-01 and 2026-03-31
        # (for Jan/Feb fiscal year filers, FY2022 ends Jan 2022; FY2025 ends Jan/Feb 2026)
        valid_10ks = []
        for tk in ten_ks:
            rd = tk["reportDate"]
            fd = tk["filingDate"]
            # Check reportDate year or filingDate year
            rd_year = int(rd[:4]) if rd else 0
            fd_year = int(fd[:4]) if fd else 0
            # If reportDate is between 2022-01-01 and 2026-02-28, or filingDate between 2022 and 2026
            if "2022-01-01" <= rd <= "2026-02-28" or (2022 <= fd_year <= 2026 and rd >= "2021-10-01"):
                # Approximate fiscal year:
                # If report date is in Jan/Feb/March, it's either named for that calendar year or previous
                valid_10ks.append(tk)
        results.append({
            "ticker": ticker,
            "cik": cik,
            "name": name,
            "ten_k_count": len(valid_10ks),
            "ten_ks": valid_10ks,
            "status": "ok"
        })
    except Exception as e:
        results.append({"ticker": ticker, "status": f"error: {e}"})

print(f"Processed {len(results)} companies.")
with open("saas_pulse/raw/check_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved results to saas_pulse/raw/check_results.json")
