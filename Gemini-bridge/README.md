# Gemini Bridge: Multi-File Analyzer

**Version:** 1.2  
**License:** GPLv3  
**Author:** Tuomas Lähteenmäki

Gemini Bridge is a professional, lightweight AI-driven tool designed to automate code reviews and structural analysis. It bridges local source files—specifically C-headers (`.h`), C-source (`.c`), and Python (`.py`)—with the Google Gemini API to provide actionable technical feedback.

---

## 🚀 Key Features

* **Multi-Language Support**: Optimized for analyzing logic in `.py` and `.c` files, as well as architectural structures in `.h` files.
* **Windows Path Resilience**: Built-in support for absolute Windows paths, automatically handling spaces and surrounding quotes.
* **Automated Reporting**: Every analysis is saved with a timestamp in a dedicated `analysis_reports/` directory.
* **Resilient Connectivity**: Implements an automated retry loop to handle API rate limits (HTTP 429) gracefully.
* **Config-Driven**: Customize your AI persona and analysis parameters via `gbridge_config.conf`.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/lahtis/gemini-bridge.git](https://github.com/your-username/gemini-bridge.git)
   cd gemini-bridge
   
2. Install Dependencies: Ensure you have the Google GenAI SDK installed:
   ```bash
   pip install google-genai
   
3. Initialize: Run the script for the first time to generate the configuration file:
   ```bash
   python gbridge.py
   
4. Configure: Open bridge_config.conf and paste your Gemini API key:

5. Usage
  Run the bridge and provide the path to the file you want to analyze:
   ```bash
   python gbridge.py

  When prompted, enter the filename (e.g., main.c or C:\Users\Name\Desktop\project\header.h). 
  The AI will analyze the code and output 3 specific improvements.

6. Project Structure
* gbridge.py: The core engine of the bridge.
* gbridge_config.conf: User settings and prompt templates.
' analysis_reports/: Automatically generated folder containing your AI review history.
* TECHNICAL_SPECS.md: Deep dive into the system architecture and error handling.

7. License
This project is licensed under the GPLv3 License. See the LICENSE file for details.


  

   
