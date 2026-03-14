"""
ZAI Genesis — Nature Engine
by Zawwar (github.com/Zawwarsami16)

This is the part that makes Genesis different from every other tool.
It reads markets through the lens of natural laws:

- Fibonacci & Golden Ratio  (nature's own proportions show up in price moves)
- Elliott Wave Theory       (markets move in predictable wave structures)
- Kondratiev Supercycles    (50-60 year economic waves — real and documented)
- Sunspot cycles            (11 year cycle, market correlation is statistically significant)
- Lunar cycles              (volume and volatility studies show lunar correlation)
- Seasonal patterns         (sell in May, Q4 rally — these patterns repeat)
- Fear & Greed psychology   (human behavior follows predictable emotional cycles)

Each engine gives a signal: BULLISH, BEARISH, or NEUTRAL.
The Nature Agreement Score counts how many agree.
"""

import os
import json
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import DATA_PATH


# ================================================================
# FIBONACCI ENGINE
# Markets respect Fibonacci levels because humans subconsciously use them.
# The 61.8% level (golden ratio) is the most powerful.
# ================================================================
def fibonacci_analysis(prices_series):
    """
    Finds Fibonacci support/resistance levels and checks where
    the current price sits relative to them.
    """
    if prices_series is None or len(prices_series) < 20:
        return {"signal": "NEUTRAL", "reason": "not enough data", "levels": {}}

    recent = prices_series.dropna().tail(200)
    high   = float(recent.max())
    low    = float(recent.min())
    curr   = float(recent.iloc[-1])

    diff   = high - low
    if diff == 0:
        return {"signal": "NEUTRAL", "reason": "no price range", "levels": {}}

    # Key Fibonacci retracement levels
    levels = {
        "0.0%":   round(low, 2),
        "23.6%":  round(low + diff * 0.236, 2),
        "38.2%":  round(low + diff * 0.382, 2),
        "50.0%":  round(low + diff * 0.500, 2),
        "61.8%":  round(low + diff * 0.618, 2),   # golden ratio — most important
        "78.6%":  round(low + diff * 0.786, 2),
        "100.0%": round(high, 2),
    }

    # Where is current price in the range?
    position = (curr - low) / diff  # 0.0 = at low, 1.0 = at high

    # Signal logic: above 61.8% = extended, potential reversal
    if position > 0.786:
        signal = "BEARISH"
        reason = f"price at {position*100:.1f}% of range — above 78.6% Fibonacci extension"
    elif position > 0.618:
        signal = "BEARISH"
        reason = f"price at {position*100:.1f}% — above golden ratio (61.8%) level, overbought"
    elif position < 0.236:
        signal = "BULLISH"
        reason = f"price at {position*100:.1f}% — near bottom, at support"
    elif 0.382 <= position <= 0.500:
        signal = "BULLISH"
        reason = f"price at {position*100:.1f}% — healthy 38.2-50% retracement zone"
    else:
        signal = "NEUTRAL"
        reason = f"price at {position*100:.1f}% — between key levels"

    return {
        "signal":   signal,
        "reason":   reason,
        "levels":   levels,
        "current":  round(curr, 2),
        "position": round(position * 100, 1),
        "high":     round(high, 2),
        "low":      round(low, 2),
    }


