import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests
from playwright.sync_api import sync_playwright

PRODUCTS_CSV = Path("saas_pulse/dataset/products.csv")
OUT_JSONL = Path("saas_pulse/dataset/pricing_pages.jsonl")
SCREENS_DIR = Path("saas_pulse/dataset/pricing_screens")
SCREENS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_robots(domain: str, path: str) -> bool:
    try:
        robots_url = f"https://{domain}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        res = requests.get(robots_url, headers=HEADERS, timeout=4)
        if res.status_code == 200:
            rp.parse(res.text.splitlines())
            target_url = f"https://{domain}{path}"
            return rp.can_fetch("*", target_url)
        return True
    except Exception:
        return True

def get_wayback_snapshot(pricing_url: str, ts: str):
    time.sleep(1.02)  # Respect Wayback limit
    api_url = f"https://archive.org/wayback/available?url={urllib.parse.quote(pricing_url)}&timestamp={ts}"
    try:
        r = requests.get(api_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if "archived_snapshots" in data and "closest" in data["archived_snapshots"]:
                wb_url = data["archived_snapshots"]["closest"]["url"]
                id_url = re.sub(r"(/web/\d+)(/)", r"\1id_\2", wb_url)
                return id_url, "ok"
    except Exception:
        pass

    try:
        time.sleep(0.5)
        from_ts = f"{ts[:4]}0501"
        to_ts = f"{ts[:4]}0731"
        cdx_url = f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(pricing_url)}&output=json&from={from_ts}&to={to_ts}&limit=1"
        cr = requests.get(cdx_url, headers=HEADERS, timeout=8)
        if cr.status_code == 200:
            lines = cr.json()
            if len(lines) > 1:
                snap_ts = lines[1][1]
                orig_url = lines[1][2]
                id_url = f"https://web.archive.org/web/{snap_ts}id_/{orig_url}"
                return id_url, "ok"
    except Exception:
        pass

    return None, "no_snapshot"

