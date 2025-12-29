# -*- coding: utf-8 -*-
"""
Linux News Automated Fetcher
License: GPLv3
Version: 2.1
Author: Tuomas Lähteenmäki
Description: Automated AI-based Linux news reader with your key words.
"""

from google import genai
import os
import time
import configparser
from datetime import datetime

# --- CONSTANTS ---
CONFIG_FILE = "config.conf"
KEYWORDS_FILE = "keywords.txt"
REPORTS_DIR = "reports"

def setup_environment():
    """Initializes files and folders on the first run."""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'api_key': 'YOUR_API_KEY_HERE',
            'model_id': 'gemini-flash-latest'
        }
        # Let's add the prompt as its own section
        config['PROMPT'] = {
            'template': (
                "Search for the latest Linux and technology news regarding: {topics}. "
                "Write a concise summary in Finnish for each item and include the source URL. "
                "Focus on developer-centric updates like version numbers and new features."
            )
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"[*] Created {CONFIG_FILE}. Please add your API key and check the prompt template.")

    if not os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
            f.write("linux kernel development\ngcc compiler updates\nc23 standard news\n")

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config

def fetch_linux_news():
    setup_environment()

    config = load_config()
    settings = config['SETTINGS']
    prompt_template = config['PROMPT']['template']

    api_key = settings.get('api_key')
    model_id = settings.get('model_id')

    if api_key == 'YOUR_API_KEY_HERE':
        print("[!] Update the API key in the config.conf file!")
        return

    client = genai.Client(api_key=api_key)

    # Luetaan hakusanat
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        topics_list = [line.strip() for line in f if line.strip()]

    topics_string = ', '.join(topics_list)
    print(f"Searching for news on topics: {topics_string}...")

    # Yhdistetään hakusanat prompt-pohjaan
    final_prompt = prompt_template.replace("{topics}", topics_string)

    for attempt in range(3):
        try:
            response = client.models.generate_content(model=model_id, contents=final_prompt)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            filename = os.path.join(REPORTS_DIR, f"news_report_{timestamp}.txt")

            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"--- REPORT ---\nTime: {datetime.now()}\n\n")
                f.write(response.text)

            print(f"Succeeded! Saved: {filename}")
            return

        except Exception as e:
            if "429" in str(e):
                print("Quota full, please wait 30s...")
                time.sleep(30)
            else:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    fetch_linux_news()
