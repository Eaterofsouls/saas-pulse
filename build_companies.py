import json
import time
import re
import requests
from pathlib import Path
import pandas as pd

USER_AGENT = "Daksh Chauhan me@buildwithdaksh.com"
HEADERS = {"User-Agent": USER_AGENT}

DATASET_DIR = Path("saas_pulse/dataset")
RAW_DIR = Path("saas_pulse/raw")
DATASET_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 1. Fetch or load company_tickers.json
tickers_path = RAW_DIR / "company_tickers.json"
if not tickers_path.exists():
    print("Fetching company_tickers.json from SEC...")
    res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS)
    res.raise_for_status()
    tickers_path.write_text(res.text, encoding="utf-8")

tickers_data = json.loads(tickers_path.read_text(encoding="utf-8"))
# Mapping: ticker -> {cik: str (padded 10 digits), name: str, ticker: str}
sec_map = {}
for item in tickers_data.values():
    t = item["ticker"].upper()
    cik_str = str(item["cik_str"]).zfill(10)
    sec_map[t] = {
        "cik": cik_str,
        "name": item["title"],
        "ticker": t
    }

print(f"Loaded {len(sec_map)} SEC tickers.")

# Candidate seed list and extras
seed_candidates = [
    # Seed list from prompt
    "CRM", "ADBE", "NOW", "WDAY", "INTU", "ADSK", "TEAM", "HUBS", "SNOW", "DDOG",
    "CRWD", "ZS", "OKTA", "TWLO", "ZM", "DOCU", "BOX", "DBX", "ASAN", "ESTC",
    "MDB", "NET", "PATH", "PLTR", "VEEV", "PCTY", "PAYC", "BILL", "FIVN", "RNG",
    "EGHT", "BRZE", "AMPL", "SPT", "SEMR", "WK", "APPF", "GWRE", "MANH", "PEGA",
    "TYL", "FRSH", "DOMO", "YEXT", "PD", "DT", "S", "QLYS", "TENB", "RPD",
    "VRNS", "GTLB", "CFLT", "DOCN", "FSLY", "NCNO", "ALKT", "QTWO", "JAMF", "PRO",
    "BLKB", "ZI", "BL", "PRGS", "CVLT", "NTNX", "SPSC", "KVYO", "IOT", "PCOR",
    "INST", "OTEX", "FROG", "TOST", "RAMP", "CWAN", "ENFN", "SMAR", "MNDY", "WIX",
    "ZUO", "COUP",
    # Additional well-known public SaaS / cloud software companies filing 10-Ks:
    "PANW", "FTNT", "CYBR", "CHKP", "AKAM", "PTC", "ANSS", "CDNS", "SNPS", "CXM",
    "DUOL", "LAW", "BLND", "TASK", "APP", "GEN", "VRNT", "DSGX", "SPLK", "NEWR",
    "SUMO", "AVLR", "ZEN", "PFPT", "MIME", "LOGI", "ORCL", "MSFT", "SAP", "WORK",
    "TWOU", "COUR", "NERD", "UPWK", "FVRR", "BMBL", "MTCH", "SHOP", "SQ", "PYPL"
]

# We need SaaS / Cloud Software categories:
# horizontal, security, data/infra, vertical, fintech/HR, communication

category_map = {
    # Security
    "CRWD": "security", "ZS": "security", "OKTA": "security", "S": "security",
    "QLYS": "security", "TENB": "security", "RPD": "security", "VRNS": "security",
    "PANW": "security", "FTNT": "security", "CYBR": "security", "CHKP": "security",
    "GEN": "security",

    # Data/Infra
    "SNOW": "data/infra", "DDOG": "data/infra", "MDB": "data/infra", "NET": "data/infra",
    "ESTC": "data/infra", "DT": "data/infra", "GTLB": "data/infra", "CFLT": "data/infra",
    "DOCN": "data/infra", "FSLY": "data/infra", "NTNX": "data/infra", "FROG": "data/infra",
    "IOT": "data/infra", "AKAM": "data/infra", "CVLT": "data/infra", "PRGS": "data/infra",
    "PLTR": "data/infra", "PATH": "data/infra",

    # Horizontal
    "CRM": "horizontal", "ADBE": "horizontal", "NOW": "horizontal", "ADSK": "horizontal",
    "TEAM": "horizontal", "HUBS": "horizontal", "DOCU": "horizontal", "BOX": "horizontal",
    "DBX": "horizontal", "ASAN": "horizontal", "SMAR": "horizontal", "MNDY": "horizontal",
    "CXM": "horizontal", "PTC": "horizontal", "ANSS": "horizontal", "CDNS": "horizontal",
    "SNPS": "horizontal", "DSGX": "horizontal", "PEGA": "horizontal", "LAW": "horizontal",
    "WK": "horizontal", "DUOL": "horizontal",

    # Communication
    "TWLO": "communication", "ZM": "communication", "FIVN": "communication",
    "RNG": "communication", "EGHT": "communication", "BAND": "communication",
    "VRNT": "communication",

    # Vertical
    "VEEV": "vertical", "APPF": "vertical", "GWRE": "vertical", "MANH": "vertical",
    "TYL": "vertical", "PCOR": "vertical", "INST": "vertical", "BLKB": "vertical",
    "PRO": "vertical", "RAMP": "vertical", "CWAN": "vertical", "OTEX": "vertical",
    "SPSC": "vertical", "DOMO": "vertical", "YEXT": "vertical", "PD": "vertical",
    "JAMF": "vertical", "ZI": "vertical", "BRZE": "vertical", "AMPL": "vertical",
    "SPT": "vertical", "SEMR": "vertical", "FRSH": "vertical",

    # Fintech/HR
    "WDAY": "fintech/HR", "INTU": "fintech/HR", "PCTY": "fintech/HR", "PAYC": "fintech/HR",
    "BILL": "fintech/HR", "NCNO": "fintech/HR", "ALKT": "fintech/HR", "QTWO": "fintech/HR",
    "BL": "fintech/HR", "ENFN": "fintech/HR", "TOST": "fintech/HR", "KVYO": "fintech/HR",
    "ZUO": "fintech/HR"
}

print(f"Total candidate tickers: {len(seed_candidates)}")