def sanitize(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")

def main():
    df = pd.read_csv(PRODUCTS_CSV)
    
    # Prioritize rows that have empty public_ticker_or_blank (the private products) or key SaaS products
    df["is_named_priority"] = df["public_ticker_or_blank"].isna() | (df["public_ticker_or_blank"] == "")
    df = df.sort_values(by="is_named_priority", ascending=False).reset_index(drop=True)

    captured_keys = set()
    if OUT_JSONL.exists():
        try:
            with open(OUT_JSONL, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        k = (obj.get("domain"), obj.get("source"), obj.get("snapshot_date", "live"))
                        captured_keys.add(k)
        except Exception:
            pass

    out_file = open(OUT_JSONL, "a", encoding="utf-8")
    candidate_paths = ["/pricing", "/plans", "/pricing-plans", "/en/pricing"]

    print(f"Starting pricing capture. Already captured: {len(captured_keys)} items.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 2000})
        page = context.new_page()

        for idx, row in df.iterrows():
            product = row["product"]
            domain = row["domain"]
            
            live_key = (domain, "live", "live")
            live_pricing_url = None

            if live_key not in captured_keys:
                print(f"[{idx+1}/{len(df)}] Live pricing: {product} ({domain})...")
                found_url = None
                is_disallowed = False

                for path in candidate_paths:
                    if not check_robots(domain, path):
                        is_disallowed = True
                        break
                    
                    test_url = f"https://{domain}{path}"
                    try:
                        time.sleep(0.4)
                        r = requests.get(test_url, headers=HEADERS, timeout=6, allow_redirects=True)
                        if r.status_code == 200 and any(kw in r.text.lower() for kw in ["pricing", "plan", "month", "tier", "billing", "$"]):
                            found_url = r.url
                            break
                    except Exception:
                        continue

                if is_disallowed:
                    record = {
                        "product": product,
                        "domain": domain,
                        "source": "live",
                        "url": f"https://{domain}/pricing",
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                        "status": "robots_disallowed",
                        "text": "",
                        "html_sha256": ""
                    }
                    out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out_file.flush()
                elif not found_url:
                    record = {
                        "product": product,
                        "domain": domain,
                        "source": "live",
                        "url": f"https://{domain}/pricing",
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                        "status": "no_pricing_page",
                        "text": "",
                        "html_sha256": ""
                    }
                    out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out_file.flush()
                else:
                    live_pricing_url = found_url
                    try:
                        resp = page.goto(found_url, timeout=20000, wait_until="load")
                        try:
                            page.wait_for_load_state("networkidle", timeout=3000)
                        except Exception:
                            pass

                        try:
                            cookie_btn = page.locator('button:has-text("Accept"), button:has-text("Reject"), button:has-text("Allow all"), button:has-text("I Agree")').first
                            if cookie_btn.is_visible(timeout=1500):
                                cookie_btn.click(timeout=1500)
                        except Exception:
                            pass

                        page_text = page.evaluate("document.body.innerText") or ""
                        html_src = page.content()
                        h = hashlib.sha256(html_src.encode("utf-8")).hexdigest()

                        if any(b_kw in page_text.lower() for b_kw in ["verifying you are human", "cloudflare challenge", "access denied", "please verify you are a human"]):
                            status = "blocked"
                        else:
                            status = "ok"

                        safe_d = sanitize(domain)
                        ss_path = SCREENS_DIR / f"{safe_d}_live.jpg"
                        page.screenshot(path=str(ss_path), type="jpeg", quality=60)
                        if ss_path.exists() and ss_path.stat().st_size > 300 * 1024:
                            page.screenshot(path=str(ss_path), type="jpeg", quality=40)

                        record = {
                            "product": product,
                            "domain": domain,
                            "source": "live",
                            "url": found_url,
                            "captured_at": datetime.now(timezone.utc).isoformat(),
                            "status": status,
                            "text": page_text,
                            "html_sha256": h
                        }
                        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        out_file.flush()
                        print(f"  Live OK: {found_url} ({len(page_text)} chars)")
                    except Exception:
                        record = {
                            "product": product,
                            "domain": domain,
                            "source": "live",
                            "url": found_url,
                            "captured_at": datetime.now(timezone.utc).isoformat(),
                            "status": "error",
                            "text": "",
                            "html_sha256": ""
                        }
                        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        out_file.flush()
            else:
                live_pricing_url = f"https://{domain}/pricing"

            # --- 2. WAYBACK SNAPSHOTS ---
            if live_pricing_url:
                for wb_ts in ["20220615", "20240615"]:
                    wb_key = (domain, "wayback", wb_ts)
                    if wb_key in captured_keys:
                        continue

                    id_url, snap_status = get_wayback_snapshot(live_pricing_url, wb_ts)
                    if not id_url or snap_status != "ok":
                        record = {
                            "product": product,
                            "domain": domain,
                            "source": "wayback",
                            "snapshot_date": wb_ts,
                            "url": live_pricing_url,
                            "captured_at": datetime.now(timezone.utc).isoformat(),
                            "status": "no_snapshot",
                            "text": "",
                            "html_sha256": ""
                        }
                        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        out_file.flush()
                        continue

                    try:
                        resp = page.goto(id_url, timeout=20000, wait_until="domcontentloaded")
                        time.sleep(1.5)
                        page_text = page.evaluate("document.body.innerText") or ""
                        html_src = page.content()
                        h = hashlib.sha256(html_src.encode("utf-8")).hexdigest()

                        safe_d = sanitize(domain)
                        ss_path = SCREENS_DIR / f"{safe_d}_wb_{wb_ts}.jpg"
                        page.screenshot(path=str(ss_path), type="jpeg", quality=60)
                        if ss_path.exists() and ss_path.stat().st_size > 300 * 1024:
                            page.screenshot(path=str(ss_path), type="jpeg", quality=40)

                        record = {
                            "product": product,
                            "domain": domain,
                            "source": "wayback",
                            "snapshot_date": wb_ts,
                            "url": id_url,
                            "captured_at": datetime.now(timezone.utc).isoformat(),
                            "status": "ok",
                            "text": page_text,
                            "html_sha256": h
                        }
                        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        out_file.flush()
                        print(f"  WB {wb_ts} OK: ({len(page_text)} chars)")
                    except Exception:
                        record = {
                            "product": product,
                            "domain": domain,
                            "source": "wayback",
                            "snapshot_date": wb_ts,
                            "url": id_url,
                            "captured_at": datetime.now(timezone.utc).isoformat(),
                            "status": "error",
                            "text": "",
                            "html_sha256": ""
                        }
                        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        out_file.flush()

        browser.close()

    out_file.close()
    print("Pricing collection finished.")

if __name__ == "__main__":
    main()
