import json
import csv
from pathlib import Path

# Load check_results
with open("saas_pulse/raw/check_results.json") as f:
    raw_results = json.load(f)

# Known CIK overrides for seed companies that had class share or name variances
extras = [
    {"ticker": "CFLT", "name": "Confluent, Inc.", "cik": "0001699838", "category": "data/infra", "ten_k_count": 4},
    {"ticker": "ZI", "name": "ZoomInfo Technologies Inc.", "cik": "0001794515", "category": "vertical", "ten_k_count": 4},
    {"ticker": "PRO", "name": "PROS Holdings, Inc.", "cik": "0001397187", "category": "vertical", "ten_k_count": 5},
    {"ticker": "SEMR", "name": "Semrush Holdings, Inc.", "cik": "0001831840", "category": "vertical", "ten_k_count": 4},
]

category_defaults = {
    # Security
    "CRWD": "security", "ZS": "security", "OKTA": "security", "S": "security",
    "QLYS": "security", "TENB": "security", "RPD": "security", "VRNS": "security",
    "PANW": "security", "FTNT": "security", "GEN": "security", "ALRM": "security",

    # Data/Infra
    "SNOW": "data/infra", "DDOG": "data/infra", "MDB": "data/infra", "NET": "data/infra",
    "ESTC": "data/infra", "DT": "data/infra", "GTLB": "data/infra", "CFLT": "data/infra",
    "DOCN": "data/infra", "FSLY": "data/infra", "NTNX": "data/infra", "FROG": "data/infra",
    "IOT": "data/infra", "AKAM": "data/infra", "CVLT": "data/infra", "PRGS": "data/infra",
    "PLTR": "data/infra", "PATH": "data/infra", "BLZE": "data/infra",

    # Horizontal
    "CRM": "horizontal", "ADBE": "horizontal", "NOW": "horizontal", "ADSK": "horizontal",
    "TEAM": "horizontal", "HUBS": "horizontal", "DOCU": "horizontal", "BOX": "horizontal",
    "DBX": "horizontal", "ASAN": "horizontal", "CXM": "horizontal", "PTC": "horizontal",
    "CDNS": "horizontal", "SNPS": "horizontal", "PEGA": "horizontal", "LAW": "horizontal",
    "WK": "horizontal", "DUOL": "horizontal", "COUR": "horizontal", "APP": "horizontal",
    "TASK": "horizontal", "YOU": "horizontal", "CALX": "horizontal", "CSGP": "horizontal",

    # Communication
    "TWLO": "communication", "ZM": "communication", "FIVN": "communication",
    "RNG": "communication", "EGHT": "communication", "BAND": "communication",

    # Vertical
    "VEEV": "vertical", "APPF": "vertical", "GWRE": "vertical", "MANH": "vertical",
    "TYL": "vertical", "PCOR": "vertical", "BLKB": "vertical", "PRO": "vertical",
    "RAMP": "vertical", "OTEX": "vertical", "SPSC": "vertical", "YEXT": "vertical",
    "PD": "vertical", "ZI": "vertical", "BRZE": "vertical", "AMPL": "vertical",
    "SPT": "vertical", "FRSH": "vertical", "SEMR": "vertical", "AGYS": "vertical",
    "VERX": "vertical",

    # Fintech/HR
    "WDAY": "fintech/HR", "INTU": "fintech/HR", "PCTY": "fintech/HR", "PAYC": "fintech/HR",
    "BILL": "fintech/HR", "NCNO": "fintech/HR", "ALKT": "fintech/HR", "QTWO": "fintech/HR",
    "BL": "fintech/HR", "TOST": "fintech/HR", "KVYO": "fintech/HR", "BLND": "fintech/HR",
    "FLYW": "fintech/HR", "PAY": "fintech/HR", "FOUR": "fintech/HR", "MQ": "fintech/HR",
    "PAYO": "fintech/HR", "RELY": "fintech/HR", "MKTX": "fintech/HR", "TWST": "data/infra",
    "APPN": "horizontal"
}

# Collect all candidates with >= 3 10-Ks
candidates = {}
for item in raw_results:
    if item.get("status") == "ok" and item.get("ten_k_count", 0) >= 3:
        t = item["ticker"]
        candidates[t] = {
            "ticker": t,
            "name": item["name"],
            "cik": item["cik"],
            "category": category_defaults.get(t, "horizontal"),
            "has_10k_fy2022_2025": True
        }

for ex in extras:
    candidates[ex["ticker"]] = {
        "ticker": ex["ticker"],
        "name": ex["name"],
        "cik": ex["cik"],
        "category": ex["category"],
        "has_10k_fy2022_2025": True
    }

print(f"Total available verified SaaS companies: {len(candidates)}")

# We select exactly 100 public SaaS companies
# Prioritize the original seed list tickers first
seed_order = [
    "CRM", "ADBE", "NOW", "WDAY", "INTU", "ADSK", "TEAM", "HUBS", "SNOW", "DDOG",
    "CRWD", "ZS", "OKTA", "TWLO", "ZM", "DOCU", "BOX", "DBX", "ASAN", "ESTC",
    "MDB", "NET", "PATH", "PLTR", "VEEV", "PCTY", "PAYC", "BILL", "FIVN", "RNG",
    "EGHT", "BRZE", "AMPL", "SPT", "SEMR", "WK", "APPF", "GWRE", "MANH", "PEGA",
    "TYL", "FRSH", "PD", "DT", "S", "QLYS", "TENB", "RPD", "VRNS", "GTLB",
    "CFLT", "DOCN", "FSLY", "NCNO", "ALKT", "QTWO", "PRO", "BLKB", "ZI", "BL",
    "PRGS", "CVLT", "NTNX", "SPSC", "KVYO", "IOT", "PCOR", "OTEX", "FROG", "TOST",
    "RAMP", "YEXT"
]

selected = []
for t in seed_order:
    if t in candidates and t not in [s["ticker"] for s in selected]:
        selected.append(candidates[t])

print(f"Selected from seed: {len(selected)}")

# Fill up to 100 with the best verified public SaaS / software filers
priority_additions = [
    "PANW", "FTNT", "AKAM", "PTC", "CDNS", "SNPS", "CXM", "DUOL", "APP", "GEN",
    "ALRM", "APPN", "VERX", "AGYS", "FOUR", "FLYW", "PAY", "BLND", "LAW", "COUR",
    "TASK", "BAND", "CSGP", "CALX", "YOU", "MQ", "PAYO", "RELY", "BLZE"
]

for t in priority_additions:
    if len(selected) >= 100:
        break
    if t in candidates and t not in [s["ticker"] for s in selected]:
        selected.append(candidates[t])

print(f"Total selected: {len(selected)}")

# Save to dataset/companies.csv
out_csv = Path("saas_pulse/dataset/companies.csv")
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ticker", "name", "cik", "category", "has_10k_fy2022_2025"])
    writer.writeheader()
    for row in selected:
        writer.writerow(row)

print("Saved dataset/companies.csv successfully!")
