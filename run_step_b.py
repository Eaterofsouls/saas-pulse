import csv
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

    valid_filings = []
    seen_acc = set()
    for f in filings:
        acc = f["accession"]
        if acc in seen_acc:
            continue
        seen_acc.add(acc)
        
        rd = f.get("report_date", "")
        fd = f.get("filing_date", "")
        
        if ("2022-01-01" <= rd <= "2026-03-31") or ("2022-01-01" <= fd <= "2026-03-31"):
            fy = int(rd[:4]) if rd else int(fd[:4])
            f["fiscal_year"] = fy
            valid_filings.append(f)

    valid_filings.sort(key=lambda x: x["filing_date"], reverse=True)
    return valid_filings

def download_filing(cik: str, accession: str, primary_doc: str):
    safe_acc = accession.replace("-", "")
    local_file = RAW_EDGAR_DIR / f"{safe_acc}_{primary_doc}"
    cik_int = int(cik)
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{safe_acc}/{primary_doc}"
    
    if local_file.exists() and local_file.stat().st_size > 0:
        try:
            return local_file.read_text(encoding="utf-8", errors="replace"), url
        except Exception:
            pass

    for attempt in range(4):
        try:
            time.sleep(0.14)
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code == 200:
                text = res.content.decode("utf-8", errors="replace")
                local_file.write_text(text, encoding="utf-8")
                return text, url
            elif res.status_code == 429:
                time.sleep(2 * (attempt + 1))
            else:
                break
        except Exception as e:
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
            else:
                break
    return None, url

def extract_sections(html_text: str):
    soup = BeautifulSoup(html_text, "lxml")
    full_text = soup.get_text("\n", strip=True)

    def find_span(start_pattern, end_patterns):
        start_matches = list(re.finditer(start_pattern, full_text, re.IGNORECASE))
        if not start_matches:
            return "", 0

        best_candidate = ""
        for sm in reversed(start_matches):
            s_pos = sm.start()
            min_e = len(full_text)
            for ep in end_patterns:
                for em in re.finditer(ep, full_text[s_pos:], re.IGNORECASE):
                    actual_e = s_pos + em.start()
                    if actual_e - s_pos > 800 and actual_e < min_e:
                        min_e = actual_e
                        break

            candidate = full_text[s_pos:min_e].strip()
            if len(candidate) > len(best_candidate):
                best_candidate = candidate
            if len(best_candidate) >= 5000:
                break
        return best_candidate, len(best_candidate)

    p_item1 = r"(?:ITEM|Item)\s+1[.:\s\-\u2013\u2014]+(?:BUSINESS)?"
    p_item1a = r"(?:ITEM|Item)\s+1A[.:\s\-\u2013\u2014]+(?:RISK\s+FACTORS)?"
    p_item1b = r"(?:ITEM|Item)\s+1B[.:\s\-\u2013\u2014]+"
    p_item2 = r"(?:ITEM|Item)\s+2[.:\s\-\u2013\u2014]+"

    text_item1, chars1 = find_span(p_item1, [p_item1a, p_item1b, p_item2])
    text_item1a, chars1a = find_span(p_item1a, [p_item1b, p_item2])

    if chars1a < 5000:
        fallback_p1a = r"(?:ITEM|Item)\s+1A"
        fallback_ends = [r"(?:ITEM|Item)\s+1B", r"(?:ITEM|Item)\s+2", r"(?:PART|Part)\s+II"]
        fb_text1a, fb_chars1a = find_span(fallback_p1a, fallback_ends)
        if fb_chars1a > chars1a:
            text_item1a = fb_text1a
            chars1a = fb_chars1a

    return text_item1, chars1, text_item1a, chars1a

def split_paragraphs(section_text: str):
    raw_lines = section_text.split("\n")
    paras = []
    curr = []
    for line in raw_lines:
        clean = line.strip()
        if not clean:
            if curr:
                joined = " ".join(curr)
                if len(joined) >= 150:
                    paras.append(joined)
                curr = []
            continue
        if len(clean) >= 150:
            if curr:
                joined = " ".join(curr)
                if len(joined) >= 150:
                    paras.append(joined)
                curr = []
            paras.append(clean)
        else:
            curr.append(clean)
    if curr:
        joined = " ".join(curr)
        if len(joined) >= 150:
            paras.append(joined)
    return paras

