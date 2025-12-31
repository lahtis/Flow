# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler
File: ask_jeeves.py and jeeves_logic.py
Author: [Tuomas Lähteenmäki]
Version: 3.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Source: https://github.com/lahtis/Flow/tree/main/Ask%20Jeeves

Description: This software fetches news from RSS feeds, analyzes it with AI models (Gemini/Groq), and presents it in a localized manner.
Notes:
- Localization: Finnish (fi) and English (en).
"""

import sys, io
import time
import feedparser
import configparser
from google import genai
from jeeves_logic import JeevesMemory, check_environment, CONFIG_FILE
from jeeves_logic import get_config_value, get_localized_text
from jeeves_archive import JeevesArchive

# Pakotetaan standarditulosteet UTF-8 muotoon
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

        from jeeves_archive import JeevesArchive
        archive_manager = JeevesArchive()

        fetch_label = get_localized_text("ui.fetching_news", self.lang) or "Fetching news"
        fetch_label = fetch_label.replace("[*] Jeeves: ", "").strip()

        added_label = get_localized_text("added_news", self.lang) or "Added {} items."
        added_label = added_label.replace("[+] Jeeves: ", "").strip()

        # --- TÄSSÄ ON KORJAUS: MUISTILISTA DUPLIKAATEILLE ---
        seen_titles = set()

        for feed_name, url in self.config['FEEDS'].items():
            if not url: continue

            category_label = "Security" if "security" in feed_name.lower() else "Linux"
            display_name = feed_name.replace('_', ' ').title()

            print(f"[*] Jeeves: {fetch_label} ({display_name})...")

            try:
                feed = feedparser.parse(url)
                added = 0
                for entry in feed.entries[:5]: # Tarkistetaan 5 uusinta
                    # 1. ESTETÄÄN SAMAN AJON DUPLIKAATIT (esim. useat TF2 päivitykset)
                    if entry.title in seen_titles:
                        continue
                    seen_titles.add(entry.title)

                    # 2. Tarkistetaan onko uutinen jo muistissa (memory.json)
                    already_in_memory = any(e['url'] == entry.link for e in self.memory.data['archive'])

                    # 3. Tarkistetaan onko uutinen jo arkistossa (news_archive.jsonl)
                    already_in_archive = archive_manager.is_already_archived(entry.link)

                    if not already_in_memory and not already_in_archive:
                        self.memory.add_entry(entry.title, self.pending_msg, entry.link, category_label)
                        added += 1

                if added > 0:
                    print(f"[+] Jeeves: {added_label.format(added)}")

            except Exception as e:
                print(f"[!] Jeeves: Error fetching {display_name}: {e}")

    def sync_from_metadata(self, metadata_path):
        """Kopioi kaikki valmiit uutiset metadatasta arkistoon, jos ne puuttuvat sieltä."""
        if not os.path.exists(metadata_path):
            return 0

        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        added = 0
        # Oletetaan että uutiset ovat 'archive'-listassa metadatassa
        for entry in data.get('archive', []):
            url = entry.get('url')
            # Jos uutisella on kunnon summary eikä se ole jo arkistossa
            if url and not self.is_already_archived(url):
                if len(entry.get('summary', '')) > 50: # Varmistetaan että on oikea sisältö
                    self.save_to_archive(entry)
                    added += 1
        return added

    def process_pending_summaries(self):
        from jeeves_archive import JeevesArchive
        archive_manager = JeevesArchive()

        pending_fi = get_localized_text("pending", "fi")
        pending_en = get_localized_text("pending", "en")

        to_analyze = [e for e in self.memory.data['archive']
                      if e['summary'] in [pending_fi, pending_en]]

        if not to_analyze:
            no_work = get_localized_text("ui.no_pending_work", self.lang)
            no_work = no_work.replace("[*] Jeeves: ", "").strip()
            print(f"[*] Jeeves: {no_work}")
            self._handle_archive_rotation()
            return

        analyzing_txt = get_localized_text("analyzing_msg", self.lang) or "Analyzing"
        quota_err_txt = get_localized_text("quota_error", self.lang) or "Quota full."
        quota_err_txt = quota_err_txt.replace("[!] Jeeves: ", "").strip()
        done_txt = get_localized_text("analysis_done", self.lang) or "Done."

        for entry in to_analyze:
            print(f"[*] Jeeves: {analyzing_txt}: {entry['title']}...")
            summary = self.summarize_with_ai(entry['title'], entry['url'])

            # Virheenkäsittely ja Groq-peiliin vaihtaminen
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

            # Päivitetään aktiivinen muisti
            entry['summary'] = summary
            self.memory._save_data()

            # --- UUSI: TALLENNUS PYSYVÄÄN ARKISTOON ---
            # Tallennetaan vain, jos vastaus ei ole virheilmoitus
            if summary and "429" not in str(summary) and "RESOURCE_EXHAUSTED" not in str(summary):
                archive_manager.save_to_archive(entry)

                # Haetaan lokalisoitu teksti
                archive_label = get_localized_text("ui.analysis_archived", self.lang) or "Analysis archived successfully."
                print(f"[+] Jeeves: {archive_label}")

            print(f"[+] Jeeves: {done_txt}")

            # Kohtelias odotus AI-kutsujen välillä
            if "429" not in str(summary):
                time.sleep(15)
            else:
                time.sleep(1)

        work_finished = get_localized_text("ui.work_finished", self.lang)
        print(f"\n[*] Jeeves: {work_finished}")

        # Lopuksi ajetaan vanha rotaatio, jos tarpeen
        self._handle_archive_rotation()

    def _handle_archive_rotation(self):
        """Apumetodi arkiston hallintaan, sir."""
        try:
            # Pidetään aktiivisessa muistissa 14 päivää
            count, arch_path = self.memory.rotate_archive(days_to_keep=14)
            if count > 0:
                import os
                arch_name = os.path.basename(arch_path)
                # Haetaan lokalisoitu teksti
                rot_msg = get_localized_text("ui.archive_rotation", self.lang) or "Moved {} items to archive: {}"
                print(f"[*] Jeeves: {rot_msg.format(count, arch_name)}")

        except Exception as e:
            err_msg = get_localized_text("ui.archive_error", self.lang) or "Delays in archiving: {}"
            print(f"[!] Jeeves: {err_msg.format(e)}") # Tämä rivi oli liian syvällä


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
