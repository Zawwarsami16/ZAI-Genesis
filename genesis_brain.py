"""
ZAI Genesis — AI Brain
by Zawwar (github.com/Zawwarsami16)

Sends all signals to best available AI and gets a prediction.

Priority order (auto-selected):
1. Groq API     — free, fastest (llama3-70b in seconds)
2. Gemini API   — free tier, fast
3. Claude API   — paid but very accurate
4. Ollama local — free, slow on CPU
5. Rule-based   — always works, no AI needed

To add Groq: put GROQ_KEY in config.py — done, nothing else to change.
To add any other provider: see the pattern in this file and follow it.
"""

import os
import json
import subprocess
import requests as req
from datetime import datetime
from config import DATA_PATH


# ================================================================
# PROMPT BUILDER
# Kept short intentionally — learned from phi3:mini timeout experience
# ================================================================
def build_prompt(nature_result, news_data, live_data):
    engines = nature_result.get("engines", {})

    engine_summary = {
        name: {
            "signal": data.get("signal"),
            "reason": data.get("reason", "")[:80],
        }
        for name, data in engines.items()
    }

    top_news = {}
    if news_data and news_data.get("signals"):
        for cat, info in list(news_data["signals"].items())[:4]:
            count = info.get("count", 0) if isinstance(info, dict) else info
            top_news[cat] = count

    live_snap = {}
    for k, v in (live_data or {}).items():
        if isinstance(v, dict):
            live_snap[k] = f"${v.get('price',0):,.0f} ({v.get('change_pct',0):+.1f}%)"

    prompt = f"""You are ZAI Genesis — a market prediction AI that reads natural laws and cycles.

NATURE AGREEMENT SCORE: {nature_result.get('score', 0):+.1f} ({nature_result.get('direction', 'NEUTRAL')})

ENGINE SIGNALS:
{json.dumps(engine_summary, indent=1)}

NEWS SIGNALS TODAY:
{json.dumps(top_news)}

LIVE MARKETS:
{json.dumps(live_snap)}

Based on natural laws, cycles, and market data — give your market prediction.
Reply ONLY in this exact JSON format, no other text outside it:
{{
  "overall_outlook": "BULLISH/BEARISH/NEUTRAL/VOLATILE",
  "confidence": 0-100,
  "predictions": {{
    "4_weeks":  {{"direction": "UP/DOWN/SIDEWAYS", "magnitude": "X%", "reasoning": "short reason"}},
    "3_months": {{"direction": "UP/DOWN/SIDEWAYS", "magnitude": "X%", "reasoning": "short reason"}},
    "6_months": {{"direction": "UP/DOWN/SIDEWAYS", "magnitude": "X%", "reasoning": "short reason"}}
  }},
  "key_signals": ["signal1", "signal2", "signal3"],
  "warning_signs": ["warning1", "warning2"],
  "crypto_outlook": "one sentence on crypto",
  "top_watch": "single most important thing to watch",
  "summary": "2 sentence plain English summary"
}}"""
    return prompt


# ================================================================
# GROQ — Free, fastest, uses llama3-70b
# Get key: groq.com → sign up → API Keys
# ================================================================
def groq_get_best_model(api_key):
    """Fetches available models from Groq and picks the best one."""
    try:
        r = req.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        models = [m["id"] for m in r.json().get("data", [])]
        # Preference order — pick first available
        preferred = [
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-8b-8192",
        ]
        for p in preferred:
            if p in models:
                return p
        # Fallback: any chat model
        for m in models:
            if "llama" in m.lower() and "guard" not in m.lower():
                return m
        return models[0] if models else None
    except Exception:
        return "llama-3.3-70b-versatile"


def groq_predict(prompt, api_key):
    model = groq_get_best_model(api_key)
    if not model:
        print("  Groq: no models available")
        return None
    print(f"  Groq model: {model}")
    try:
        r = req.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       model,
                "messages":    [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens":  1000,
            },
            timeout=30
        )
        data = r.json()

        if "error" in data:
            print(f"  Groq error: {data['error'].get('message', 'unknown')}")
            return None

        text  = data["choices"][0]["message"]["content"]
        text  = text.replace("```json", "").replace("```", "").strip()
        # Remove any trailing comments inside JSON (LLMs sometimes add them)
        import re
        text = re.sub(r'//.*', '', text)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                result           = json.loads(text[start:end])
                result["source"] = f"groq:{model}"
                return result
            except json.JSONDecodeError:
                # Try fixing common issues
                clean = text[start:end]
                clean = re.sub(r',\s*}', '}', clean)
                clean = re.sub(r',\s*]', ']', clean)
                result           = json.loads(clean)
                result["source"] = f"groq:{model}"
                return result

    except Exception as e:
        print(f"  Groq error: {e}")
    return None


