# -*- coding: utf-8 -*-
import configparser
import os
from google import genai

CONFIG_FILE = "model_checker.conf"

def setup_config():
    """Luo asetustiedoston jos se puuttuu."""
    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'api_key': 'YOUR_API_KEY_HERE'
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f"[*] Created {CONFIG_FILE}. Please add your API key.")
        return False
    return True

def list_gemini_models():
    """Hakee ja listaa kaikki saatavilla olevat Gemini-mallit."""
    if not setup_config():
        return

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    api_key = config['SETTINGS'].get('api_key')

    if api_key == 'YOUR_API_KEY_HERE':
        print("[!] Päivitä API-avaimesi tiedostoon: model_checker.conf")
        return

    try:
        client = genai.Client(api_key=api_key)
        print(f"{'MODEL ID':<40} | {'SUPPORTED ACTIONS'}")
        print("-" * 80)

        # Käytetään client.models.list() hakuun
        for model in client.models.list():
            actions = ", ".join(model.supported_actions)
            # Lyhennetään nimeä jos siinä on "models/" etuliite
            display_name = model.name.replace("models/", "")
            print(f"{display_name:<40} | {actions}")

    except Exception as e:
        print(f"[!] Virhe haettaessa malleja: {e}")

if __name__ == "__main__":
    list_gemini_models()
