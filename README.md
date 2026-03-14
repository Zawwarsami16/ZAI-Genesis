# ZAI GENESIS 🌌
### Laws of Everything · Market Prediction AI

**by Zawwar · [github.com/Zawwarsami16](https://github.com/Zawwarsami16)**

---

## What Is This?

Most market tools look at price charts. Genesis looks at natural laws.

The idea: markets don't move randomly — they follow the same mathematical patterns found in nature. Fibonacci sequences, 11-year sunspot cycles, lunar rhythms, Elliott waves, 50-year economic supercycles. When multiple natural laws point in the same direction, that's a signal worth listening to.

Genesis reads all of them simultaneously and gives you a **Nature Agreement Score** — how many natural laws agree right now.

---

## How It Works

```
Hardware auto-detected → AI mode selected (Ollama / Claude API / Rule-based)
              ↓
Data collected: markets (1871–today) + sunspots (1749–today) + lunar cycles + live prices + 435 news feeds
              ↓
7 Nature Engines run in parallel:
  Fibonacci levels · Elliott Wave position · Kondratiev supercycle
  Sunspot cycle · Lunar phase · Seasonal patterns · Fear/Greed psychology
              ↓
Nature Agreement Score: how many laws agree on direction
              ↓
AI Prediction: 4-week, 3-month, 6-month outlook
              ↓
Live Dashboard: dark terminal, 60s refresh, 24/7
```

---

## One Command

```bash
python3 zai_genesis.py
```

That's it. It detects your hardware, installs what's missing, downloads data on first run, and launches.

---

## AI Modes — Auto-Selected

| Setup | AI Mode | Cost |
|-------|---------|------|
| Nothing extra | Rule-based logic | FREE |
| Ollama + phi3:mini | Local LLM (CPU) | FREE |
| Ollama + llama3:8b | Local LLM (GPU) | FREE |
| API key in config.py | Claude API | ~$0.01/prediction |

**Right now:** works without any API or GPU. Add either later and it upgrades automatically.

---

## Install Ollama (when you have a good machine)

```bash
# Linux / Kali
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini        # CPU — 2GB
# or
ollama pull llama3:8b        # GPU 8GB+
```

Set in `config.py`:
```python
USE_LOCAL_LLM    = True
# model auto-detected based on your hardware
```

---

## The 7 Nature Engines

| Engine | What It Reads | Key Law |
|--------|--------------|---------|
| Fibonacci | Price position vs. golden ratio levels | 61.8% = golden ratio support/resistance |
| Elliott Wave | Wave cycle position (1-5, A-C) | Markets move in 5+3 wave patterns |
| Kondratiev | 50-60 year economic supercycle phase | Current: New Spring (2020-2033) |
| Sunspot | 11-year solar activity cycle | Solar max historically precedes volatility |
| Lunar | Moon phase (new/full cycle) | Full moon → slightly elevated risk aversion |
| Seasonal | Month/quarter historical bias | September worst, April best, Q4 strongest |
| Psychology | VIX fear/greed reading | VIX >40 = extreme fear = buy signal |

---

## Files

| File | Purpose |
|------|---------|
| `config.py` | Settings — only file you edit |
| `zai_genesis.py` | Main launcher — run this |
| `hardware_detector.py` | Scans machine, picks best AI mode |
| `data_collector.py` | Downloads all data + live updates |
| `nature_engine.py` | All 7 nature engines |
| `genesis_brain.py` | AI prediction (Ollama/API/rule-based) |
| `dashboard.py` | Live 24/7 terminal display |

---

*Research tool. Not financial advice.*
