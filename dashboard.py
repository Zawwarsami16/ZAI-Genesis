"""
ZAI Genesis — Live Dashboard
by Zawwar (github.com/Zawwarsami16)

Dark terminal display — runs 24/7.
Auto-refreshes every 60 seconds.
Shows live prices, nature signals, world news, AI prediction.
Leave it running in the background — it keeps itself updated.
"""

import os
import json
import time
from datetime import datetime
from config import DATA_PATH, UPDATE_INTERVAL


# ANSI color codes for the dark terminal look
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[92m"
    CYAN    = "\033[96m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    BG_DARK = "\033[40m"

def clr():
    os.system("cls" if os.name == "nt" else "clear")


def build_signal_list(live, latest, news):
    """
    Builds a simple UP/DOWN/WAIT/DANGER verdict for each asset.
    This is the 'what should I know right now' section.
    Uses live price momentum + nature score + news signals together.
    """
    signals = []

    if not live:
        return signals

    pred       = (latest or {}).get("prediction", {})
    nat_score  = (latest or {}).get("nature_score", 0)
    news_sigs  = (news or {}).get("signals", {})
    war_count  = news_sigs.get("war_conflict", {}).get("count", 0) if isinstance(news_sigs.get("war_conflict"), dict) else news_sigs.get("war_conflict", 0)
    oil_count  = news_sigs.get("oil_energy",   {}).get("count", 0) if isinstance(news_sigs.get("oil_energy"),   dict) else news_sigs.get("oil_energy",   0)

    def verdict(key, label, is_risk_asset=True):
        d     = live.get(key, {})
        price = d.get("price", 0)
        chg   = d.get("change_pct", 0)

        # Start from price momentum
        if   chg >  2.0: v, reason = "UP",     "strong momentum today"
        elif chg >  0.5: v, reason = "UP",     "positive momentum"
        elif chg < -2.0: v, reason = "DOWN",   "selling pressure today"
        elif chg < -0.5: v, reason = "DOWN",   "mild selling"
        else:            v, reason = "WAIT",   "no clear momentum"

        # Adjust for news risk on risk assets
        if is_risk_asset and war_count >= 15 and oil_count >= 15:
            if v == "UP":
                v, reason = "WAIT", "momentum positive but war+oil signals elevated"
            elif v == "WAIT":
                v, reason = "WAIT", "war+oil signals elevated — no clear edge"

        # Oil specific
        if key == "oil":
            if price >= 110: v, reason = "DANGER", f"oil at ${price:.0f} — inflation trigger level"
            elif price >= 100: v, reason = "DANGER", f"oil at ${price:.0f} — psychological resistance"
            elif chg > 0:    v, reason = "UP",    f"rising — watch $100 level"

        # VIX specific (inverted — high VIX = market fear)
        if key == "vix":
            if price > 40:   v, reason = "DANGER", "extreme fear — possible capitulation"
            elif price > 30: v, reason = "DANGER", "high fear — market stressed"
            elif price > 20: v, reason = "WAIT",   "elevated uncertainty"
            else:            v, reason = "SAFE",   "low fear — markets calm"

        # Nature score boost
        if is_risk_asset and nat_score > 40 and v == "WAIT":
            v, reason = "UP", "nature agreement bullish"
        elif is_risk_asset and nat_score < -40 and v == "WAIT":
            v, reason = "DOWN", "nature agreement bearish"

        signals.append((label, key, price, chg, v, reason))

    verdict("btc",   "Bitcoin",  True)
    verdict("eth",   "Ethereum", True)
    verdict("sp500", "S&P 500",  True)
    verdict("nasdaq","NASDAQ",   True)
    verdict("gold",  "Gold",     False)
    verdict("oil",   "oil",      False)
    verdict("vix",   "VIX",      False)

    return signals

def g(text, color):
    return f"{color}{text}{C.RESET}"

def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


# ================================================================
# DISPLAY
# ================================================================
def display(tick, hw):
    clr()
    now  = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    spin = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"][tick % 10]

    # ── HEADER ──────────────────────────────────────────────
    print(g("╔══════════════════════════════════════════════════════════════╗", C.GREEN))
    print(g("║", C.GREEN) + g("      ZAI GENESIS  —  LAWS OF EVERYTHING                     ", C.BOLD + C.WHITE) + g("║", C.GREEN))
    print(g("║", C.GREEN) + g(f"      {now}   {spin} LIVE   by Zawwar              ", C.GRAY) + g("║", C.GREEN))
    print(g("╚══════════════════════════════════════════════════════════════╝", C.GREEN))

    # AI mode badge
    mode     = hw.get("ai_mode", "none")
    api_type = hw.get("api_type", "")
    if mode == "api":
        label = f"  AI: {api_type.upper()} — ACTIVE"
        mode_str = g(label, C.GREEN)
    elif mode == "ollama":
        mode_str = g(f"  AI: LOCAL ({hw.get('ollama_model','?')}) — FREE", C.CYAN)
    else:
        mode_str = g("  AI: RULE-BASED  (add GROQ_KEY to config.py for free AI)", C.YELLOW)
    print(mode_str)
    print()

    # ── LIVE MARKETS ────────────────────────────────────────
    live = load(f"{DATA_PATH}/live/prices.json")
    if live:
        print(g("  LIVE MARKETS", C.CYAN + C.BOLD))
        print(g("  " + "─"*58, C.GRAY))
        items = [
            ("S&P 500",  "sp500"),
            ("NASDAQ",   "nasdaq"),
            ("Gold",     "gold"),
            ("Oil WTI",  "oil"),
            ("VIX",      "vix"),
            ("Bitcoin",  "btc"),
            ("Ethereum", "eth"),
        ]
        for label, key in items:
            d = live.get(key)
            if not d:
                continue
            price = d.get("price", 0)
            chg   = d.get("change_pct", 0)
            arr   = g("↑", C.GREEN) if chg >= 0 else g("↓", C.RED)
            chg_c = g(f"{chg:+.2f}%", C.GREEN if chg >= 0 else C.RED)
            print(f"  {g(label, C.WHITE):<20}  {g(f'${price:>12,.2f}', C.YELLOW)}   {arr} {chg_c}")
    else:
        print(g("  No live data — run data_collector.py", C.YELLOW))
    print()

    # ── SIGNAL LIST — the main decision helper ───────────────
    news    = load(f"{DATA_PATH}/news/latest.json")
    latest2 = load(f"{DATA_PATH}/predictions/latest.json")
    sigs    = build_signal_list(live, latest2, news)

    if sigs:
        print(g("  SIGNAL LIST  — what to watch right now", C.GREEN + C.BOLD))
        print(g("  " + "─"*58, C.GRAY))
        v_icons = {
            "UP":     g("▲ UP    ", C.GREEN),
            "DOWN":   g("▼ DOWN  ", C.RED),
            "WAIT":   g("◆ WAIT  ", C.YELLOW),
            "DANGER": g("✖ DANGER", C.RED + C.BOLD),
            "SAFE":   g("● SAFE  ", C.CYAN),
        }
        for label, key, price, chg, verdict, reason in sigs:
            icon  = v_icons.get(verdict, g("? -----", C.GRAY))
            chg_c = g(f"{chg:+.1f}%", C.GREEN if chg >= 0 else C.RED)
            print(f"  {g(label, C.WHITE):<14} {icon}  {chg_c:<8}  {g(reason, C.GRAY)}")
        print()

    # ── NATURE ENGINES ──────────────────────────────────────
    latest = load(f"{DATA_PATH}/predictions/latest.json")
    if latest:
        engines = latest.get("engine_signals", {})
        score   = latest.get("nature_score", 0)
        nat_dir = latest.get("nature_direction", "NEUTRAL")

        print(g("  NATURE AGREEMENT", C.MAGENTA + C.BOLD))
        print(g("  " + "─"*58, C.GRAY))

        # Score bar
        bar_len = 30
        pos     = int((score + 100) / 200 * bar_len)
        bar     = g("█"*pos, C.GREEN) + g("░"*(bar_len-pos), C.GRAY)
        dir_col = C.GREEN if "BULL" in nat_dir else C.RED if "BEAR" in nat_dir else C.YELLOW
        print(f"  Score:  [{bar}]  {g(f'{score:+.1f}', dir_col)}  {g(nat_dir, dir_col + C.BOLD)}")
        print()

        # Each engine
        sig_icons = {"BULLISH": g("↑ BULL", C.GREEN), "BEARISH": g("↓ BEAR", C.RED), "NEUTRAL": g("→ NEUT", C.YELLOW)}
        for engine, sig in engines.items():
            icon = sig_icons.get(sig, g("? ----", C.GRAY))
            print(f"  {g(engine, C.WHITE):<18}  {icon}")
        print()

    # ── NEWS SIGNALS ────────────────────────────────────────
    news = load(f"{DATA_PATH}/news/latest.json")
    if news and news.get("signals"):
        print(g("  WORLD NEWS SIGNALS", C.CYAN + C.BOLD))
        print(g("  " + "─"*58, C.GRAY))
        for cat, info in list(news["signals"].items())[:5]:
            count = info.get("count", 0)
            bar   = g("█"*min(count,10), C.RED if count > 5 else C.YELLOW)
            print(f"  {g(cat, C.WHITE):<20}  {bar} ({count})")
        fetched = news.get("fetched_at","")[:16]
        print(g(f"  Last scan: {fetched}", C.GRAY))
        print()

    # ── AI PREDICTION ───────────────────────────────────────
    if latest and latest.get("prediction"):
        pred    = latest["prediction"]
        outlook = pred.get("overall_outlook", pred.get("overall_market_outlook", "N/A"))
        conf    = pred.get("confidence", 0)
        source  = pred.get("source", "unknown")
        summary = pred.get("summary", "")
        watch   = pred.get("top_watch", pred.get("most_important_indicator_to_watch",""))

        out_col = C.GREEN if "BULL" in str(outlook) else C.RED if "BEAR" in str(outlook) else C.YELLOW

        print(g("  GENESIS PREDICTION", C.GREEN + C.BOLD))
        print(g("  " + "─"*58, C.GRAY))
        print(f"  Outlook:    {g(str(outlook), out_col + C.BOLD)}")

        if conf:
            conf_bar = g("█"*(conf//10), C.CYAN) + g("░"*(10-conf//10), C.GRAY)
            print(f"  Confidence: [{conf_bar}] {g(str(conf)+'%', C.CYAN)}")

        preds = pred.get("predictions", {})
        if preds:
            print()
            print(g("  TIMELINE:", C.WHITE))
            for period, p in preds.items():
                d = p.get("direction","?")
                m = p.get("magnitude","?")
                r = p.get("reasoning","")[:50]
                ic = g("↑",C.GREEN) if d=="UP" else g("↓",C.RED) if d=="DOWN" else g("→",C.YELLOW)
                print(f"  {g(period, C.GRAY):<14} {ic} {g(d,C.WHITE):<10} ~{g(m,C.YELLOW)}  {g(r,C.GRAY)}")

        signals = pred.get("key_signals", [])
        if signals:
            print()
            print(g("  KEY SIGNALS:", C.WHITE))
            for s in signals[:3]:
                print(f"  {g('•',C.GREEN)} {s}")

        warnings = pred.get("warning_signs", [])
        if warnings:
            print()
            print(g("  WARNINGS:", C.RED))
            for w in warnings[:2]:
                print(f"  {g('⚠',C.RED)} {w}")

        if summary:
            print()
            print(g("  SUMMARY:", C.WHITE))
            # Word wrap at 58 chars
            words = summary.split()
            line  = "  "
            for word in words:
                if len(line) + len(word) > 60:
                    print(g(line, C.GRAY))
                    line = "  " + word + " "
                else:
                    line += word + " "
            if line.strip():
                print(g(line, C.GRAY))

        if watch:
            print()
            print(f"  {g('👁 WATCH:', C.CYAN)} {watch}")

        print(g(f"\n  Source: {source} | Generated: {latest.get('generated_at','')[:19]}", C.GRAY))
    else:
        print(g("  No prediction yet — run: python3 zai_genesis.py", C.YELLOW))

    # ── FOOTER ──────────────────────────────────────────────
    print()
    print(g("  " + "─"*58, C.GRAY))
    print(g(f"  Tick #{tick}  ·  Refresh in {UPDATE_INTERVAL}s  ·  Ctrl+C = stop", C.GRAY))


# ================================================================
# MAIN LOOP
# ================================================================
def run(hw):
    if not os.path.exists(DATA_PATH):
        print(g("No data found. Run: python3 zai_genesis.py", C.YELLOW))
        return

    tick          = 0
    last_analysis = 0
    ANALYSIS_INT  = 21600  # full re-analysis every 6 hours

    while True:
        try:
            display(tick, hw)
            time.sleep(UPDATE_INTERVAL)
            tick += 1

            # Live price update every tick
            try:
                from data_collector import update_live
                update_live()
            except Exception:
                pass

            # Full re-analysis every 6 hours
            if time.time() - last_analysis > ANALYSIS_INT:
                try:
                    from data_collector import fetch_news
                    from nature_engine  import run_all
                    from genesis_brain  import get_prediction, save_prediction

                    news_data   = fetch_news(max_feeds=8)
                    live_data   = load(f"{DATA_PATH}/live/prices.json") or {}
                    nature_res  = run_all(live_data=live_data)
                    prediction  = get_prediction(hw, nature_res, news_data, live_data)
                    save_prediction(prediction, nature_res)
                    last_analysis = time.time()
                except Exception as e:
                    pass

        except KeyboardInterrupt:
            print(g("\n\n  Stopped. — Zawwar\n", C.GREEN))
            break
        except Exception as e:
            time.sleep(10)


if __name__ == "__main__":
    hw = {"ai_mode": "none", "ollama_model": None}
    try:
        from hardware_detector import detect
        hw = detect()
    except Exception:
        pass
    run(hw)
