# -*- coding: utf-8 -*-
"""
Clipboard Analyzer for CodeBlocks
Version: 1.0
Author: Tuomas Lähteenmäki
Lisence: GPLv3
Description: Analyzes code from clipboard and saves reports to a dedicated folder.
"""

import os
import time
import configparser
import pyperclip
from google import genai

# --- CONSTANTS ---
CONFIG_FILE = "clipboard_config.conf"
REPORTS_DIR = "clipboard_reports"

def setup_analyzer():
    """Initializes config and reports directory."""
    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'api_key': 'YOUR_API_KEY_HERE',
            'model_id': 'gemini-flash-latest',
            'attempts': '3'
        }
        config['PROMPT'] = {
            'template': "You are an experienced C/C++ developer. Analyze this code snippet from CodeBlocks and suggest 3 improvements: {code}"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"[*] Created {CONFIG_FILE}. Please add your API key.")

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def run_analysis():
    setup_analyzer()
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    
    api_key = config['SETTINGS'].get('api_key')
    model_id = config['SETTINGS'].get('model_id')
    attempts = int(config['SETTINGS'].get('attempts', 3))
    prompt_template = config['PROMPT'].get('template')

    if api_key == 'YOUR_API_KEY_HERE':
        print("[!] Update your API key in clipboard_config.conf!")
        return

    # Get code from clipboard
    code_snippet = pyperclip.paste()
    if not code_snippet.strip():
        print("[!] Clipboard is empty! Copy some code from CodeBlocks first.")
        return

    print(f"[*] Analyzing clipboard content (Length: {len(code_snippet)} characters)...")

    client = genai.Client(api_key=api_key)
    final_prompt = prompt_template.replace("{code}", code_snippet)

    for i in range(attempts):
        try:
            response = client.models.generate_content(model=model_id, contents=final_prompt)
            
            # Create a unique filename for the report
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_name = f"clipboard_analysis_{timestamp}.txt"
            report_path = os.path.join(REPORTS_DIR, report_name)
            
            # Save the report
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("CLIPBOARD ANALYSIS REPORT\n")
                f.write(f"DATE: {time.ctime()}\n")
                f.write("="*40 + "\n\n")
                f.write(response.text)
            
            print("\n--- ANALYSIS SUCCESSFUL ---")
            print(response.text)
            print(f"\n[+] Saved to: {report_path}")
            return

        except Exception as e:
            if "429" in str(e):
                print(f"Quota full, retrying {i+1}/{attempts} in 30s...")
                time.sleep(30)
            else:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    run_analysis()
