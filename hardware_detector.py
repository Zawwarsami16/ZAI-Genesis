"""
ZAI Genesis — Hardware Detector
by Zawwar (github.com/Zawwarsami16)

Runs first on every startup.
Scans the machine and picks the best available AI mode.
Priority: Groq → Gemini → Claude → Ollama → Rule-based

No setup needed — just run zai_genesis.py and it figures it out.
Future: add any key to config.py and it auto-upgrades.
"""

import os
import sys
import platform
import subprocess


def detect():
    hw = {
        "os":              platform.system(),
        "cpu_cores":       os.cpu_count() or 1,
        "ram_gb":          0,
        "disk_free_gb":    0,
        "gpu":             None,
        "gpu_vram_gb":     0,
        "gpu_type":        "none",
        "ollama_ready":    False,
        "ollama_model":    None,
        "api_key_present": False,
        "api_type":        None,
        "ai_mode":         "none",
        "recommended_llm": "phi3:mini",
    }

    # --- RAM + Disk ---
    try:
        import psutil
        hw["ram_gb"]       = round(psutil.virtual_memory().total / (1024**3), 1)
        hw["disk_free_gb"] = round(psutil.disk_usage("/").free  / (1024**3), 1)
    except Exception:
        try:
            if hw["os"] == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if "MemTotal" in line:
                            hw["ram_gb"] = round(int(line.split()[1]) / (1024**2), 1)
                            break
        except Exception:
            hw["ram_gb"] = 8

    # --- GPU: NVIDIA ---
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=8
        )
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split("\n")[0].split(",")
            hw["gpu"]         = parts[0].strip()
            hw["gpu_vram_gb"] = round(int(parts[1].strip()) / 1024, 1)
            hw["gpu_type"]    = "nvidia"
    except Exception:
        pass

    # --- GPU: AMD ---
    if not hw["gpu"]:
        try:
            r = subprocess.run(["rocminfo"], capture_output=True, text=True, timeout=8)
            if r.returncode == 0 and "GPU" in r.stdout:
                hw["gpu_type"] = "amd"
                hw["gpu"]      = "AMD GPU (ROCm)"
        except Exception:
            pass

    # --- GPU: Apple Silicon ---
    if not hw["gpu"] and hw["os"] == "Darwin":
        try:
            r = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                               capture_output=True, text=True)
            if "Apple" in r.stdout:
                hw["gpu_type"]    = "apple"
                hw["gpu"]         = r.stdout.strip()
                hw["gpu_vram_gb"] = hw["ram_gb"] * 0.75
        except Exception:
            pass

    # --- Best local model based on hardware ---
    vram = hw["gpu_vram_gb"]
    if hw["gpu_type"] == "nvidia":
        if   vram >= 24: hw["recommended_llm"] = "llama3:70b"
        elif vram >= 12: hw["recommended_llm"] = "llama3:13b"
        elif vram >= 8:  hw["recommended_llm"] = "llama3:8b"
        elif vram >= 4:  hw["recommended_llm"] = "mistral:7b"
        else:            hw["recommended_llm"] = "phi3:mini"
    elif hw["gpu_type"] in ("apple", "amd"):
        hw["recommended_llm"] = "llama3:8b" if hw["ram_gb"] >= 16 else "phi3:mini"

    # --- Check Ollama ---
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            hw["ollama_ready"] = True
            lines = r.stdout.strip().split("\n")
            for line in lines[1:]:
                if line.strip():
                    hw["ollama_model"] = line.split()[0]
                    break
    except Exception:
        pass

    # --- Check API keys (priority order) ---
    key_checks = [
        ("GROQ_KEY",      "groq"),
        ("GEMINI_KEY",    "gemini"),
        ("ANTHROPIC_KEY", "claude"),
    ]
    for key_name, key_type in key_checks:
        try:
            import importlib, config as cfg
            importlib.reload(cfg)
            val = getattr(cfg, key_name, "")
            if val and val not in ("", f"YOUR_{key_name}_HERE"):
                hw["api_key_present"] = True
                hw["api_type"]        = key_type
                break  # use first available key
        except Exception:
            pass

    # --- Pick AI mode ---
    # API always beats local Ollama (faster)
    if hw["api_key_present"]:
        hw["ai_mode"] = "api"
    elif hw["ollama_ready"] and hw["ollama_model"]:
        hw["ai_mode"] = "ollama"
    else:
        hw["ai_mode"] = "none"

    return hw


def print_report(hw):
    mode_labels = {
        "api":    f"API ({hw.get('api_type','?').upper()}) — online",
        "ollama": f"LOCAL ({hw.get('ollama_model','?')}) — free offline",
        "none":   "RULE-BASED — no AI (add key to config.py)",
    }
    lines = [
        "",
        "  HARDWARE SCAN",
        "  " + "─"*40,
        f"  OS          {hw['os']}",
        f"  CPU cores   {hw['cpu_cores']}",
        f"  RAM         {hw['ram_gb']} GB",
        f"  Disk free   {hw['disk_free_gb']} GB",
        f"  GPU         {hw['gpu'] or 'none detected'}",
        "  " + "─"*40,
        f"  AI mode     {mode_labels.get(hw['ai_mode'], 'unknown')}",
        "",
    ]
    if hw["ai_mode"] == "none":
        lines += [
            "  To enable AI predictions:",
            "    Groq (free):  groq.com → get key → GROQ_KEY in config.py",
            "    Ollama (free): curl -fsSL https://ollama.com/install.sh | sh",
            f"                  ollama pull {hw['recommended_llm']}",
            "",
        ]
    print("\n".join(lines))


if __name__ == "__main__":
    hw = detect()
    print_report(hw)
