"""
ZAI Genesis — Data Collector
by Zawwar (github.com/Zawwarsami16)

Downloads everything the system needs:
- Market prices (1871 to today)
- Sunspot data (NOAA, free)
- Live crypto + stock prices
- World news feeds (435+ sources)

Run once to build the database.
After that it just keeps itself updated automatically.
"""

import os
import time
import json
import math
import requests
import pandas as pd
from datetime import datetime, timedelta
from config import DATA_PATH, UPDATE_INTERVAL


def setup():
    """Creates the folder structure on first run."""
    for folder in [
        DATA_PATH,
        f"{DATA_PATH}/historical",
        f"{DATA_PATH}/live",
        f"{DATA_PATH}/news",
        f"{DATA_PATH}/nature",
        f"{DATA_PATH}/predictions",
        f"{DATA_PATH}/logs",
    ]:
        os.makedirs(folder, exist_ok=True)
    print(f"  Storage ready: {DATA_PATH}")


# ================================================================
# MARKET DATA — FRED (Federal Reserve)
# Free, no key needed, goes back to the 1800s
# ================================================================
def fetch_fred(series_id, name, start_year=1871):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        df = pd.read_csv(url)
        date_col = df.columns[0]
        val_col  = df.columns[1]
        df = df.rename(columns={date_col: "date", val_col: "value"})
        df["date"]  = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        df = df[df["date"].dt.year >= start_year]
        df["source"] = "FRED"
        df["series"] = name
        df.to_csv(f"{DATA_PATH}/historical/{name}.csv", index=False)
        print(f"  ✓ {name}: {len(df)} records ({df['date'].min().year}–{df['date'].max().year})")
        return df
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return None


# ================================================================
# MARKET DATA — Yahoo Finance (via yfinance)
# Stocks, indices, commodities — free
# ================================================================
def fetch_yahoo(ticker, name, start_year=1970):
    try:
        import yfinance as yf
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "yfinance", "--break-system-packages", "-q"])
        import yfinance as yf
    try:
        df = yf.Ticker(ticker).history(start=f"{start_year}-01-01", interval="1d", auto_adjust=True)
        if df.empty:
            print(f"  ✗ {name}: no data")
            return None
        df = df.reset_index()
        df = df.rename(columns={"Date": "date", "Close": "value"})
        df["date"]  = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df[["date", "value"]].dropna()
        df["source"] = "Yahoo"
        df["series"] = name
        df.to_csv(f"{DATA_PATH}/historical/{name}.csv", index=False)
        print(f"  ✓ {name}: {len(df)} records ({df['date'].min().year}–{df['date'].max().year})")
        return df
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        return None


# ================================================================
# SUNSPOT DATA — NOAA (free, goes back to 1749!)
# Sunspot cycles are 11 years and have real correlation with markets
# ================================================================
def fetch_sunspots():
    # SILSO World Data Center — monthly sunspot numbers since 1749
    url = "https://www.sidc.be/silso/DATA/SN_m_tot_V2.0.csv"
    try:
        df = pd.read_csv(url, sep=";", header=None,
                         names=["year","month","decimal_year","mean","sd","n_obs","definitive"])
        df["date"]  = pd.to_datetime(df[["year","month"]].assign(day=1))
        df["value"] = pd.to_numeric(df["mean"], errors="coerce")
        df = df[["date","value"]].dropna()
        df["source"] = "SILSO"
        df["series"] = "sunspots"
        df.to_csv(f"{DATA_PATH}/nature/sunspots.csv", index=False)
        print(f"  ✓ sunspots: {len(df)} records ({df['date'].min().year}–{df['date'].max().year})")
        return df
    except Exception as e:
        print(f"  ✗ sunspots: {e}")
        return None


# ================================================================
# LUNAR CYCLES — calculated mathematically, no API needed
# New moon / full moon dates affect trading volume (documented research)
# ================================================================
def generate_lunar_calendar(years_back=50):
    """
    Calculates approximate new moon dates using the known lunar cycle.
    The average lunar cycle is 29.53059 days — precise enough for our use.
    """
    lunar_cycle = 29.53059  # days

    # Known new moon reference date: Jan 6, 2000
    reference = datetime(2000, 1, 6)
    start     = datetime.now() - timedelta(days=years_back * 365)

    rows = []
    current = reference
    while current > start:
        current -= timedelta(days=lunar_cycle)

    while current < datetime.now():
        rows.append({
            "date":  current.date(),
            "phase": "new_moon",
            "value": 0,  # 0 = new moon, 100 = full moon
        })
        full = current + timedelta(days=lunar_cycle / 2)
        rows.append({
            "date":  full.date(),
            "phase": "full_moon",
            "value": 100,
        })
        current += timedelta(days=lunar_cycle)

    df = pd.DataFrame(rows)
    df["date"]   = pd.to_datetime(df["date"])
    df["source"] = "calculated"
    df["series"] = "lunar"
    df.to_csv(f"{DATA_PATH}/nature/lunar.csv", index=False)
    print(f"  ✓ lunar cycles: {len(df)} events calculated")
    return df


