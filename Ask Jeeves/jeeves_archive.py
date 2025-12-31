# -*- coding: utf-8 -*-

"""
Jeeves - Personal News Butler & Archiver
File: jeeves_archive.py
Author: Tuomas Lähteenmäki
Version: v2.2.0 (Arkistointiversio)
Licence: GNU GPLv3

Description:
    Fetches, analyzes, and archives news using AI (Gemini/Groq).
    Uses JSONL (JSON Lines) for persistent storage to ensure
    efficient data appending and resilience.

Key Features:
    - Persistent 'Memory': Prevents re-analyzing old news.
    - Localization: Finnish and English support via personality.json.
    - GUI: CustomTkinter with dynamic butler reactions and avatar.

Dependencies:
    - customtkinter, Pillow, requests, google-generativeai, groq
"""

import json
import os
from datetime import datetime

class JeevesArchive:
    def __init__(self, filename="news_archive.jsonl"):
        # Määritetään polku archive-kansioon
        base_dir = os.path.dirname(os.path.abspath(__file__))
        archive_dir = os.path.join(base_dir, "archive")

        # Luodaan archive-kansio, jos se puuttuu
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
            print(f"[*] Created missing archive directory: {archive_dir}")

        self.path = os.path.join(archive_dir, filename)

    def is_already_archived(self, url):
        """Tarkistaa onko uutinen jo tallennettu URL:n perusteella."""
        if not os.path.exists(self.path):
            return False

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("url") == url:
                        return True
                except json.JSONDecodeError:
                    continue
        return False

    def save_to_archive(self, entry):
        """Lisää uuden analyysin arkistoon."""
        # Lisätään tallennusajankohta
        entry["archived_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def sync_from_metadata(self, metadata_path):
        """Kopioi kaikki valmiit uutiset metadatasta arkistoon, jos ne puuttuvat sieltä."""
        if not os.path.exists(metadata_path):
            print(f"[!] Jeeves: Metadata-tiedostoa ei löytynyt: {metadata_path}")
            return 0

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] Jeeves: Virhe metadataa lukiessa: {e}")
            return 0

        added = 0
        # Haetaan uutiset 'archive'-listasta (tai 'history' riippuen koodista)
        news_list = data.get('archive', [])

        for entry in news_list:
            url = entry.get('url')
            # Jos uutisella on URL, se ei ole jo arkistossa ja siinä on oikea analyysi
            if url and not self.is_already_archived(url):
                summary = entry.get('summary', '')
                # Suodatetaan pois tyhjät tai "pending"-tilassa olevat
                if len(summary) > 50 and "odotetaan" not in summary.lower() and "waiting" not in summary.lower():
                    self.save_to_archive(entry)
                    added += 1
        return added