# ================================================================
# GEMINI — Google AI Studio free tier
# Get key: aistudio.google.com/app/api-keys
# ================================================================
def gemini_predict(prompt, api_key):
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            r = req.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000},
                },
                timeout=30
            )
            data = r.json()

            if "error" in data:
                print(f"  Gemini {model}: {data['error'].get('message','')}")
                continue

            text  = data["candidates"][0]["content"]["parts"][0]["text"]
            text  = text.replace("```json", "").replace("```", "").strip()
            start = text.find("{")
            end   = text.rfind("}") + 1
            if start >= 0 and end > start:
                result           = json.loads(text[start:end])
                result["source"] = f"gemini:{model}"
                print(f"  Gemini success ({model})")
                return result

        except Exception as e:
            print(f"  Gemini {model}: {e}")
            continue
    return None


# ================================================================
# CLAUDE — Anthropic API
# Get key: console.anthropic.com
# ================================================================
def claude_predict(prompt, api_key):
    try:
        r = req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages":   [{"role": "user", "content": prompt}],
            },
            timeout=30
        )
        data = r.json()
        if "content" in data:
            text  = data["content"][0]["text"]
            text  = text.replace("```json", "").replace("```", "").strip()
            start = text.find("{")
            end   = text.rfind("}") + 1
            if start >= 0 and end > start:
                result           = json.loads(text[start:end])
                result["source"] = "claude"
                return result
    except Exception as e:
        print(f"  Claude error: {e}")
    return None


# ================================================================
# OLLAMA — local model, slow on CPU but free forever
# ================================================================
def ollama_predict(prompt, model):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0 and result.stdout.strip():
            text  = result.stdout.strip()
            start = text.find("{")
            end   = text.rfind("}") + 1
            if start >= 0 and end > start:
                r           = json.loads(text[start:end])
                r["source"] = f"ollama:{model}"
                return r
    except subprocess.TimeoutExpired:
        print("  Ollama timed out")
    except Exception as e:
        print(f"  Ollama error: {e}")
    return None


# ================================================================
# RULE-BASED — always works, no AI needed
# Pure logic from nature signals
# ================================================================
def rule_based_predict(nature_result, news_data, live_data):
    score    = nature_result.get("score", 0)
    direction= nature_result.get("direction", "NEUTRAL")
    engines  = nature_result.get("engines", {})

    news_signals  = (news_data or {}).get("signals", {})
    war_count  = (news_signals.get("war_conflict") or {}).get("count", 0) if isinstance(news_signals.get("war_conflict"), dict) else int(news_signals.get("war_conflict", 0))
    oil_count  = (news_signals.get("oil_energy") or {}).get("count", 0) if isinstance(news_signals.get("oil_energy"), dict) else int(news_signals.get("oil_energy", 0))
    news_risk  = war_count >= 10 or oil_count >= 10

    # Timeline based on score
    if score > 40:
        outlook = "BULLISH"
        p4w = {"direction": "UP",       "magnitude": "3-7%",  "reasoning": "Strong nature law agreement — bullish"}
        p3m = {"direction": "UP",       "magnitude": "8-15%", "reasoning": "Multiple cycles aligned positive"}
        p6m = {"direction": "UP",       "magnitude": "10-20%","reasoning": "Macro + nature both positive"}
    elif score < -40:
        outlook = "BEARISH"
        p4w = {"direction": "DOWN",     "magnitude": "3-8%",  "reasoning": "Strong bearish law agreement"}
        p3m = {"direction": "DOWN",     "magnitude": "10-20%","reasoning": "Multiple cycles aligned negative"}
        p6m = {"direction": "SIDEWAYS", "magnitude": "0-10%", "reasoning": "Bear markets stabilize after 6 months"}
    else:
        outlook = "NEUTRAL"
        p4w = {"direction": "SIDEWAYS", "magnitude": "0-2%",  "reasoning": "Nature signals balanced — no strong bias"}
        p3m = {"direction": "SIDEWAYS", "magnitude": "0-5%",  "reasoning": "No dominant cycle signal"}
        p6m = {"direction": "UP",       "magnitude": "3-7%",  "reasoning": "Long-term markets tend to rise"}

    bullish = [k for k, v in engines.items() if v.get("signal") == "BULLISH"]
    bearish = [k for k, v in engines.items() if v.get("signal") == "BEARISH"]
    vix     = (live_data or {}).get("vix", {}).get("price", 20)

    return {
        "source":         "rule_based",
        "overall_outlook": outlook,
        "confidence":     50 + abs(score) // 2,
        "predictions": {"4_weeks": p4w, "3_months": p3m, "6_months": p6m},
        "key_signals":    bullish[:3] if bullish else ["kondratiev", "seasonal"],
        "warning_signs":  [f"oil_energy ({oil_count} articles)", f"war_conflict ({war_count} articles)"] if news_risk else ["no major warnings"],
        "crypto_outlook": "HIGH VOLATILITY — follow VIX closely" if vix > 25 else "Stable — risk-on environment",
        "top_watch":      "VIX + Oil — these move everything else right now",
        "summary": (
            f"Nature Agreement Score: {score:+.1f} ({direction}). "
            f"{len(bullish)} laws bullish, {len(bearish)} bearish. "
            f"{'Elevated geopolitical risk — caution advised. ' if news_risk else ''}"
            f"Add Groq key (free) to config.py for AI-enhanced analysis."
        ),
        "generated_at": datetime.now().isoformat(),
    }