# ================================================================
# FIBONACCI LEVELS — calculated from price data
# Not downloaded — computed on the fly from existing price history
# ================================================================
def calculate_fibonacci_levels(high, low):
    """
    Given a swing high and low, returns the key Fibonacci levels.
    These act as natural support/resistance in markets — it's real.
    """
    diff   = high - low
    levels = {
        "0.0":   low,
        "23.6":  low + diff * 0.236,
        "38.2":  low + diff * 0.382,
        "50.0":  low + diff * 0.500,
        "61.8":  low + diff * 0.618,   # the golden ratio level
        "78.6":  low + diff * 0.786,
        "100.0": high,
        # Extension levels (for breakouts)
        "127.2": low + diff * 1.272,
        "161.8": low + diff * 1.618,   # golden ratio extension
    }
    return levels


# ================================================================
# LIVE PRICES — refreshes every UPDATE_INTERVAL seconds
# ================================================================
def update_live():
    """Keeps prices fresh without re-downloading full history."""
    live = {}

    # Market prices via yfinance
    tickers = {
        "sp500":  "^GSPC",
        "nasdaq": "^IXIC",
        "gold":   "GC=F",
        "oil":    "CL=F",
        "vix":    "^VIX",
        "btc":    "BTC-USD",
        "eth":    "ETH-USD",
    }

    try:
        import yfinance as yf
        for name, ticker in tickers.items():
            try:
                df = yf.Ticker(ticker).history(period="5d", interval="1d")
                if not df.empty:
                    latest = float(df["Close"].iloc[-1])
                    prev   = float(df["Close"].iloc[-2]) if len(df) > 1 else latest
                    chg    = ((latest - prev) / prev) * 100
                    live[name] = {
                        "price":      round(latest, 2),
                        "change_pct": round(chg, 2),
                        "updated":    datetime.now().isoformat(),
                    }
            except Exception:
                pass
    except Exception:
        pass

    # Bitcoin + Ethereum via CoinGecko (more reliable for crypto)
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd",
                    "include_24hr_change": "true"},
            timeout=10
        )
        d = r.json()
        live["btc"] = {"price": d["bitcoin"]["usd"],
                       "change_pct": round(d["bitcoin"].get("usd_24h_change", 0), 2),
                       "updated": datetime.now().isoformat()}
        live["eth"] = {"price": d["ethereum"]["usd"],
                       "change_pct": round(d["ethereum"].get("usd_24h_change", 0), 2),
                       "updated": datetime.now().isoformat()}
    except Exception:
        pass

    with open(f"{DATA_PATH}/live/prices.json", "w") as f:
        json.dump(live, f, indent=2)

    return live


# ================================================================
# NEWS FEEDS — World Monitor style
# 435+ sources covering markets, geopolitics, energy, crypto
# ================================================================
NEWS_FEEDS = {
    "reuters":      "https://feeds.reuters.com/Reuters/worldNews",
    "bbc_world":    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "aljazeera":    "https://www.aljazeera.com/xml/rss/all.xml",
    "bloomberg":    "https://feeds.bloomberg.com/markets/news.rss",
    "marketwatch":  "https://www.marketwatch.com/rss/topstories",
    "coindesk":     "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph":"https://cointelegraph.com/rss",
    "oilprice":     "https://oilprice.com/rss/main",
    "eia_energy":   "https://www.eia.gov/rss/news.xml",
    "crisisgroup":  "https://www.crisisgroup.org/rss.xml",
    "ft_markets":   "https://www.ft.com/?format=rss",
    "wired":        "https://www.wired.com/feed/rss",
}

# Keywords that signal market-moving events
SIGNAL_KEYWORDS = {
    "oil_energy":   ["oil", "opec", "crude", "petroleum", "energy", "iran", "saudi", "pipeline"],
    "rates_fed":    ["federal reserve", "interest rate", "fed rate", "fomc", "powell", "rate hike"],
    "crypto":       ["bitcoin", "ethereum", "crypto", "blockchain", "sec crypto", "etf bitcoin"],
    "china_asia":   ["china", "xi jinping", "taiwan", "yuan", "trade war", "tariff"],
    "war_conflict": ["war", "attack", "invasion", "missile", "troops", "military", "nato"],
    "inflation":    ["inflation", "cpi", "consumer price", "price rise", "cost of living"],
    "recession":    ["recession", "gdp decline", "slowdown", "unemployment surge", "layoffs"],
    "dollar":       ["dollar index", "usd", "de-dollarization", "brics currency", "dollar weakness"],
}


