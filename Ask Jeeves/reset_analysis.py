# reset_analysis.py

"""
Jeeves - Personal news butler
File: reset_analysis.py
Author: [Tuomas Lähteenmäki]
Version: 3.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Source: https://github.com/lahtis/Flow/tree/main/Ask%20Jeeves

Description: This software fetches news from RSS feeds, analyzes it with AI models (Gemini/Groq), and presents it in a localized manner.
Notes:
- Localization: Finnish (fi) and English (en).
"""

from jeeves_logic import JeevesMemory, get_localized_text

memory = JeevesMemory()
# Haetaan uusi englanninkielinen odotusviesti
new_pending_msg = get_localized_text("pending", "en")

count = 0
for entry in memory.data['archive']:
    # Muutetaan kaikki uutiset takaisin odottamaan analyysia
    entry['summary'] = new_pending_msg
    count += 1

memory._save_data()
print(f"[*] Arkisto nollattu. {count} uutista palautettu tilaan: '{new_pending_msg}'")