# ================================================================
# MAIN — auto-selects best available AI
# ================================================================
def get_prediction(hw, nature_result, news_data, live_data):
    prompt   = build_prompt(nature_result, news_data, live_data)
    ai_mode  = hw.get("ai_mode", "none")
    api_type = hw.get("api_type", "")

    print(f"\n  Getting prediction...")

    # Load all keys
    groq_key = gemini_key = claude_key = ""
    try:
        import importlib, config as cfg
        importlib.reload(cfg)
        groq_key   = getattr(cfg, "GROQ_KEY",      "")
        gemini_key = getattr(cfg, "GEMINI_KEY",    "")
        claude_key = getattr(cfg, "ANTHROPIC_KEY", "")
    except Exception:
        pass

    # 1. Groq — free, fastest
    if groq_key:
        print("  Using Groq (llama3-70b) — free & fast...")
        result = groq_predict(prompt, groq_key)
        if result:
            print("  Groq prediction complete!")
            return result
        print("  Groq failed — trying next...")

    # 2. Gemini — free tier
    if gemini_key:
        print("  Using Gemini (Google)...")
        result = gemini_predict(prompt, gemini_key)
        if result:
            return result
        print("  Gemini failed — trying next...")

    # 3. Claude — paid but accurate
    if claude_key:
        print("  Using Claude API...")
        result = claude_predict(prompt, claude_key)
        if result:
            return result
        print("  Claude failed — trying next...")

    # 4. Ollama — local
    if hw.get("ollama_ready") and hw.get("ollama_model"):
        model = hw["ollama_model"]
        print(f"  Using Ollama ({model}) — this takes 2-4 min on CPU...")
        result = ollama_predict(prompt, model)
        if result:
            return result
        print("  Ollama failed — using rule-based...")

    # 5. Rule-based — always works
    print("  Using rule-based prediction")
    print("  Tip: add GROQ_KEY to config.py for free AI predictions")
    return rule_based_predict(nature_result, news_data, live_data)


# ================================================================
# SAVE
# ================================================================
def save_prediction(prediction, nature_result):
    os.makedirs(f"{DATA_PATH}/predictions", exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc = {
        "generated_at":     datetime.now().isoformat(),
        "nature_score":     nature_result.get("score"),
        "nature_direction": nature_result.get("direction"),
        "engine_signals":   {k: v.get("signal") for k, v in nature_result.get("engines", {}).items()},
        "prediction":       prediction,
    }
    with open(f"{DATA_PATH}/predictions/pred_{ts}.json", "w") as f:
        json.dump(doc, f, indent=2)
    with open(f"{DATA_PATH}/predictions/latest.json", "w") as f:
        json.dump(doc, f, indent=2)
    return doc
