"""
Jeeves - Personal news butler
File: sanitize_jeeves.py
Author: [Tuomas Lähteenmäki]
Version: v2.1.1
Licence: GNU General Public License v3.0 (GPLv3)

Description:
This script repairs JSON syntax errors in personality.json and
removes duplicate news entries from the memory archive.
"""

import json
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSONALITY_FILE = os.path.join(BASE_DIR, "resources", "personality.json")
MEMORY_FILE = os.path.join(BASE_DIR, "archive", "jeeves_memory.json")

def repair_json_syntax(file_path):
    """Attempts to load the JSON file and reports specific error locations."""
    print(f"[*] Checking: {file_path}")
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"[+] {os.path.basename(file_path)} is syntactically correct!")
        return True
    except json.JSONDecodeError as e:
        print(f"\n[!!!] SYNTAX ERROR FOUND:")
        print(f"      Line: {e.lineno}, Column: {e.colno}")
        print(f"      Message: {e.msg}")

        # Read the file and display the problematic lines
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                print("-" * 40)
                for i in range(start, end):
                    prefix = ">>> " if i + 1 == e.lineno else "    "
                    print(f"{prefix}{i + 1}: {lines[i].rstrip()}")
                print("-" * 40)
        except Exception:
            print("[!] Could not read file content for preview.")
        return False

def clean_duplicates():
    """Removes identical news titles from the memory archive."""
    print(f"[*] Checking for duplicates in: {MEMORY_FILE}")
    if not os.path.exists(MEMORY_FILE):
        print("[!] Memory file not found. Skipping duplicate check.")
        return

    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'archive' not in data:
            return

        original_count = len(data['archive'])
        seen_titles = set()
        new_archive = []

        for entry in data['archive']:
            title = entry.get('title', '').strip()
            if title not in seen_titles:
                new_archive.append(entry)
                seen_titles.add(title)

        if len(new_archive) < original_count:
            data['archive'] = new_archive
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[+] Cleanup complete: Removed {original_count - len(new_archive)} duplicates.")
        else:
            print("[+] No duplicates found.")

    except Exception as e:
        print(f"[!] Error processing memory: {e}")

if __name__ == "__main__":
    print(f"{'='*55}")
    print(f"   JEEVES SANITIZER v2.1.1 - [GPLv3]")
    print(f"{'='*55}")

    # 1. Check localization file
    is_ok = repair_json_syntax(PERSONALITY_FILE)

    # 2. Clean memory
    print("")
    clean_duplicates()

    print(f"{'='*55}")
    if not is_ok:
        print("[NOTICE] Please fix the JSON error mentioned above, sir.")
    else:
        print("[DONE] All systems clean. You may proceed, sir.")