# ================================================================
# ELLIOTT WAVE ENGINE
# Markets move in 5-wave impulse patterns then 3-wave corrections.
# This detects which wave we might be in.
# ================================================================
def elliott_wave_analysis(prices_series):
    """
    Simplified Elliott Wave position detection.
    Looks for the wave structure in recent price action.
    """
    if prices_series is None or len(prices_series) < 50:
        return {"signal": "NEUTRAL", "wave_position": "unknown", "reason": "not enough data"}

    recent = prices_series.dropna().tail(100)
    pct_changes = recent.pct_change().dropna()

    # Count consecutive up/down moves to estimate wave position
    up_moves   = (pct_changes > 0).sum()
    down_moves = (pct_changes < 0).sum()
    total      = len(pct_changes)

    up_ratio = up_moves / total if total > 0 else 0.5

    # Recent momentum
    last_20   = pct_changes.tail(20)
    last_5    = pct_changes.tail(5)
    momentum  = float(last_20.mean()) * 100
    recent_m  = float(last_5.mean())  * 100

    # Trend strength
    first_half = float(recent.iloc[:len(recent)//2].mean())
    second_half= float(recent.iloc[len(recent)//2:].mean())
    trend_up   = second_half > first_half

    # Wave position estimation
    if up_ratio > 0.65 and recent_m > 0:
        wave = "Wave 5 (final impulse)"
        signal = "BEARISH"
        reason = "strong extended uptrend — likely completing Wave 5, correction ahead"
    elif up_ratio > 0.55 and trend_up:
        wave = "Wave 3 (strongest impulse)"
        signal = "BULLISH"
        reason = "sustained uptrend, momentum building — characteristic of Wave 3"
    elif up_ratio < 0.4 and recent_m < 0:
        wave = "Wave C (final correction)"
        signal = "BULLISH"
        reason = "deep correction in progress — Wave C bottom may be near"
    elif up_ratio < 0.45 and not trend_up:
        wave = "Wave A-B (early correction)"
        signal = "BEARISH"
        reason = "correction beginning — more downside likely before reversal"
    else:
        wave = "Consolidation / Wave 2 or 4"
        signal = "NEUTRAL"
        reason = "no clear wave impulse detected — consolidation phase"

    return {
        "signal":        signal,
        "wave_position": wave,
        "reason":        reason,
        "up_ratio":      round(up_ratio * 100, 1),
        "momentum":      round(momentum, 3),
    }


# ================================================================
# KONDRATIEV SUPERCYCLE
# 50-60 year economic waves — Winter/Spring/Summer/Autumn
# We're somewhere in this cycle right now
# ================================================================
def kondratiev_cycle():
    """
    Estimates where we are in the Kondratiev supercycle.
    The last Winter (depression) was 1930s. The current cycle started ~1950.
    Each phase lasts ~13-15 years.
    """
    # Known cycle phases (approximate)
    # Spring: 1950-1966 (postwar boom)
    # Summer: 1966-1980 (inflation, volatility)
    # Autumn: 1980-2000 (debt expansion, financialization)
    # Winter: 2000-2020 (deleveraging, deflation risk)
    # New Spring: 2020+ (stimulus, new tech cycle)

    current_year = datetime.now().year

    if 2020 <= current_year <= 2033:
        phase  = "New Spring"
        signal = "BULLISH"
        reason = "Kondratiev New Spring (2020-2033) — recovery, new technology adoption, expansion"
    elif 2033 <= current_year <= 2046:
        phase  = "Summer"
        signal = "BEARISH"
        reason = "Kondratiev Summer — inflation returns, commodity super-cycle, volatility"
    else:
        phase  = "Transition"
        signal = "NEUTRAL"
        reason = "cycle position uncertain at this date"

    return {
        "signal": signal,
        "phase":  phase,
        "reason": reason,
        "cycle":  "50-60 year Kondratiev supercycle",
    }


# ================================================================
# SUNSPOT CYCLE ENGINE
# 11-year cycle. Market returns are statistically different at
# solar maximum vs solar minimum — documented in financial research.
# ================================================================
def sunspot_analysis():
    """
    Loads NOAA sunspot data and determines where we are in the cycle.
    Solar maximum tends to correlate with market tops.
    Solar minimum with bottoms and recoveries.
    """
    path = f"{DATA_PATH}/nature/sunspots.csv"
    if not os.path.exists(path):
        return {"signal": "NEUTRAL", "reason": "sunspot data not downloaded yet"}

    try:
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.sort_values("date")

        # Last 15 years
        recent = df.tail(180)
        current_count = float(recent["value"].iloc[-1])
        avg_count     = float(recent["value"].mean())
        max_count     = float(recent["value"].max())

        # Where in cycle? High = near maximum, low = near minimum
        cycle_position = current_count / max_count if max_count > 0 else 0.5

        # 12-month trend
        trend_val = float(recent.tail(12)["value"].mean()) - float(recent.head(12)["value"].mean())

        if cycle_position > 0.8:
            signal = "BEARISH"
            reason = f"near solar maximum (activity: {current_count:.0f}) — historically precedes market volatility"
        elif cycle_position < 0.3 and trend_val > 0:
            signal = "BULLISH"
            reason = f"past solar minimum, rising (activity: {current_count:.0f}) — historically positive for markets"
        elif cycle_position < 0.2:
            signal = "NEUTRAL"
            reason = f"at solar minimum (activity: {current_count:.0f}) — transition phase"
        else:
            signal = "NEUTRAL"
            reason = f"mid-cycle (activity: {current_count:.0f}) — no strong solar signal"

        return {
            "signal":         signal,
            "reason":         reason,
            "current_count":  round(current_count, 1),
            "cycle_position": round(cycle_position * 100, 1),
            "trend":          "rising" if trend_val > 0 else "falling",
        }

    except Exception as e:
        return {"signal": "NEUTRAL", "reason": f"error: {e}"}


# ================================================================
# LUNAR CYCLE ENGINE
# Studies show trading volume and volatility shift around new/full moons.
# Returns are slightly lower around full moons (higher risk aversion).
# ================================================================
def lunar_analysis():
    """
    Checks where we are in the current lunar cycle.
    Days to next new moon / full moon affect sentiment.
    """
    # Known new moon reference: Jan 6, 2000
    reference    = datetime(2000, 1, 6)
    lunar_cycle  = 29.53059
    now          = datetime.now()

    elapsed = (now - reference).total_seconds() / 86400
    phase   = elapsed % lunar_cycle  # 0 = new moon, ~14.76 = full moon

    days_to_new  = lunar_cycle - phase
    days_to_full = abs(lunar_cycle / 2 - phase)

    # Phase name
    if phase < 1.5 or phase > lunar_cycle - 1.5:
        phase_name = "new moon"
        signal     = "BULLISH"
        reason     = "new moon — research shows slightly positive market bias in following week"
    elif lunar_cycle/2 - 1.5 < phase < lunar_cycle/2 + 1.5:
        phase_name = "full moon"
        signal     = "BEARISH"
        reason     = "full moon — studies show slightly elevated risk aversion and volatility"
    elif phase < lunar_cycle / 4:
        phase_name = "waxing crescent"
        signal     = "BULLISH"
        reason     = "waxing phase — historically mild positive bias"
    elif phase > 3 * lunar_cycle / 4:
        phase_name = "waning crescent"
        signal     = "NEUTRAL"
        reason     = "waning phase — mixed historical returns"
    else:
        phase_name = "waxing/waning gibbous"
        signal     = "NEUTRAL"
        reason     = "mid-cycle — no strong lunar signal"

    return {
        "signal":        signal,
        "reason":        reason,
        "phase":         phase_name,
        "days_to_new":   round(days_to_new, 1),
        "days_to_full":  round(days_to_full, 1),
        "cycle_day":     round(phase, 1),
    }


# ================================================================
# SEASONAL PATTERNS
# Month-of-year effects are one of the most consistent market anomalies.
# "Sell in May", the Santa Claus rally, October volatility — all real.
# ================================================================
def seasonal_analysis():
    """
    Returns the seasonal bias based on month and quarter.
    Based on 100+ years of S&P 500 seasonal data.
    """
    now   = datetime.now()
    month = now.month
    day   = now.day

    # Average monthly S&P 500 returns (historical averages, rough)
    monthly_bias = {
        1:  ("January Effect", "BULLISH",  "January historically strong — new money, tax-loss buying reversal"),
        2:  ("February",       "NEUTRAL",  "February mixed — digesting January moves"),
        3:  ("March",          "NEUTRAL",  "March variable — end of Q1 positioning"),
        4:  ("April",          "BULLISH",  "April historically strongest month of the year"),
        5:  ("Sell in May",    "BEARISH",  "May — start of weakest 6-month period (May-October)"),
        6:  ("June",           "BEARISH",  "June often weak — mid-year profit taking"),
        7:  ("July",           "BULLISH",  "July often recovers — summer rally"),
        8:  ("August",         "BEARISH",  "August frequently volatile and negative"),
        9:  ("September",      "BEARISH",  "September is statistically the worst month of the year"),
        10: ("October",        "NEUTRAL",  "October volatile but often marks bottoms"),
        11: ("November",       "BULLISH",  "November strong — pre-holiday buying"),
        12: ("Santa Rally",    "BULLISH",  "December strong — Santa Claus rally, year-end window dressing"),
    }

    name, signal, reason = monthly_bias.get(month, ("Unknown", "NEUTRAL", "No seasonal data"))

    # Q4 bonus
    if month in [10, 11, 12]:
        q4_note = " | Q4 historically strongest quarter"
        reason += q4_note

    return {
        "signal":  signal,
        "reason":  reason,
        "month":   name,
        "quarter": f"Q{(month-1)//3 + 1}",
    }


# ================================================================
# PSYCHOLOGY ENGINE
# Fear & Greed cycle — markets move on emotion, not just fundamentals.
# VIX above 30 = fear. Below 15 = greed. Extremes signal reversals.
# ================================================================
def psychology_analysis(live_data):
    """
    Uses VIX (fear index) and market momentum to detect crowd psychology.
    Extreme fear = buy opportunity. Extreme greed = sell signal.
    """
    vix_data = live_data.get("vix", {})
    sp_data  = live_data.get("sp500", {})

    if not vix_data:
        return {"signal": "NEUTRAL", "reason": "no VIX data available", "state": "unknown"}

    vix     = vix_data.get("price", 20)
    sp_chg  = sp_data.get("change_pct", 0)

    # VIX interpretation
    if vix > 40:
        state  = "EXTREME FEAR"
        signal = "BULLISH"
        reason = f"VIX at {vix:.1f} — extreme fear, historically a strong buy signal"
    elif vix > 30:
        state  = "FEAR"
        signal = "BULLISH"
        reason = f"VIX at {vix:.1f} — elevated fear, market oversold conditions"
    elif vix > 20:
        state  = "CAUTION"
        signal = "NEUTRAL"
        reason = f"VIX at {vix:.1f} — uncertainty, wait for direction"
    elif vix < 12:
        state  = "EXTREME GREED"
        signal = "BEARISH"
        reason = f"VIX at {vix:.1f} — extreme complacency, historically a warning signal"
    elif vix < 15:
        state  = "GREED"
        signal = "BEARISH"
        reason = f"VIX at {vix:.1f} — low fear, market potentially overbought"
    else:
        state  = "NEUTRAL"
        signal = "NEUTRAL"
        reason = f"VIX at {vix:.1f} — normal range, no strong sentiment signal"

    return {
        "signal": signal,
        "reason": reason,
        "state":  state,
        "vix":    round(vix, 1),
    }


# ================================================================
# NATURE AGREEMENT SCORE
# The core of Genesis — how many natural laws agree on direction?
# ================================================================
def calculate_agreement_score(signals):
    """
    Takes all engine signals and calculates the overall agreement.
    Returns a score from -100 (all bearish) to +100 (all bullish).
    """
    bullish = sum(1 for s in signals.values() if s.get("signal") == "BULLISH")
    bearish = sum(1 for s in signals.values() if s.get("signal") == "BEARISH")
    neutral = sum(1 for s in signals.values() if s.get("signal") == "NEUTRAL")
    total   = len(signals)

    if total == 0:
        return 0, "NEUTRAL", 0

    score      = ((bullish - bearish) / total) * 100
    confidence = ((bullish + bearish) / total) * 100  # how many gave a strong signal

    if score > 40:
        direction = "BULLISH"
    elif score < -40:
        direction = "BEARISH"
    elif score > 15:
        direction = "MILDLY BULLISH"
    elif score < -15:
        direction = "MILDLY BEARISH"
    else:
        direction = "NEUTRAL"

    return round(score, 1), direction, round(confidence, 1)


# ================================================================
# RUN ALL ENGINES
# ================================================================
def run_all(live_data=None, prices=None):
    """Runs every nature engine and returns combined results."""
    signals = {}

    # Load S&P 500 prices for technical analysis
    sp500_prices = None
    try:
        sp_path = f"{DATA_PATH}/historical/sp500.csv"
        if os.path.exists(sp_path):
            df = pd.read_csv(sp_path, parse_dates=["date"])
            sp500_prices = df.set_index("date")["value"]
    except Exception:
        pass

    signals["fibonacci"]   = fibonacci_analysis(sp500_prices)
    signals["elliott"]     = elliott_wave_analysis(sp500_prices)
    signals["kondratiev"]  = kondratiev_cycle()
    signals["sunspots"]    = sunspot_analysis()
    signals["lunar"]       = lunar_analysis()
    signals["seasonal"]    = seasonal_analysis()
    signals["psychology"]  = psychology_analysis(live_data or {})

    score, direction, confidence = calculate_agreement_score(signals)

    return {
        "engines":    signals,
        "score":      score,
        "direction":  direction,
        "confidence": confidence,
        "timestamp":  datetime.now().isoformat(),
    }


if __name__ == "__main__":
    # Quick test — no data needed for most engines
    live = {"vix": {"price": 27.2, "change_pct": -0.4},
            "sp500": {"price": 6632, "change_pct": -0.6}}

    result = run_all(live_data=live)

    print("\nNATURE ENGINE RESULTS")
    print("─" * 50)
    for name, data in result["engines"].items():
        sig = data.get("signal", "?")
        rsn = data.get("reason", "")[:60]
        print(f"  {name:<15} {sig:<10} {rsn}")

    print("─" * 50)
    print(f"  AGREEMENT SCORE: {result['score']:+.1f}")
    print(f"  DIRECTION:       {result['direction']}")
    print(f"  CONFIDENCE:      {result['confidence']}%")
