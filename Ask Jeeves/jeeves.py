# -*- coding: utf-8 -*-

"""
Jeeves - Personal News Butler
File: jeeves.py
Author: [Tuomas Lähteenmäki]
Version: v2.2.0
Licence: GNU General Public License v3.0 (GPLv3)

Description:
    Main orchestrator for the Jeeves system. Manages the workflow between
    RSS fetching (Gemini), Failover (Groq Mirror), and Archiving.
"""

import subprocess
import sys
import configparser
import os
from jeeves_logic import check_environment, JeevesMemory, get_localized_text, CONFIG_FILE
from jeeves_archive import JeevesArchive


# Tuodaan arkistointi mukaan tarkistuksia varten
from jeeves_archive import JeevesArchive

def main():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    lang = config['SETTINGS'].get('language', 'en').lower()

    # Alustetaan muisti ja arkisto
    memory = JeevesMemory()
    archive = JeevesArchive()

    # 3. Käynnistys
    print(get_localized_text("starting_routines", lang) or "[*] Starting routines...")

    # 4. Varmistus ja Gemini
    check_environment()
    print(get_localized_text("fetching_news_gemini", lang) or "[*] Fetching news...")
    subprocess.run([sys.executable, "ask_jeeves.py"])

    # --- UUSI VAIHE: SYNKRONOINTI ARKISTOON ---
    # Tämä varmistaa, että myös aiemmin muistiin jääneet uutiset menevät arkistoon
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "jeeves_metadata.json")
    synced_count = archive.sync_from_metadata(metadata_path)
    if synced_count > 0:
        print(f"[*] Jeeves: Herra, synkronoitu {synced_count} uutta uutista arkistoon.")
    # -----------------------------------------

    # Päivitetään muisti-olio
    memory = JeevesMemory()

    # 5. Rästitunnistus (Varmistettu versio)
    p_fi = get_localized_text("pending", "fi")
    p_en = get_localized_text("pending", "en")

    pending = [
        e for e in memory.data['archive']
        if e['summary'] in [p_fi, p_en] or len(e['summary']) < 100 or "quota" in e['summary'].lower()
    ]

    if pending:
        p_msg = get_localized_text("pending_count_msg", lang) or "summaries are still pending."
        m_msg = get_localized_text("activating_mirror", lang) or "[*] Activating Groq Mirror, sir..."

        print(f"[*] Jeeves: {len(pending)} {p_msg}")
        print(m_msg)

        # AJETAAN PEILI
        subprocess.run([sys.executable, "jeeves_mirror.py"])
        memory = JeevesMemory()

    # 6. Loppuraportti
    report_ready_txt = get_localized_text('report_ready', lang) or "Report ready:"
    print(f"\n{report_ready_txt}")
    subprocess.run([sys.executable, "jeeves_logic.py"])

if __name__ == "__main__":
    main()
