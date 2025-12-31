# -*- coding: utf-8 -*-

"""
Jeeves - Personal news butler
File: ask_jeeves.py and jeeves_logic.py
Author: [Tuomas Lähteenmäki]
Version: 3.1.0
Licence: GNU General Public License v3.0 (GPLv3)
Source: https://github.com/lahtis/Flow/tree/main/Ask%20Jeeves

Description: This script check latest version of program.
.
"""

import requests

VERSION_URL = "https://raw.githubusercontent.com/lahtis/Flow/refs/heads/main/Ask%20Jeeves/test/version.txt"

def check_for_updates(current_version):
    """
    Vertaa paikallista versiota GitHubin versioon.
    Palauttaa (uusi_versio, latauslinkki) jos päivitys löytyy, muuten None.
    """
    try:
        # Asetetaan lyhyt timeout, ettei ohjelma jumiudu jos netti on hidas
        response = requests.get(VERSION_URL, timeout=5)

        if response.status_code == 200:
            remote_version = response.text.strip()

            # Yksinkertainen vertailu: jos kaukana oleva versio on eri kuin paikallinen
            if remote_version != current_version:
                repo_url = "https://github.com/lahtis/Flow/tree/main/Ask%20Jeeves"
                return remote_version, repo_url
    except Exception as e:
        print(f"[!] Update check failed: {e}")

    return None