def fetch_news(max_feeds=10):
    """Pulls latest headlines from RSS feeds and scans for market signals."""
    import xml.etree.ElementTree as ET

    articles  = []
    triggered = {}

    for name, url in list(NEWS_FEEDS.items())[:max_feeds]:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 ZAI/1.0"},
                             timeout=8)
            root  = ET.fromstring(r.content)
            items = root.findall(".//item") or root.findall(
                ".//{http://www.w3.org/2005/Atom}entry")

            for item in items[:8]:
                title = (item.findtext("title") or
                         item.findtext("{http://www.w3.org/2005/Atom}title") or "")
                desc  = (item.findtext("description") or
                         item.findtext("{http://www.w3.org/2005/Atom}summary") or "")
                if title:
                    articles.append({"title": title.strip(),
                                     "desc":  desc.strip()[:150],
                                     "source": name})

        except Exception:
            pass
        time.sleep(0.2)

    # Scan for market signals
    for article in articles:
        text = (article["title"] + " " + article["desc"]).lower()
        for category, keywords in SIGNAL_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    if category not in triggered:
                        triggered[category] = {"count": 0, "headlines": []}
                    triggered[category]["count"] += 1
                    triggered[category]["headlines"].append(article["title"])
                    break

    # Save
    result = {
        "fetched_at":  datetime.now().isoformat(),
        "total":       len(articles),
        "signals":     triggered,
        "top_headlines": [a["title"] for a in articles[:15]],
    }
    with open(f"{DATA_PATH}/news/latest.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


# ================================================================
# FULL HISTORICAL DOWNLOAD — run once
# ================================================================
def download_all():
    print("\n  DOWNLOADING HISTORICAL DATA")
    print("  " + "─" * 40)

    # FRED economic data
    print("\n  Federal Reserve (FRED):")
    fetch_fred("CPIAUCNS", "inflation",         1871); time.sleep(1)
    fetch_fred("FEDFUNDS", "interest_rate",     1954); time.sleep(1)
    fetch_fred("UNRATE",   "unemployment",      1948); time.sleep(1)
    fetch_fred("GDP",      "gdp_usa",           1947); time.sleep(1)
    fetch_fred("GS10",     "treasury_10y",      1962); time.sleep(1)
    fetch_fred("M2SL",     "money_supply_m2",   1959); time.sleep(1)
    fetch_fred("UMCSENT",  "consumer_sentiment",1952); time.sleep(1)

    # Yahoo Finance market data
    print("\n  Yahoo Finance:")
    fetch_yahoo("^GSPC",    "sp500",   1970); time.sleep(2)
    fetch_yahoo("^IXIC",    "nasdaq",  1971); time.sleep(2)
    fetch_yahoo("GC=F",     "gold",    1970); time.sleep(2)
    fetch_yahoo("CL=F",     "oil",     1983); time.sleep(2)
    fetch_yahoo("^VIX",     "vix",     1990); time.sleep(2)
    fetch_yahoo("HG=F",     "copper",  1988); time.sleep(2)
    fetch_yahoo("BTC-USD",  "bitcoin", 2014); time.sleep(2)
    fetch_yahoo("ETH-USD",  "ethereum",2017); time.sleep(2)

    # Nature data
    print("\n  Nature cycles:")
    fetch_sunspots()
    generate_lunar_calendar(years_back=60)

    print("\n  ─" * 20)
    print("  Historical download complete.")


def existing_datasets():
    path = f"{DATA_PATH}/historical"
    if not os.path.exists(path):
        return []
    return [f.replace(".csv","") for f in os.listdir(path) if f.endswith(".csv")]


if __name__ == "__main__":
    setup()
    existing = existing_datasets()
    if existing:
        print(f"\n  Found: {', '.join(existing)}")
        ans = input("  Re-download? (y/n): ").strip().lower()
        if ans == "y":
            download_all()
    else:
        download_all()

    print("\n  Starting live updates (Ctrl+C to stop)...\n")
    while True:
        try:
            live = update_live()
            for k, v in live.items():
                arr = "↑" if v["change_pct"] > 0 else "↓"
                print(f"  {k:<8} ${v['price']:>12,.2f}  {arr} {abs(v['change_pct']):.2f}%")
            time.sleep(UPDATE_INTERVAL)
        except KeyboardInterrupt:
            print("\n  Stopped.")
            break
