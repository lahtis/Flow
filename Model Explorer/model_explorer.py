# -*- coding: utf-8 -*-
import configparser
import os
from google import genai

CONFIG_FILE = "model_checker.conf"

def setup_config():
    """Creates the configuration file if it is missing."""
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
    """Fetches and lists all available Gemini models."""
    if not setup_config():
        return

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    api_key = config['SETTINGS'].get('api_key')

    if api_key == 'YOUR_API_KEY_HERE':
        print("[!] Please update your API key in the file: model_checker.conf")
        return

    try:
        client = genai.Client(api_key=api_key)
        print(f"{'MODEL ID':<40} | {'SUPPORTED ACTIONS'}")
        print("-" * 85)

        # Iterate through the list of available models
        for model in client.models.list():
            actions = ", ".join(model.supported_actions)
            # Remove the "models/" prefix for cleaner display
            display_name = model.name.replace("models/", "")
            print(f"{display_name:<40} | {actions}")

    except Exception as e:
        print(f"[!] Error retrieving models: {e}")

if __name__ == "__main__":
    list_gemini_models()
