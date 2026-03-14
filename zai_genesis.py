"""
ZAI Genesis — Main Launcher
by Zawwar (github.com/Zawwarsami16)

One command runs everything:
  python3 zai_genesis.py

What it does:
1. Detects hardware + AI capabilities
2. Installs any missing packages automatically
3. Downloads data if first run
4. Runs all nature engines
5. Gets AI prediction (whatever is available)
6. Launches live dashboard

No setup needed. Just run it and it figures everything out.
Future: install Ollama or add API key — it auto-upgrades.
"""

import os
import sys
import subprocess
import json
from datetime import datetime


# ================================================================
# BANNER
# ================================================================
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print("""
\033[92m
  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║    ███████╗ █████╗ ██╗     ██████╗ ███████╗███╗   ██╗   ║
  ║       ███╔╝██╔══██╗██║    ██╔════╝ ██╔════╝████╗  ██║   ║
  ║      ███╔╝ ███████║██║    ██║  ███╗█████╗  ██╔██╗ ██║   ║
  ║     ███╔╝  ██╔══██║██║    ██║   ██║██╔══╝  ██║╚██╗██║   ║
  ║    ███████╗██║  ██║██║    ╚██████╔╝███████╗██║ ╚████║   ║
  ║    ╚══════╝╚═╝  ╚═╝╚═╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ║
  ║                                                          ║
  ║              G E N E S I S                               ║
  ║         Laws of Everything · Market Prediction           ║
  ║         by Zawwar · github.com/Zawwarsami16              ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
\033[0m""")


# ================================================================
# AUTO-INSTALL MISSING PACKAGES
# ================================================================
REQUIRED = ["requests", "pandas", "numpy", "yfinance", "psutil"]

def ensure_packages():
    print("\033[96m  Checking packages...\033[0m")
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            print(f"  Installing {pkg}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pkg,
                "--break-system-packages", "-q"
            ])
    print("\033[92m  All packages ready.\033[0m")


# ================================================================
# MAIN
# ================================================================
def main():
    banner()
    ensure_packages()

    # Hardware detection
    print("\033[96m\n  Scanning hardware...\033[0m")
    from hardware_detector import detect, print_report
    hw = detect()
    print_report(hw)

    # Setup data folders
    from data_collector import setup, existing_datasets, download_all, update_live, fetch_news
    setup()

    # Download historical data if first run
    existing = existing_datasets()
    if not existing:
        print("\033[93m  First run — downloading historical data (10-15 min)...\033[0m")
        download_all()
    else:
        print(f"\033[92m  Data ready: {len(existing)} datasets found.\033[0m")

    # Update live prices
    print("\033[96m  Fetching live prices...\033[0m")
    live_data = update_live()
    if live_data:
        for k, v in live_data.items():
            arr = "↑" if v["change_pct"] >= 0 else "↓"
            print(f"    {k:<10} ${v['price']:>12,.2f}  {arr} {v['change_pct']:+.2f}%")

    # Fetch world news
    print("\033[96m\n  Scanning world news...\033[0m")
    news_data = fetch_news(max_feeds=10)
    if news_data:
        print(f"  {news_data.get('total', 0)} articles — {len(news_data.get('signals',{}))} market categories detected")

    # Run nature engines
    print("\033[96m\n  Running nature engines...\033[0m")
    from nature_engine import run_all
    nature_result = run_all(live_data=live_data)

    print(f"\n  \033[1mNature Agreement Score: {nature_result['score']:+.1f}\033[0m")
    print(f"  Direction: {nature_result['direction']}")
    print()
    for name, data in nature_result["engines"].items():
        sig = data.get("signal","?")
        col = "\033[92m" if sig=="BULLISH" else "\033[91m" if sig=="BEARISH" else "\033[93m"
        rsn = data.get("reason","")[:60]
        print(f"  {col}{name:<18}  {sig:<10}\033[0m  {rsn}")

    # Get historical similarity (basic)
    hist_sim = "data not downloaded"
    try:
        import pandas as pd
        from config import DATA_PATH
        sp_path = f"{DATA_PATH}/historical/sp500.csv"
        if os.path.exists(sp_path):
            hist_sim = "S&P500 data available — crash pattern matching active"
    except Exception:
        pass

    # Get AI prediction
    print("\033[96m\n  Getting prediction...\033[0m")
    from genesis_brain import get_prediction, save_prediction
    prediction = get_prediction(hw, nature_result, news_data, live_data)

    if prediction:
        outlook = prediction.get("overall_outlook", prediction.get("overall_market_outlook","?"))
        summary = prediction.get("summary","")
        source  = prediction.get("source","unknown")
        col     = "\033[92m" if "BULL" in str(outlook) else "\033[91m" if "BEAR" in str(outlook) else "\033[93m"
        print(f"\n  Outlook: {col}{outlook}\033[0m")
        print(f"  Source:  {source}")
        if summary:
            print(f"  Summary: {summary[:120]}")

        save_prediction(prediction, nature_result)
        print("\033[92m  Prediction saved.\033[0m")

    # Launch dashboard
    print("\n\033[92m  All systems ready. Launching dashboard...\033[0m")
    print("\033[90m  Ctrl+C to stop.\033[0m\n")
    import time
    time.sleep(2)

    from dashboard import run
    run(hw)


if __name__ == "__main__":
    main()
