# -*- coding: utf-8 -*-
"""
mmAnalyzer - Multi-Mode Gemini Bridge Analyzer
Version: 1.3.1
Author: Tuomas Lähteenmäki
Lisence: GPLv3
Description: Hybrid analyzer (File/Clipboard/Static) with Latin-1 fallback support.
"""

import os
import time
import configparser
import pyperclip
from google import genai

# --- CONSTANTS ---
CONFIG_FILE = "mmAnalyzer_config.conf"
REPORTS_DIR = "analysis_reports"
DEFAULT_INPUT = "input_code.txt"

def setup_bridge():
    """Initializes config, reports directory and default input file."""
    # 1. Luo konfiguraatiotiedosto
    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'api_key': 'YOUR_API_KEY_HERE',
            'model_id': 'gemini-flash-latest',
            'attempts': '3'
        }
        config['PROMPT'] = {
            'template': "Analyze this code and give 3 improvements:\n\n{code}"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"[*] Created {CONFIG_FILE}")

    # 2. Luo raporttikansio
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    # 3. LUO OLETUSSYÖTETIEDOSTO (Tämä puuttui)
    if not os.path.exists(DEFAULT_INPUT):
        with open(DEFAULT_INPUT, "w", encoding="utf-8") as f:
            f.write("// Put the code to be analyzed in this file.\n")
            f.write("// Or copy it to the clipboard and press Enter in the program.\n")
        print(f"[*] Created {DEFAULT_INPUT} for static code input.")

def read_source(path):
    """Reads file with UTF-8 support and Latin-1 fallback for Finnish characters."""
    try:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), "UTF-8"
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                return f.read(), "Latin-1"
    except Exception as e:
        return None, str(e)

def run_bridge():
    setup_bridge()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')

    api_key = config['SETTINGS'].get('api_key')
    if api_key == 'YOUR_API_KEY_HERE':
        print("[!] Set API key in mmAnalyzer_config.conf")
        return

    print("\n--- Multi-Mode Gemini Bridge Analyzer 1.3.1 ---")
    print(f"Modes: Enter path | Empty Enter for Clipboard | Uses {DEFAULT_INPUT} as fallback")
    user_input = input("Target: ").strip().strip('"' + "'")

    source_code = ""
    origin_name = ""

    # 1. FILE MODE
    if user_input and os.path.exists(user_input):
        source_code, enc = read_source(user_input)
        origin_name = os.path.basename(user_input)
        print(f"[*] Loaded file: {origin_name} ({enc})")

    # 2. CLIPBOARD MODE
    elif not user_input:
        source_code = pyperclip.paste().strip()
        if source_code:
            origin_name = "clipboard_content"
            print("[*] Loaded content from Clipboard")

        # 3. STATIC FILE FALLBACK
        elif os.path.exists(DEFAULT_INPUT):
            source_code, enc = read_source(DEFAULT_INPUT)
            origin_name = DEFAULT_INPUT
            print(f"[*] Loaded fallback file: {DEFAULT_INPUT}")

    if not source_code:
        print("[!] No source code found from any source.")
        return

    # ANALYSIS LOGIC
    client = genai.Client(api_key=api_key)
    prompt = config['PROMPT'].get('template').replace("{code}", source_code)

    print(f"[*] Analyzing {origin_name}...")
    try:
        response = client.models.generate_content(model=config['SETTINGS'].get('model_id'), contents=prompt)

        # Save Report
        ts = time.strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(REPORTS_DIR, f"report_{origin_name}_{ts}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"SOURCE: {origin_name}\nDATE: {time.ctime()}\n\n{response.text}")

        print("\n" + "="*30 + "\n" + response.text + "\n" + "="*30)
        print(f"[+] Saved to: {report_path}")
    except Exception as e:
        print(f"[!] API Error: {e}")

if __name__ == "__main__":
    run_bridge()
