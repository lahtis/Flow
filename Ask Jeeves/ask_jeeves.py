# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler
File: ask_jeeves.py and jeeves_logic.py
Author: [Tuomas Lähteenmäki]
Version: v2.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Website:

Description: This software fetches news from RSS feeds, analyzes it with AI models (Gemini/Groq), and presents it in a localized manner.
Notes:
- Localization: Finnish (fi) and English (en).
"""

import feedparser
import configparser
import sys
import time
from google import genai
from jeeves_logic import JeevesMemory, check_environment, CONFIG_FILE
from jeeves_logic import get_config_value, get_localized_text

class JeevesFetcher:
    def __init__(self):
        if not check_environment():
            sys.exit()

        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding='utf-8')

        self.lang = self.config['SETTINGS'].get('language', 'en').lower()
        self.memory = JeevesMemory()

        self.api_key = self.config['SETTINGS'].get('api_key')
        self.model = get_config_value("gemini_model", self.lang) or \
                     self.config['MODELS'].get('gemini', 'gemini-2.0-flash')

        self.pending_msg = get_localized_text("pending", self.lang) or "Waiting for analysis."
        self.ai_instruction = get_localized_text("ai_instruction", self.lang)

        self.client = genai.Client(api_key=self.api_key)

    def run(self):
        self.fetch_all_feeds()
        # Haetaan "analysis_start" ja varmistetaan siisti tuloste
        start_msg = get_localized_text("analysis_start", self.lang) or "Starting analysis..."
        # Siivotaan mahdolliset kovakoodatut merkit metadatasta varmuuden vuoksi
        start_msg = start_msg.replace("[*] Jeeves: ", "").strip()
        print(f"\n[*] Jeeves: {start_msg}")

        self.process_pending_summaries()

    def fetch_all_feeds(self):
        if 'FEEDS' not in self.config:
            return

        fetch_label = get_localized_text("fetching_news", self.lang) or "Fetching news"
        fetch_label = fetch_label.replace("[*] Jeeves: ", "").strip()

        added_label = get_localized_text("added_news", self.lang) or "Added {} items."
        added_label = added_label.replace("[+] Jeeves: ", "").strip()

        for feed_name, url in self.config['FEEDS'].items():
            if not url: continue

            category_label = "Security" if "security" in feed_name.lower() else "Linux"
            display_name = feed_name.replace('_', ' ').title()

            print(f"[*] Jeeves: {fetch_label} ({display_name})...")

            try:
                feed = feedparser.parse(url)
                added = 0
                for entry in feed.entries[:3]:
                    if not any(e['url'] == entry.link for e in self.memory.data['archive']):
                        self.memory.add_entry(entry.title, self.pending_msg, entry.link, category_label)
                        added += 1

                if added > 0:
                    print(f"[+] Jeeves: {added_label.format(added)}")
            except Exception as e:
                print(f"[!] Jeeves: Error fetching {display_name}: {e}")

    def process_pending_summaries(self):
        pending_fi = get_localized_text("pending", "fi")
        pending_en = get_localized_text("pending", "en")

        to_analyze = [e for e in self.memory.data['archive']
                      if e['summary'] in [pending_fi, pending_en]]

        if not to_analyze:
            no_work = get_localized_text("no_pending_work", self.lang) or "No pending work."
            no_work = no_work.replace("[*] Jeeves: ", "").strip()
            print(f"[*] Jeeves: {no_work}")
            # Vaikka uutta analysoitavaa ei ole, tarkistetaan silti vanha arkisto rotaation varalta
            self._handle_archive_rotation()
            return

        analyzing_txt = get_localized_text("analyzing_msg", self.lang) or "Analyzing"
        quota_err_txt = get_localized_text("quota_error", self.lang) or "Quota full."
        quota_err_txt = quota_err_txt.replace("[!] Jeeves: ", "").strip()

        done_txt = get_localized_text("analysis_done", self.lang) or "Done."

        for entry in to_analyze:
            print(f"[*] Jeeves: {analyzing_txt}: {entry['title']}...")
            summary = self.summarize_with_ai(entry['title'], entry['url'])

            if "RESOURCE_EXHAUSTED" in summary or "429" in summary:
                print(f"[!] Jeeves: {quota_err_txt}")
                try:
                    from jeeves_mirror import JeevesMirror
                    mirror = JeevesMirror()
                    if mirror.api_key:
                        mirror_act_msg = get_localized_text("activating_mirror", self.lang) or "Activating Mirror..."
                        mirror_act_msg = mirror_act_msg.replace("[*] Jeeves: ", "").strip()
                        print(f"[*] Jeeves: {mirror_act_msg}")

                        summary = mirror.ask_groq(entry['title'], entry['url'])
                        if not summary: break
                    else:
                        break
                except Exception as mirror_err:
                    print(f"[!] Jeeves: Mirror failed: {mirror_err}")
                    break

            entry['summary'] = summary
            self.memory._save_data()
            print(f"[+] Jeeves: {done_txt}")

            if "429" not in str(summary):
                time.sleep(15)
            else:
                time.sleep(1)

        work_finished = get_localized_text("work_finished", self.lang) or "Work complete."
        print(f"\n[*] Jeeves: {work_finished}")

        # --- ARKISTON ROTAATIO ---
        self._handle_archive_rotation()

    def _handle_archive_rotation(self):
        """Apumetodi arkiston hallintaan, sir."""
        try:
            # Pidetään aktiivisessa muistissa 14 päivää
            count, arch_path = self.memory.rotate_archive(days_to_keep=14)
            if count > 0:
                import os
                arch_name = os.path.basename(arch_path)
                print(f"[*] Jeeves: Siirretty {count} vanhaa uutista arkistoon: {arch_name}")
        except Exception as e:
            print(f"[!] Jeeves: Arkistoinnissa ilmeni viiveitä: {e}")

    def summarize_with_ai(self, title, url):
        p_title = get_localized_text("prompt_title", self.lang) or "News"
        p_source = get_localized_text("prompt_source", self.lang) or "Source"

        prompt = (
            f"{self.ai_instruction}\n\n"
            f"{p_title}: {title}\n"
            f"{p_source}: {url}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    fetcher = JeevesFetcher()
    fetcher.run()
