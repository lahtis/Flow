# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler
File: jeeves_mirror.py
Author: [Tuomas Lähteenmäki]
Version: v2.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Website:

Description: This software fetches news from RSS feeds, analyzes it with AI models (Gemini/Groq), and presents it in a localized manner.
Notes:
- Localization: Finnish (fi) and English (en).
"""

import json
import os
import time
import configparser
from groq import Groq
from jeeves_logic import JeevesMemory, CONFIG_FILE, get_localized_text

class JeevesMirror:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding='utf-8')

        # Haetaan kieli
        self.lang = self.config['SETTINGS'].get('language', 'fi').lower()

        # Haetaan API-avain
        self.api_key = self.config['API_KEYS'].get('groq') if 'API_KEYS' in self.config else None

        # Haetaan malli
        self.model = "llama-3.3-70b-versatile"
        if 'MODELS' in self.config:
            self.model = self.config['MODELS'].get('groq', self.model)

        if not self.api_key:
            print(get_localized_text("error_no_api", self.lang) or "[!] Groq API-key missing.")
            return

        try:
            self.client = Groq(api_key=self.api_key)
            self.memory = JeevesMemory()
        except Exception as e:
            print(f"[!] Alustusvirhe: {e}")
            self.api_key = None

    def process_queue(self):
        # Tunnistetaan uutiset molemmilla kielillä (varmistetaan ristiinyhteensopivuus)
        pending_fi = get_localized_text("pending", "fi")
        pending_en = get_localized_text("pending", "en")

        pending = [e for e in self.memory.data['archive']
                  if e['summary'] in [pending_fi, pending_en]]

        if not pending:
            msg = get_localized_text("no_pending_work", self.lang) or "No news to analyze."
            print(f"[*] Jeeves: {msg}")
            return

        print(f"[*] Jeeves Mirror: {self.model} ({self.lang})")

        analyzing_txt = get_localized_text("analyzing_msg", self.lang) or "Analyzing"
        # Haetaan dynaaminen kuittaus (esim. "Analyysi valmis." tai "Analysis complete.")
        done_txt = get_localized_text("analysis_done", self.lang) or "Done."

        for entry in pending:
            print(f"[*] {analyzing_txt}: {entry['title']}...")
            summary = self.ask_groq(entry['title'], entry['url'])

            if summary:
                entry['summary'] = summary
                self.memory._save_data()
                # Tulostetaan lokalisoitu kuittaus
                print(f"[+] {done_txt}")
                time.sleep(1)
            else:
                # Jos ask_groq palauttaa None (virhe), keskeytetään
                break

    def ask_groq(self, title, url):
        # Haetaan AI-ohjeistus ja otsikot metadatasta
        base_instruction = get_localized_text("ai_instruction", self.lang)
        p_title = get_localized_text("prompt_title", self.lang) or "News"
        p_source = get_localized_text("prompt_source", self.lang) or "Source"

        # Rakennetaan dynaaminen prompt
        prompt = (
            f"{base_instruction}\n\n"
            f"{p_title}: {title}\n"
            f"{p_source}: {url}"
        )

        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a polite and professional butler named Jeeves."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, # Laskettu hieman tarkkuuden vuoksi
                max_tokens=500
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[!] Groq-virhe: {e}")
            return None

if __name__ == "__main__":
    mirror = JeevesMirror()
    if hasattr(mirror, 'api_key') and mirror.api_key:
        mirror.process_queue()
        final_msg = get_localized_text("work_finished", mirror.lang)
        print(f"\n[*] Jeeves Mirror: {final_msg}")
