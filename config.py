# ================================================================
# ZAI GENESIS — CONFIG
# by Zawwar (github.com/Zawwarsami16)
#
# This is the ONLY file you ever need to touch.
# Everything else is automatic.
#
# CURRENT SETUP: Add your Groq key below and run zai_genesis.py
# FUTURE: Add any other key — system auto-upgrades itself
# ================================================================

# ----------------------------------------------------------------
# AI KEYS — add whichever you have, system picks best automatically
# Priority: Groq → Gemini → Claude → Ollama → Rule-based
# ----------------------------------------------------------------

# Groq — groq.com (FREE, fastest, llama3-70b)
GROQ_KEY = ""  # paste your key here: gsk_...

# Google Gemini — aistudio.google.com/app/api-keys (free tier)
GEMINI_KEY = ""

# Anthropic Claude — console.anthropic.com (~$5 credit)
ANTHROPIC_KEY = ""

# ----------------------------------------------------------------
# DATA STORAGE
# I keep mine on a 1TB portable SSD — change path if needed
# Windows: "D:/ZAI_Genesis"    Linux: "/mnt/ssd/ZAI_Genesis"
# ----------------------------------------------------------------
DATA_PATH = "./genesis_data"

# ----------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------

# Dashboard refresh speed in seconds
UPDATE_INTERVAL = 60

# Minimum Nature Agreement Score to show confident prediction
MIN_AGREEMENT = 50

# Local LLM via Ollama (auto-detected, no need to change)
USE_LOCAL_LLM   = True
LOCAL_LLM_MODEL = "phi3:mini"  # auto-overridden based on your GPU
