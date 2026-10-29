import json
import re
import time
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

USER_AGENT = "Daksh Chauhan me@buildwithdaksh.com"
HEADERS = {"User-Agent": USER_AGENT}

DATASET_DIR = Path("saas_pulse/dataset")
RAW_EDGAR_DIR = Path("saas_pulse/raw/edgar")
SUBMISSIONS_DIR = Path("saas_pulse/raw/submissions")

DATASET_DIR.mkdir(parents=True, exist_ok=True)
RAW_EDGAR_DIR.mkdir(parents=True, exist_ok=True)

COMPANIES_CSV = DATASET_DIR / "companies.csv"
INDEX_CSV = DATASET_DIR / "filings_index.csv"
PARAGRAPHS_JSONL = DATASET_DIR / "filings_paragraphs.jsonl"

AI_REGEX = re.compile(
    r"artificial\s+intelligence|generative\s+AI|machine\s+learning|large\s+language\s+model|LLM|copilot|AI\s+agent",
    re.IGNORECASE
)

def get_filings_for_company(ticker: str, cik: str):
    sub_file = SUBMISSIONS_DIR / f"{cik}.json"
    if not sub_file.exists():
        return []
    
    data = json.loads(sub_file.read_text(encoding="utf-8"))
    company_name = data.get("name", ticker)
    recent = data["filings"]["recent"]
    
    filings = []
    for acc, fd, rd, form, doc in zip(recent["accessionNumber"], recent["filingDate"], recent["reportDate"], recent["form"], recent["primaryDocument"]):
        if form == "10-K":
            filings.append({
                "ticker": ticker,
                "company": company_name,
                "cik": cik,
                "accession": acc,
                "filing_date": fd,
                "report_date": rd,
                "primary_doc": doc
            })

    # Check older submission chunks if necessary
    extra_files = data["filings"].get("files", [])
    for ef in extra_files:
        if ef.get("filingTo", "") >= "2022-01-01":
            ef_path = SUBMISSIONS_DIR / f"{cik}_{ef['name']}"
            if ef_path.exists():
                try:
                    ef_data = json.loads(ef_path.read_text(encoding="utf-8"))
                    for acc, fd, rd, form, doc in zip(ef_data["accessionNumber"], ef_data["filingDate"], ef_data["reportDate"], ef_data["form"], ef_data["primaryDocument"]):
                        if form == "10-K":
                            filings.append({
                                "ticker": ticker,
                                "company": company_name,
                                "cik": cik,
                                "accession": acc,
                                "filing_date": fd,
                                "report_date": rd,
                                "primary_doc": doc
                            })
                except Exception:
                    pass

    # Filter for fiscal years 2022-2025 (or filing dates 2022-2026)
    valid_filings = []
    seen_acc = set()
    for f in filings:
        acc = f["accession"]
        if acc in seen_acc:
            continue
        seen_acc.add(acc)
        
        rd = f.get("report_date", "")
        fd = f.get("filing_date", "")
        
        # Check if period falls in FY2022-2025
        # reportDate between 2022-01-01 and 2026-03-31
        if ("2022-01-01" <= rd <= "2026-03-31") or ("2022-01-01" <= fd <= "2026-03-31"):
            fy = int(rd[:4]) if rd else int(fd[:4])
            f["fiscal_year"] = fy
            valid_filings.append(f)

    # Sort descending by filing date
    valid_filings.sort(key=lambda x: x["filing_date"], reverse=True)
    return valid_filings

def download_filing_html(cik: str, accession: str, primary_doc: str):
    safe_acc = accession.replace("-", "")
    local_file = RAW_EDGAR_DIR / f"{safe_acc}_{primary_doc}"
    
    cik_int = int(cik)
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{safe_acc}/{primary_doc}"
    
    if local_file.exists() and local_file.stat().st_size > 0:
        try:
            return local_file.read_text(encoding="utf-8", errors="replace"), url
        except Exception:
            pass

    time.sleep(0.15)  # SEC rate limit <= 8 req/sec
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        text = res.content.decode("utf-8", errors="replace")
        local_file.write_text(text, encoding="utf-8")
        return text, url
    else:
        return None, url

def extract_sections(html_text: str):
    soup = BeautifulSoup(html_text, "lxml")
    full_text = soup.get_text("\n", strip=True)

    def find_best_span(start_pattern, end_patterns):
        start_matches = list(re.finditer(start_pattern, full_text, re.IGNORECASE))
        if not start_matches:
            return "", 0

        # Try matches starting from the last match backwards (to skip TOC)
        best_text = ""
        for sm in reversed(start_matches):
            s_pos = sm.start()
            # Find earliest end pattern after s_pos
            min_e_pos = len(full_text)
            for ep in end_patterns:
                for em in re.finditer(ep, full_text[s_pos:], re.IGNORECASE):
                    # Relative position
                    actual_e = s_pos + em.start()
                    # Only consider if there is some meaningful distance (> 1000 chars)
                    if actual_e - s_pos > 1000 and actual_e < min_e_pos:
                        min_e_pos = actual_e
                        break

            candidate = full_text[s_pos:min_e_pos].strip()
            if len(candidate) > len(best_text):
                best_text = candidate
            if len(best_text) >= 5000:
                break

        return best_text, len(best_text)

    # Patterns
    p_item1 = r"(?:ITEM|Item)\s+1[.:\s\-\u2013\u2014]+(?:BUSINESS)?"
    p_item1a = r"(?:ITEM|Item)\s+1A[.:\s\-\u2013\u2014]+(?:RISK\s+FACTORS)?"
    p_item1b = r"(?:ITEM|Item)\s+1B[.:\s\-\u2013\u2014]+"
    p_item2 = r"(?:ITEM|Item)\s+2[.:\s\-\u2013\u2014]+"

    text_item1, chars1 = find_best_span(p_item1, [p_item1a, p_item1b, p_item2])
    text_item1a, chars1a = find_best_span(p_item1a, [p_item1b, p_item2])

    # Fallback if Item 1A < 5000 chars
    if chars1a < 5000:
        # Fallback regex patterns: more lenient
        fallback_p1a = r"(?:ITEM|Item)\s+1A"
        fallback_ends = [r"(?:ITEM|Item)\s+1B", r"(?:ITEM|Item)\s+2", r"(?:PART|Part)\s+II"]
        fb_text1a, fb_chars1a = find_best_span(fallback_p1a, fallback_ends)
        if fb_chars1a > chars1a:
            text_item1a = fb_text1a
            chars1a = fb_chars1a

    return text_item1, chars1, text_item1a, chars1a

def split_into_paragraphs(section_text: str):
    # Split on line breaks
    raw_paras = section_text.split("\n")
    paras = []
    current_p = []
    
    for line in raw_paras:
        clean = line.strip()
        if not clean:
            if current_p:
                joined = " ".join(current_p)
                if len(joined) >= 150:
                    paras.append(joined)
                current_p = []
            continue
        
        # If line starts with capital and looks like new paragraph, or current length is large
        if len(clean) >= 150:
            if current_p:
                joined = " ".join(current_p)
                if len(joined) >= 150:
                    paras.append(joined)
                current_p = []
            paras.append(clean)
        else:
            current_p.append(clean)
            
    if current_p:
        joined = " ".join(current_p)
        if len(joined) >= 150:
            paras.append(joined)
            
    return paras

print("Step B module loaded.")
