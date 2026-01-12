# Jeeves - Personal News Butler (v3.1.5)

Jeeves is a sophisticated and discreet personal news butler designed to fetch technology and cybersecurity news from RSS feeds, analyze them using AI, and present them in a refined, localized manner.

Tailored for power users who value both professional insights and a polished user experience, Jeeves ensures you stay informed without the noise of traditional news aggregators.


## 🛠 Features

* **Multi-source Intelligence:** Continuously monitors specialized feeds including Linux hardware (Phoronix), security vulnerabilities (NVD/CVE), and the broader Ubuntu ecosystem.
* **AI-Powered Analysis:** everages the **Google Gemini 2.0 Flash** model to provide concise, context-aware news summarization and analysis.
* **Failover System (Mirror):** Features an automated failover system. If the Gemini quota is exceeded, Jeeves seamlessly switches to the **Groq (Llama 3.3)** mirror server to ensure uninterrupted service.
* **Dynamic Localization:** Full bilingual support for **Finnish (fi)** and **English (en)**, managed through a central localization file.
* **Smart Memory:** Implements a "Smart Memory" system that archives news items older than 14 days, maintaining a lightweight and high-performance local database.
* **Butler Etiquette:** A personalized personality engine that greets the user with appropriate decorum based on the specific time of day.



## 📂 Project Structure

| File / Folder | Description |
| :--- | :--- |
| `jeeves_gui.py` | **Main GUI Application**: The modern visual interface for the user. |
| `ask_jeeves.py` | **CLI Controller**: Main entry point for command-line operations. |
| `jeeves_logic.py` | **Core Engine**: Handles RSS fetching, AI analysis, and memory management. |
| `jeeves_personality.py` | **Personality Engine**: Logic for Jeeves' greetings and commentary. |
| `jeeves_mirror.py` | **Failover System**: Handles API redundancy (Groq/Gemini). |
| `resources/` | **Assets**: Contains `personality.json` (styles/icons) and `jeeves_avatar.png`. |
| `archive/` | **Data Storage**: Local news database (`jeeves_memory.json`) and archives. |
| `jeeves.conf` | **Configuration**: Stores API keys and source RSS feed URLs. |
| `requirements.txt` | **Dependencies**: List of required Python libraries for the project. |



## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed. On Linux (Ubuntu/Debian), you must install the Tkinter header files:

```bash
sudo apt-get update
sudo apt-get install python3-tk
```
1.1 **Install Dependencies**

```bash
python -m pip install groq google-genai feedparser customtkinter pillow
```
or

```bash
python -m pip install -r requirements.txt`
```

2. **Environment Check:**
   Run `python jeeves_logic.py`. The program will automatically create missing folders and a `.gitignore` file to protect your settings.

* GOOGLE_API_KEY -> https://aistudio.google.com/app/apikey
* GROQ_API_KEY -> https://console.groq.com/home

3. **Configuration:**
   Open the generated `jeeves.conf` in the root directory and add your API keys:
```ini
   [SETTINGS]
   api_key = YOUR_GEMINI_KEY
   language = en
   
   [API_KEYS]
   groq = YOUR_GROQ_KEY
```

3. **Usage:**
* Update news and perform analysis: `python ask_jeeves.py`
* Read the report: `python jeeves_logic.py`
* Read full summaries: `python jeeves_logic.py --full`

4. **License and Copyright**
* Author: Tuomas Lähteenmäki
* License: GNU General Public License v3.0 (GPLv3)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

**Jeeves is at your service, sir.**

  
