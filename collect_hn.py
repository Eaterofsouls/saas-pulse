import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

RAW_HN_DIR = Path("saas_pulse/raw/hn")
RAW_HN_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = Path("saas_pulse/dataset/hn_comments.jsonl")

QUERIES = [
    "SaaS is dead",
    "AI agents replace SaaS",
    "seat-based pricing",
    "usage-based pricing AI",
    "AI wrapper",
    "SaaS AI features",
    "vibe coding SaaS",
    "build vs buy AI"
]

TAGS = ["comment", "story"]

def generate_monthly_windows():
    windows = []
    start_year = 2022
    end_year = 2026
    
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == 2026 and month > 10:
                break
            s_dt = datetime(year, month, 1, tzinfo=timezone.utc)
            s_ts = int(s_dt.timestamp())
            
            if month == 12:
                e_dt = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                e_dt = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            e_ts = int(e_dt.timestamp()) - 1
            
            w_label = f"{year}_{month:02d}"
            windows.append((w_label, s_ts, e_ts))
    return windows

def clean_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(" ", strip=True)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_page(query: str, tag: str, w_label: str, s_ts: int, e_ts: int, page: int = 0):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", query.lower()).strip("_")
    cache_path = RAW_HN_DIR / f"{slug}_{tag}_{w_label}_p{page}.json"
    
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    url = "https://hn.algolia.com/api/v1/search_by_date"
    params = {
        "query": query,
        "tags": tag,
        "numericFilters": f"created_at_i>={s_ts},created_at_i<={e_ts}",
        "hitsPerPage": 100,
        "page": page
    }
    
    for attempt in range(4):
        try:
            time.sleep(0.22)
            res = requests.get(url, params=params, timeout=20)
            if res.status_code == 200:
                data = res.json()
                cache_path.write_text(json.dumps(data), encoding="utf-8")
                return data
            elif res.status_code == 429:
                time.sleep(2 * (attempt + 1))
            else:
                break
        except Exception:
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
            else:
                break
    return None

def main():
    windows = generate_monthly_windows()
    print(f"Generated {len(windows)} monthly windows.")
    
    collected_records = {}
    if OUT_FILE.exists():
        try:
            with open(OUT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        collected_records[str(obj["id"])] = obj
            print(f"Resuming with {len(collected_records)} existing records.")
        except Exception:
            pass

    TARGET_MIN = 5000
    TARGET_MAX = 20000

    stop_collection = False

    for q in QUERIES:
        if stop_collection:
            break
        print(f"\n--- Collecting for query: '{q}' ---")
        for tag in TAGS:
            if stop_collection:
                break
            for w_label, s_ts, e_ts in reversed(windows):
                if stop_collection:
                    break
                
                first_page = fetch_page(q, tag, w_label, s_ts, e_ts, 0)
                if not first_page:
                    continue
                
                nb_pages = min(first_page.get("nbPages", 1), 10)
                hits = first_page.get("hits", [])
                
                for hit in hits:
                    hit_id = str(hit.get("objectID"))
                    if not hit_id or hit_id in collected_records:
                        continue
                    
                    raw_content = hit.get("comment_text") if tag == "comment" else (hit.get("story_text") or hit.get("title", ""))
                    cleaned = clean_text(raw_content)
                    if len(cleaned) < 80:
                        continue
                    
                    author = hit.get("author") or "anonymous"
                    author_hash = hashlib.sha256(author.encode("utf-8")).hexdigest()
                    
                    record = {
                        "id": hit_id,
                        "type": tag,
                        "created_at": hit.get("created_at"),
                        "author_hash": author_hash,
                        "points": hit.get("points"),
                        "story_id": hit.get("story_id"),
                        "query": q,
                        "text": cleaned
                    }
                    collected_records[hit_id] = record
                    
                    if len(collected_records) >= TARGET_MAX:
                        stop_collection = True
                        break
                        
                for p in range(1, nb_pages):
                    if stop_collection:
                        break
                    p_data = fetch_page(q, tag, w_label, s_ts, e_ts, p)
                    if not p_data:
                        continue
                    for hit in p_data.get("hits", []):
                        hit_id = str(hit.get("objectID"))
                        if not hit_id or hit_id in collected_records:
                            continue
                        raw_content = hit.get("comment_text") if tag == "comment" else (hit.get("story_text") or hit.get("title", ""))
                        cleaned = clean_text(raw_content)
                        if len(cleaned) < 80:
                            continue
                        author = hit.get("author") or "anonymous"
                        author_hash = hashlib.sha256(author.encode("utf-8")).hexdigest()
                        record = {
                            "id": hit_id,
                            "type": tag,
                            "created_at": hit.get("created_at"),
                            "author_hash": author_hash,
                            "points": hit.get("points"),
                            "story_id": hit.get("story_id"),
                            "query": q,
                            "text": cleaned
                        }
                        collected_records[hit_id] = record
                        if len(collected_records) >= TARGET_MAX:
                            stop_collection = True
                            break

                if len(collected_records) % 500 < 50:
                    print(f"Current collected unique records: {len(collected_records)}")

    print(f"\nFinal collected unique HN records: {len(collected_records)}")
    
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for rec in collected_records.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            
    print(f"Successfully saved {len(collected_records)} records to {OUT_FILE}")

if __name__ == "__main__":
    main()
