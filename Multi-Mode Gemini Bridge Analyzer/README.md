# mmAnalyzer - Multi-Mode Gemini Bridge Analyzer

**Version:** 1.2.0  
**License:** GPLv3  
**Author:** Tuomas Lähteenmäki

Multi-Mode Gemini Bridge Analyzer Suite is a collection of professional AI-driven development tools designed to bridge local source code environments with the Google Gemini API. 
It provides automated, high-quality code reviews, structural analysis, and modernization suggestions.

---

## 🚀 Included Tools

### 1. mmAnalyzer (File Analyzer)
The core engine for analyzing entire source files (`.c`, `.h`, `.py`).
* **Feature**: Automatically sanitizes Windows paths (handling spaces and quotes).
* **Output**: Generates timestamped reports in `analysis_reports/`.

### 2. Clipboard Analyzer (IDE Companion)
A rapid-response tool optimized for **CodeBlocks** and other IDEs.
* **Workflow**: Copy code to clipboard (`Ctrl+C`) -> Run Script -> Get Analysis.
* **Integration**: Can be added as an "External Tool" directly inside CodeBlocks.
* **Output**: Saves history in `clipboard_reports/`.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
  
   cd Multi-Mode Gemini Bridge Analyzer

2. **Install Dependencies**
   ```Bash
   pip install google-genai pyperclip
API Configuration: Run either script once to generate the .conf files. Open mmAnalyzer_config.conf or clipboard_config.conf and add your Gemini API Key:

3. **SETTINGS**
* api_key = YOUR_GOOGLE_API_KEY
  
4. **How to Use**
Using the File Analyzer:
   ```Bash
   python mmAnalyzer.py

Enter the path to your file (e.g., C:\Projects\main.c).

Using the Clipboard Analyzer in CodeBlocks:
Highlight code in CodeBlocks.

Press Ctrl + C.

Run the analyzer (or use your custom shortcut like Ctrl+Shift+A).

5. **Technical Specifications**
Model: Optimized for gemini-flash-latest.
* Resilience: Includes a 30-second automated retry logic for HTTP 429 (Rate Limit) errors.
* Security: sensitive configuration files and reports are excluded from Git via .gitignore.

6. **License**
This project is licensed under the GPLv3 License. See the LICENSE file for details.

7. **History**
- Add detailed sections for mmAnalyzer and Clipboard Analyzer
- Include installation, usage, and IDE workflow instructions
- Document the directory structure and security protocols
- Align project description with v1.2.0 standards
