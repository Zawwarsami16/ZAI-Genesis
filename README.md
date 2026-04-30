# ZAI Genesis

Market-cycle and natural-pattern research terminal.

ZAI Genesis is a Python-based research system for exploring market behavior through historical cycles, technical structures, sentiment conditions, and nature-inspired pattern models.

Built by Anteroom Studio as part of its research systems and intelligence tooling.

---

## Overview

Most market tools focus on price charts or headline streams. ZAI Genesis is designed to study a wider set of market-cycle signals: Fibonacci levels, Elliott-wave structure, long-cycle economic phases, solar-cycle context, lunar timing, seasonality, volatility psychology, and live market conditions.

It helps explore questions such as:

- Which market-cycle signals are currently aligned?
- How strong is the current agreement across independent models?
- What time horizons appear most consistent with the current setup?
- Which conditions should researchers monitor next?
- How do technical, seasonal, and sentiment patterns compare?

This is a research tool, not a trading signal service.

---

## Core Capabilities

- Live market data collection
- Fibonacci-level analysis
- Elliott-wave structure checks
- Long-cycle market phase modeling
- Solar-cycle and lunar-cycle context
- Seasonal tendency analysis
- Volatility and fear/greed interpretation
- Nature Agreement Score calculation
- Local or API-assisted summary generation
- Terminal dashboard rendering
- Local storage for downloaded data and snapshots

---

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local environment settings:

```bash
cp .env.example .env
```

Optional keys can be added to `.env`:

```txt
GROQ_KEY=
GEMINI_KEY=
ANTHROPIC_KEY=
DATA_PATH=./genesis_data
```

Run the terminal:

```bash
python3 zai_genesis.py
```

The launcher filename is retained for continuity. It can be renamed after repository migration.

---

## AI Modes

The system can run without external API keys using rule-based logic. Optional keys or local models can be added later for richer summaries.

| Setup | Mode | Notes |
|---|---|---|
| No keys | Rule-based logic | Default fallback |
| Ollama available | Local model | Runs locally where supported |
| API key configured | Hosted model | Uses available provider settings |

---

## System Architecture

```txt
ZAI Genesis
├── zai_genesis.py       Main CLI entry point
├── config.py            Runtime settings and environment loading
├── hardware_detector.py Hardware and local-model detection
├── data_collector.py    Market and historical data collection
├── nature_engine.py     Cycle and pattern engines
├── genesis_brain.py     Rule/model-assisted research summary
├── dashboard.py         Terminal dashboard renderer
└── .env.example         Safe local configuration template
```

---

## Safety and Scope

ZAI Genesis is intended for research, education, and internal experimentation. Its outputs may be incomplete, stale, or incorrect depending on data-source availability, model behavior, API limits, and market conditions.

This project does not provide financial, investment, legal, or professional advice. Always verify outputs independently before using them in any real-world decision.

---

## Studio

Anteroom Studio  
Research systems, intelligence interfaces, and experimental software.

Research and implementation by ZAI (Zawwar Sami).