def main():
    df = pd.read_csv(COMPANIES_CSV, dtype={"cik": str})
    
    existing_acc = set()
    if INDEX_CSV.exists():
        try:
            ex_df = pd.read_csv(INDEX_CSV)
            existing_acc = set(ex_df["accession"].astype(str))
        except Exception:
            pass

    index_mode = "a" if INDEX_CSV.exists() and len(existing_acc) > 0 else "w"
    para_mode = "a" if PARAGRAPHS_JSONL.exists() and len(existing_acc) > 0 else "w"

    index_file = open(INDEX_CSV, index_mode, newline="", encoding="utf-8")
    index_writer = csv.writer(index_file)
    if index_mode == "w":
        index_writer.writerow(["ticker", "fiscal_year", "filing_date", "accession", "url", "chars_item1", "chars_item1a", "status"])

    para_file = open(PARAGRAPHS_JSONL, para_mode, encoding="utf-8")

    all_filings = []
    for _, row in df.iterrows():
        ticker = row["ticker"]
        cik = str(row["cik"]).zfill(10)
        c_filings = get_filings_for_company(ticker, cik)
        all_filings.extend(c_filings)

    print(f"Total filings to process: {len(all_filings)} (already done: {len(existing_acc)})")

    success_count = 0
    fail_count = 0
    total_paras = 0

    for idx, f in enumerate(all_filings, start=1):
        acc = f["accession"]
        if acc in existing_acc:
            continue

        ticker = f["ticker"]
        cik = f["cik"]
        doc = f["primary_doc"]
        fy = f["fiscal_year"]
        fd = f["filing_date"]
        company = f["company"]

        html_text, url = download_filing(cik, acc, doc)
        if not html_text:
            index_writer.writerow([ticker, fy, fd, acc, url, 0, 0, "download_failed"])
            index_file.flush()
            fail_count += 1
            continue

        try:
            t1, c1, t1a, c1a = extract_sections(html_text)
            status = "ok" if c1a >= 5000 else "parse_failed"
            
            index_writer.writerow([ticker, fy, fd, acc, url, c1, c1a, status])
            index_file.flush()

            p1_list = split_paragraphs(t1)
            for p_idx, p_text in enumerate(p1_list, start=1):
                p_obj = {
                    "ticker": ticker,
                    "company": company,
                    "cik": cik,
                    "fiscal_year": fy,
                    "filing_date": fd,
                    "accession": acc,
                    "section": "Item 1",
                    "para_id": f"{acc}_Item1_{p_idx}",
                    "text": p_text,
                    "mentions_ai": bool(AI_REGEX.search(p_text))
                }
                para_file.write(json.dumps(p_obj, ensure_ascii=False) + "\n")
                total_paras += 1

            p1a_list = split_paragraphs(t1a)
            for p_idx, p_text in enumerate(p1a_list, start=1):
                p_obj = {
                    "ticker": ticker,
                    "company": company,
                    "cik": cik,
                    "fiscal_year": fy,
                    "filing_date": fd,
                    "accession": acc,
                    "section": "Item 1A",
                    "para_id": f"{acc}_Item1A_{p_idx}",
                    "text": p_text,
                    "mentions_ai": bool(AI_REGEX.search(p_text))
                }
                para_file.write(json.dumps(p_obj, ensure_ascii=False) + "\n")
                total_paras += 1

            para_file.flush()

            if status == "ok":
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            index_writer.writerow([ticker, fy, fd, acc, url, 0, 0, "error"])
            index_file.flush()
            fail_count += 1

        if idx % 20 == 0:
            print(f"[{idx}/{len(all_filings)}] Processed. OK: {success_count}, Failed: {fail_count}, Paras: {total_paras}")

    index_file.close()
    para_file.close()

    print(f"\nStep B complete! Total filings: {len(all_filings)}. OK: {success_count}, Failed: {fail_count}, Total paragraphs: {total_paras}")

if __name__ == "__main__":
    main()
