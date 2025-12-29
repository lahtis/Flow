# -*- coding: utf-8 -*-
"""
Gemini Bridge: Multi-File Analyzer
Version: 1.2
License: GPLv3
Description: Professional AI bridge for source code analysis with Windows path support.
"""

import os
import time
import configparser
from google import genai

# --- CONSTANTS ---
CONFIG_FILE = "gbridge_config.conf"
REPORTS_DIR = "analysis_reports"

def setup_bridge():
    """Initializes the configuration and reports directory if missing."""
    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'api_key': 'YOUR_API_KEY_HERE',
            'model_id': 'gemini-flash-latest',
            'attempts': '3'
        }
        config['PROMPT'] = {
            'template': "You are an experienced developer. Analyze this file and suggest 3 concrete improvements: {code}"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"[*] Generated {CONFIG_FILE}. Please add your API key.")

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        print(f"[*] Created directory: {REPORTS_DIR}")

def run_bridge():
    setup_bridge()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')

    settings = config['SETTINGS']
    api_key = settings.get('api_key')
    model_id = settings.get('model_id')
    attempts = int(settings.get('attempts', 3))
    prompt_template = config['PROMPT'].get('template')

    if api_key == 'YOUR_API_KEY_HERE':
        print("[!] Error: API key not set in gbridge_config.conf")
        return

    print("\n--- GEMINI BRIDGE: ANALYZER ---")
    # Clean spaces and quotes from the input path (Windows support)
    input_path = input("Enter filename to analyze: ").strip().strip('"' + "'")

    if not os.path.exists(input_path):
        print(f"[!] Error: File not found: {input_path}")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        print(f"[!] Read error: {e}")
        return

    client = genai.Client(api_key=api_key)
    final_prompt = prompt_template.replace("{code}", source_code)
    print(f"[*] Analyzing: {input_path} using {model_id}...")

    for i in range(attempts):
        try:
            response = client.models.generate_content(model=model_id, contents=final_prompt)
            print("\n--- ANALYSIS SUCCESSFUL ---")

            # Extract only the filename (basename) for the report to avoid path errors
            file_only = os.path.basename(input_path)
            ts = time.strftime("%Y%m%d_%H%M")
            report_name = f"analysis_{file_only}_{ts}.txt"
            report_path = os.path.join(REPORTS_DIR, report_name)

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"FILE: {input_path}\nDATE: {time.ctime()}\n")
                f.write("="*40 + "\n\n")
                f.write(response.text)

            print(f"[+] Report saved to: {report_path}\n")
            print(response.text)
            return

        except Exception as e:
            if "429" in str(e):
                print(f"Quota exhausted, retrying {i+1}/{attempts} in 30s...")
                time.sleep(30)
            else:
                print(f"Error during attempt {i+1}: {e}")
                time.sleep(2)

if __name__ == "__main__":
    run_bridge()
if __name__ == "__main__":
    run_bridge()
