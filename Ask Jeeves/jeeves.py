# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler
File: jeeves.py
Author: [Tuomas Lähteenmäki]
Version: v2.1.0
Licence: GNU General Public License v3.0 (GPLv3) /Json MIT
Website:

Description: This software fetches news from RSS feeds, analyzes it with AI models (Gemini/Groq), and presents it in a localized manner.
Notes:
- Localization: Finnish (fi) and English (en).
"""

import subprocess
import sys
import configparser
from jeeves_logic import check_environment, JeevesMemory, get_localized_text, CONFIG_FILE

def main():
    # 1. Luetaan kieli suoraan tiedostosta, jotta emme ole riippuvaisia memory-olion rakenteesta
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')

    # Haetaan kieli (oletuksena 'en')
    lang = config['SETTINGS'].get('language', 'en').lower()

    # 2. Alustetaan muisti uutisia varten
    memory = JeevesMemory()

    # 3. Käynnistys (Metadatasta)
    print(get_localized_text("starting_routines", lang) or "[*] Starting routines...")

    # 4. Varmistus ja Gemini
    check_environment()
    print(get_localized_text("fetching_news_gemini", lang) or "[*] Fetching news...")
    subprocess.run([sys.executable, "ask_jeeves.py"])

    # 5. Rästitunnistus (Varmistettu versio)

    subprocess.run([sys.executable, "ask_jeeves.py"])

    # --- TÄRKEÄ LISÄYS ---
    # Päivitetään muisti-olio lukemaan ask_jeeves.py:n tekemät muutokset levyltä
    memory = JeevesMemory()
    # ---------------------

    p_fi = get_localized_text("pending", "fi")
    p_en = get_localized_text("pending", "en")

    # Katsotaan rästiksi uutiset, jotka:
    # 1. Ovat metadatan mukaisessa odotustilassa
    # 2. Ovat liian lyhyitä (alle 100 merkkiä on yleensä vain virheilmoitus tai tynkä)
    # 3. Sisältävät virheen merkkejä (esim. "Error" tai "quota")
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

        # TÄRKEÄÄ: Ladataan muisti uudelleen, jotta loppuraportti näyttää Mirrorin tekemät analyysit!
        memory = JeevesMemory()

    # 6. Loppuraportti
    report_ready_txt = get_localized_text('report_ready', lang) or "Report ready:"
    print(f"\n{report_ready_txt}")
    subprocess.run([sys.executable, "jeeves_logic.py"])

if __name__ == "__main__":
    main()

