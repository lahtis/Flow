# Jeeves - Personal News Butler (v2.1.0)

Jeeves is a sophisticated and discreet personal news butler designed to fetch technology and cybersecurity news from RSS feeds, analyze them using AI, and present them in a refined, localized manner.



## 🛠 Features

* **Multi-source Fetching:** Monitors Linux news (Phoronix), security vulnerabilities (NVD/CVE), and the Ubuntu ecosystem.
* **AI-Powered Analysis:** Utilizes the Google Gemini 2.0 Flash model for intelligent news summarization.
* **Failover System (Mirror):** If Gemini's quota is exhausted, Jeeves automatically switches to the Groq mirror server (Llama-3.3).
* **Dynamic Localization:** Full support for Finnish (fi) and English (en) via the `jeeves_metadata.json` file.
* **Smart Memory:** Automatically archives news items older than 14 days to keep the daily memory lightweight.
* **Etiquette:** Greets the user based on the time of day (Morning, Day, Afternoon, Evening, Night).



## 📂 File Structure

| File | Description |
| :--- | :--- |
| `ask_jeeves.py` | Main CLI-program: Fetch logic and AI integration. |
| `jeeves_gui.py` | Main UI: Fetch logic and AI integration. |
| `jeeves_logic.py` | Interface and reporting logic (CLI). |
| `jeeves_mirror.py` | Failover system for Groq integration. |
| `resources/` | Contains `jeeves_metadata.json` (localization strings). |
| `archive/` | News archives and `jeeves_memory.json`. |
| `jeeves.conf` | Technical configuration (API keys, feeds). |



## 🚀 Getting Started

1. **Environment Check:**
   Run `python jeeves_logic.py`. The program will automatically create missing folders and a `.gitignore` file to protect your settings.

2. **Configuration:**
   Open the generated `jeeves.conf` in the root directory and add your API keys:
   ```ini
   [SETTINGS]
   api_key = YOUR_GEMINI_KEY
   language = en
   
   [API_KEYS]
   groq = YOUR_GROQ_KEY


2.1 **Prerequisites**
Ensure you have Python 3.x installed. On Linux (Ubuntu/Debian), you may also need to install the header files for Tkinter:

   ```bash
   sudo apt-get install python3-tk

2.2 **Install Dependencies**

   ```bash
    `python -m pip install groq google-genai feedparser customtkinter`

or

   ```bash
    `python -m pip install -r requirements.txt`


3. **Usage:**
* Update news and perform analysis: `python ask_jeeves.py`
* Read the report: `python jeeves_logic.py`
* Read full summaries: `python jeeves_logic.py --full`

4. **License and Copyright**
* Author: Tuomas Lähteenmäki
* License: GNU General Public License v3.0 (GPLv3)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

5. **Jeeves is at your service, sir.**

  
