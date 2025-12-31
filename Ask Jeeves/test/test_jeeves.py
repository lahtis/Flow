# -*- coding: utf-8 -*-
import os
import sys

# 1. Pakotetaan absoluuttinen polku juurikansioon
current_script_path = os.path.abspath(__file__)
test_folder = os.path.dirname(current_script_path)
root_folder = os.path.dirname(test_folder)

# Lisätään juuri polkuun
if root_folder not in sys.path:
    sys.path.insert(0, root_folder)

print(f"[*] Debug: Skriptin sijainti: {test_folder}")
print(f"[*] Debug: Juurikansio (root): {root_folder}")

# 2. Yritetään tuonti
try:
    import jeeves_logic
    from jeeves_logic import get_localized_text, get_time_based_greeting
    print("[+] Jeeves_logic ladattu onnistuneesti!\n")
except ImportError as e:
    print(f"[!] Kriittinen virhe: {e}")
    print(f"[*] Tarkista, että tiedosto {os.path.join(root_folder, 'jeeves_logic.py')} on olemassa.")
    sys.exit(1)

def run_test():
    print(f"{'='*50}")
    print(" JEEVESIN PUHETESTI (LOCALIZATION TEST)")
    print(f"{'='*50}\n")

    for kieli in ["fi", "en"]:
        print(f"--- TESTATAAN KIELI: {kieli.upper()} ---")

        # UI-testi
        val = get_localized_text("ui.pending", kieli)
        print(f"[UI] Pending-teksti: {val}")

        # Persoonallisuus-testi
        cat_msg = get_localized_text("personality.category_comments.Security", kieli)
        print(f"[REACTION] Turvallisuus: {cat_msg}")

        # Tervehdys-testi
        greeting = get_time_based_greeting(kieli)
        print(f"[GREETING] Kellonaikaan perustuva: {greeting}")

        print("-" * 30)

if __name__ == "__main__":
    run_test()
