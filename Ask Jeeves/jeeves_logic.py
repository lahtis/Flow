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

import json
import os
import sys, io
import configparser
import time
import shutil
from datetime import datetime, timedelta

# Pakotetaan standarditulosteet UTF-8 muotoon
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 1. Peruspolut
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Kansioiden määritykset
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
MEMORY_DIR = os.path.join(BASE_DIR, "archive")

# --- AUTOMAATTINEN TARKISTUS ---
# Luodaan kansiot, jos niitä ei ole olemassa
for directory in [RESOURCES_DIR, MEMORY_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[*] Jeeves: Created missing folder: {directory}")
# -------------------------------

# 3. Tiedostojen polut
MEMORY_FILE = os.path.join(MEMORY_DIR, "jeeves_memory.json")
# METADATA_FILE = os.path.join(RESOURCES_DIR, "jeeves_metadata.json") # metadata (Localization)
METADATA_FILE = os.path.join(RESOURCES_DIR, "personality.json")
CONFIG_FILE = os.path.join(BASE_DIR, "jeeves.conf") # Pidetään juuressa turvassa

if not os.path.exists(METADATA_FILE):
    print(f"[!] WARNING: {METADATA_FILE} is missing. The program may not function properly.")

def get_config_value(key, lang="fi"):
    """Hakee teknisen konfiguraation metadatasta."""
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(lang, {}).get("system_config", {}).get(key)
    except Exception as e:
        print(f"[!] Error retrieving configuration: {e}")
        return None

def get_localized_text(key_path, lang="fi"):
    try:
        # Varmistetaan, että käytetään globaalia polkua
        if not os.path.exists(METADATA_FILE):
            return f"[{key_path}]"

        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Valitaan kieli tai fallback englantiin
        lang_data = data.get(lang, data.get("en", {}))

        # 1. Piste-navigointi (esim. "personality.greetings.morning")
        keys = key_path.split('.')
        val = lang_data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                val = None
                break

        # Jos löytyi validi merkkijono, palautetaan se
        if val and isinstance(val, str):
            return val

        # 2. Varajärjestelmä automaattisille lohkohauille
        for section in ["ui", "personality"]:
            if section in lang_data and key_path in lang_data[section]:
                result = lang_data[section][key_path]
                # Jos kyseessä on lista (kuten idle_comments), palautetaan se sellaisenaan
                return result

        return f"[{key_path}]"
    except Exception:
        return f"[{key_path}]"

def get_priority_keywords():
    """Hakee prioriteettiavainsanat konfiguraatiosta vikasietoisesti."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        try:
            # Yritetään ensin standardia UTF-8
            config.read(CONFIG_FILE, encoding='utf-8')
        except (UnicodeDecodeError, Exception):
            # Jos epäonnistuu, käytetään latin-1 (joka lukee Windowsin ä-kirjaimet oikein)
            config.read(CONFIG_FILE, encoding='latin-1')

        if 'KEYWORDS' in config and 'priority' in config['KEYWORDS']:
            return [k.strip() for k in config['KEYWORDS']['priority'].split(',') if k.strip()]
    return []

def get_news_category(title, source_name=""):
    """Määrittää uutisen kategorian avainsanojen ja lähteen perusteella."""
    t = title.lower()
    s = source_name.lower()

    # 1. Pelit ja Steam
    if any(x in t for x in ['steam', 'gaming', 'proton', 'wine', 'valve', 'peli', 'fps']) or "gaming" in s:
        return "Gaming"

    # 2. Laitteisto (Hardware)
    if any(x in t for x in ['nvidia', 'amd', 'intel', 'cpu', 'gpu', 'rtx', 'ryzen', 'benchmarks', 'displayport']):
        return "Hardware"

    # 3. Tietoturva (Security)
    if any(x in t for x in ['cve', 'vulnerability', 'security', 'haavoittuvuus', 'patched', 'exploit']):
        return "Security"

    # 4. Ubuntu
    if "ubuntu" in t or "canonical" in t:
        return "Ubuntu"

    # Oletus
    return "Linux"


def format_summary(text):
    """Lisää sisennykset ja kauneusvirheet tekstiin, sir."""
    lines = text.split('\n')
    # Lisätään jokaisen rivin alkuun kaksi välilyöntiä (sisennys)
    indented = "\n".join([f"    {line.strip()}" for line in lines if line.strip()])
    return indented

def check_environment():
    """Varmistaa, että tarvittavat tiedostot ovat olemassa, luo ne tarvittaessa."""
    # 1. Luodaan konfiguraatio, jos se puuttuu
    if not os.path.exists(CONFIG_FILE):
        print(f"[*] Jeeves: Luodaan uusi konfiguraatiotiedosto: {CONFIG_FILE}")
        config = configparser.ConfigParser()
        config['SETTINGS'] = {'api_key': 'LISÄÄ_GEMINI_AVAIN', 'language': 'fi'}
        config['API_KEYS'] = {'groq': 'LISÄÄ_GROQ_AVAIN'}
        config['MODELS'] = {
            'gemini': 'gemini-2.0-flash',
            'groq': 'llama-3.3-70b-versatile'
        }
        config['FEEDS'] = {
            'linux_primary': 'https://www.phoronix.com/rss.php',
            'security_primary': 'https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml'
        }
        config['KEYWORDS'] = {'priority': 'CVE, Kernel, Security, Critical, CachyOS'}

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print("[!] Huomio: Käykää lisäämässä API-avaimet tiedostoon, sir.")

    # 2. Luodaan muisti, jos se puuttuu
    if not os.path.exists(MEMORY_FILE):
        print(f"[*] Jeeves: Alustetaan uusi arkisto: {MEMORY_FILE}")
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"archive": []}, f, indent=4)

    # 3. Luodaan .gitignore, jos se puuttuu (GPL3-valmius)
    gitignore_path = os.path.join(BASE_DIR, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("jeeves.conf\narchive/\n__pycache__/\n*.pyc\n")
        print("[*] Jeeves: Created a .gitignore to protect your settings, sir.")

    return True

import configparser

class JeevesMemory:
    def __init__(self):
        # 1. Ladataan konfiguraatio (TÄRKEÄÄ: Lisätty tämä osa)
        self.config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE, encoding='utf-8')

        # 2. Asetetaan kieli attribuuttiin (KORJAA AIEMMAT VIRHEET)
        # Katsotaan SETTINGS-lohkosta language, oletus 'fi'
        try:
            self.lang = self.config['SETTINGS'].get('language', 'fi').lower()
        except (KeyError, Exception):
            self.lang = 'fi'

        # 3. Ladataan uutisdata (alkuperäinen logiikka)
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"archive": []}
        return {"archive": []}

    def _save_data(self):
        """ Tallentaa nykyisen tiedon muistiin """
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Virhe tallennettaessa muistia: {e}")

    def add_entry(self, title, summary, url, category):
        """ Lisää uuden uutisen arkistoon """
        now = datetime.now()
        entry = {
            "title": title,
            "summary": summary,
            "url": url,
            "category": category,
            "timestamp": now.timestamp(),
            "date": now.strftime('%Y-%m-%d')  # Lisätään ISO-päivämäärä rotaatiota varten
        }
        self.data['archive'].append(entry)
        self._save_data()

    def rotate_archive(self, days_to_keep=14):
        """Siirtää vanhat uutiset erilliseen arkistotiedostoon."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        to_keep = []
        to_archive = []

        for entry in self.data['archive']:
            # Ensisijaisesti katsotaan 'timestamp', toissijaisesti 'date'
            try:
                ts = entry.get('timestamp')
                if ts:
                    entry_time = datetime.fromtimestamp(float(ts))
                else:
                    # Fallback vanhaan formaattiin
                    entry_time = datetime.strptime(entry.get('date', '2000-01-01'), '%Y-%m-%d')

                if entry_time < cutoff_date:
                    to_archive.append(entry)
                else:
                    to_keep.append(entry)
            except Exception:
                to_keep.append(entry)

        if to_archive:
            # Luodaan kansio arkistoille jos se puuttuu
            if not os.path.exists(MEMORY_DIR):
                os.makedirs(MEMORY_DIR)

            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_filename = os.path.join(MEMORY_DIR, f"jeeves_archive_{timestamp_str}.json")

            with open(archive_filename, 'w', encoding='utf-8') as f:
                json.dump({'archive': to_archive}, f, ensure_ascii=False, indent=4)

            self.data['archive'] = to_keep
            self._save_data()
            return len(to_archive), archive_filename

        return 0, None

    def get_report(self, days=7):
        now = time.time()
        cutoff = now - (days * 24 * 60 * 60)
        return [e for e in self.data["archive"] if float(e.get("timestamp", 0)) >= cutoff]


def get_time_based_greeting(lang="fi"):
    """Hakee tervehdyksen kellonajan mukaan käyttäen uutta polkurakennetta."""
    hour = datetime.now().hour

    if 5 <= hour < 10:
        key = "personality.greetings.morning"
    elif 10 <= hour < 14:
        key = "personality.greetings.day"
    elif 14 <= hour < 18:
        key = "personality.greetings.afternoon"
    elif 18 <= hour < 22:
        key = "personality.greetings.evening"
    else:
        key = "personality.greetings.night"

    return get_localized_text(key, lang)

def get_category_comment(category, lang="fi"):
    """Hakee hovimestarin kommentin uutisluokasta."""
    # Varmistetaan, että kategoria alkaa isolla (esim. "Security")
    formatted_cat = category.capitalize()
    comment = get_localized_text(f"personality.category_comments.{formatted_cat}", lang)

    # Fallback jos kategorialle ei ole omaa kommenttia
    if comment.startswith("["):
        comment = get_localized_text("personality.category_comments.Default", lang)

    return comment

if __name__ == "__main__":
    check_environment()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')

    # 1. Haetaan asetukset
    current_lang = config['SETTINGS'].get('language', 'fi').lower()
    show_full = "--full" in sys.argv

    # Haetaan prioriteettisanat
    keywords_str = config['KEYWORDS'].get('priority', '') if 'KEYWORDS' in config else ''
    keywords = [k.strip().lower() for k in keywords_str.split(',') if k.strip()]

    # 2. Alustetaan muisti
    memory = JeevesMemory()
    entries = memory.get_report(days=7)

    # --- UUSI MODULAARINEN TULOSTUS ---
    # Tuodaan uusi muotoilija (varmista että jeeves_formatter.py on olemassa)
    try:
        from jeeves_formatter import JeevesFormatter
        formatter = JeevesFormatter(get_localized_text, current_lang)

        greeting = get_time_based_greeting(current_lang)
        pending_indicator = get_localized_text("ui.pending", current_lang)

        # Rakennetaan raportti käyttäen uutta luokkaa
        full_report = formatter.build_report(
            entries=entries,
            keywords=keywords,
            greeting=greeting,
            pending_indicator=pending_indicator,
            show_full=show_full
        )

        # Tulostetaan koko komeus kerralla
        print(full_report)

    except ImportError:
        print("[!] Jeeves: Muotoilumoduulia (jeeves_formatter.py) ei löytynyt!")
    # ----------------------------------

    # 3. Loppustatus (montako analysoimatonta)
    pending_count = sum(1 for e in entries if get_localized_text("ui.pending", current_lang) in e['summary'])
    if pending_count > 0:
        processing_text = get_localized_text("ui.processing", current_lang)
        print(f"[*] Status: {pending_count} {processing_text}")
