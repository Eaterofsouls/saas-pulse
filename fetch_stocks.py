import pandas as pd
import yfinance as yf
from pathlib import Path
import time

COMPANIES_CSV = Path("saas_pulse/dataset/companies.csv")
OUT_CSV = Path("saas_pulse/dataset/stock_performance.csv")

def main():
    df_comp = pd.read_csv(COMPANIES_CSV)
    tickers = df_comp["ticker"].tolist()
    
    # Add benchmark ETFs
    benchmarks = ["IGV", "SPY"]
    all_symbols = tickers + benchmarks
    
    print(f"Downloading historical stock data for {len(all_symbols)} symbols (2023-01-01 to present)...")
    
    # Download in bulk
    data = yf.download(all_symbols, start="2023-01-01", auto_adjust=True, progress=False)
    
    adj_close = data["Close"]
    
    # Determine benchmark returns
    igv_start = adj_close["IGV"].dropna().iloc[0]
    igv_end = adj_close["IGV"].dropna().iloc[-1]
    igv_return = ((igv_end - igv_start) / igv_start) * 100.0
    
    spy_start = adj_close["SPY"].dropna().iloc[0]
    spy_end = adj_close["SPY"].dropna().iloc[-1]
    spy_return = ((spy_end - spy_start) / spy_start) * 100.0
    
    print(f"Benchmark IGV Return (2023 to present): {igv_return:.2f}%")
    print(f"Benchmark SPY Return (2023 to present): {spy_return:.2f}%")
    
    results = []
    missing = []
    
    for _, row in df_comp.iterrows():
        t = row["ticker"]
        name = row["name"]
        cat = row["category"]
        
        if t in adj_close.columns:
            series = adj_close[t].dropna()
            if len(series) >= 10:
                p_start = series.iloc[0]
                p_end = series.iloc[-1]
                p_min = series.min()
                p_max = series.max()
                ret = ((p_end - p_start) / p_start) * 100.0
                excess_igv = ret - igv_return
                
                results.append({
                    "ticker": t,
                    "name": name,
                    "category": cat,
                    "price_start_2023": round(float(p_start), 2),
                    "price_latest": round(float(p_end), 2),
                    "return_pct": round(float(ret), 2),
                    "excess_return_vs_igv": round(float(excess_igv), 2),
                    "max_drawdown_ref_min": round(float(p_min), 2),
                    "max_high": round(float(p_max), 2),
                    "status": "ok"
                })
                continue
        missing.append(t)
        results.append({
            "ticker": t,
            "name": name,
            "category": cat,
            "price_start_2023": None,
            "price_latest": None,
            "return_pct": None,
            "excess_return_vs_igv": None,
            "max_drawdown_ref_min": None,
            "max_high": None,
            "status": "no_stock_data"
        })
        
    out_df = pd.DataFrame(results)
    out_df.to_csv(OUT_CSV, index=False)
    print(f"Saved {len(out_df)} records to {OUT_CSV}")
    print(f"Stocks with clean pricing: {len(results) - len(missing)}/100")
    if missing:
        print("Missing symbols:", missing)

if __name__ == "__main__":
    main()
