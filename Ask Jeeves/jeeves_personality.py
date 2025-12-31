# -*- coding: utf-8 -*-

"""
Jeeves - jeeves personality
File: jeeves_personality.py
Author: [Tuomas Lähteenmäki]
Version: 3.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Source: https://github.com/lahtis/Flow/tree/main/Ask%20Jeeves

Description: Jeeves personality.
Notes:
- Localization: Finnish (fi), English (en). Use own personality.json file.
"""

import datetime
import json
import random
import os
import sys


class JeevesPersonality:
    def __init__(self, filename='personality.json'):
        # 1. Haetaan tämän tiedoston (jeeves_personality.py) sijainti
        # Tämä palauttaa: C:\Users\lahti\Desktop\Projektit\Flow\Ask Jeeves
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. Muodostetaan polku resources-kansioon, joka on samassa paikassa
        # Tämä muodostaa: C:\Users\lahti\Desktop\Projektit\Flow\Ask Jeeves\resources\personality.json
        self.config_path = os.path.join(current_dir, 'resources', filename)

        self.personality_data = self._load_personality()

    def _load_personality(self):
        """Lataa tervehdykset ja kommentit JSON-tiedostosta."""
        if not os.path.exists(self.config_path):
            # Tulostetaan virhe teknisesti englanniksi
            print(f"CRITICAL ERROR: Personality file missing at {self.config_path}", file=sys.stderr)
            print("Please ensure the 'resources' folder and 'personality.json' exist.", file=sys.stderr)
            return None

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR: Failed to load personality data, sir: {e}", file=sys.stderr)
            return None

    def get_greeting(self, lang="fi"):
        """Palauttaa tervehdyksen kellonajan mukaan."""
        if not self.personality_data:
            return "Personality data not loaded, sir."

        hour = datetime.datetime.now().hour
        # Haetaan oikea kieliosio ja sieltä greetings-sanakirja
        try:
            greetings = self.personality_data[lang]["personality"]["greetings"]

            if 5 <= hour < 10:
                return greetings["morning"]
            elif 10 <= hour < 14:
                return greetings["day"]
            elif 14 <= hour < 18:
                return greetings["afternoon"]
            elif 18 <= hour < 23:
                return greetings["evening"]
            else:
                return greetings["night"]
        except KeyError:
            return "Good day, sir." # Fallback jos avainta ei löydy

    def get_commentary(self, category, priority, lang="fi"):
        """Hakee kommentin täysin JSON-tiedoston perusteella."""
        if not self.personality_data:
            return "..."

        try:
            # Polku: fi -> personality -> category_comments
            cat_comments = self.personality_data[lang]["personality"]["category_comments"]

            # 1. Tarkistetaan ensin kriittisyys (Priority)
            if priority == "Critical":
                return cat_comments.get("Critical")

            # 2. Tarkistetaan löytyykö kategoria (esim. Security, Steam, Linux)
            # Jos kategoriaa ei löydy, käytetään "Default" -viestiä
            return cat_comments.get(category, cat_comments.get("Default"))

        except KeyError:
            return "Here is the news, sir."

# Esimerkki käytöstä:
# jeeves = JeevesPersonality()
# print(jeeves.get_greeting())
