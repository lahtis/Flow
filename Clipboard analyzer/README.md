# Clipboard Analyzer for Code:Blocks

**Version:** 1.0  
**Part of:** Gemini Bridge Suite

This utility is designed for rapid code reviews during active development in **CodeBlocks** (or any C/C++ IDE). Instead of passing file paths, it captures code directly from your clipboard.

# Code:Blocks Integration Guide
To make your workflow seamless, you can add the Gemini Clipboard Analyzer directly to the CodeBlocks interface. This allows you to analyze code snippets without leaving your editor.

1. Configure the External Tool
* Open CodeBlocks.
* Go to the top menu: Tools -> Configure tools...
* Click the Add button.

2. Fill in the following details:

* **Name:** Gemini Clipboard Analyzer
* **Executable:** python (or the full path to your python.exe)
* **Parameters:** "C:\Path\To\Your\Project\clipboard_analyzer.py"
* **Working directory:** "C:\Path\To\Your\Project\"

3. Launch Options:
* Select "Launch tool visible (external console)" if you want the analysis to appear in a pop-up window.
* Click OK.

4. Usage Workflow
Highlight the code block you want to review in the editor.
* Press **Ctrl + C** to copy it.
* Go to Tools -> Gemini Clipboard Analyzer.
* The AI analysis will appear instantly, and a permanent report will be saved in your clipboard_reports/ folder.

4.1 (Optional) Set a Keyboard Shortcut
For maximum speed, assign a hotkey:
* Go to Settings -> Editor...
* Select Keyboard shortcuts from the left sidebar.
* Expand the Tools category and find Gemini Clipboard Analyzer.
* Click the New shortcut field and press your preferred keys (e.g., **Ctrl + Shift + A**).
* Click Assign and OK.

## 🚀 Workflow
1. **Highlight** a function or logic block in Code:Blocks.
2. **Press `Ctrl + C`** to copy it.
3. **Run** `python clipboard_analyzer.py`.
4. **Review** the analysis in the console or the `clipboard_reports/` folder.

## 🛠️ Technical Details
- **Input**: System clipboard via `pyperclip`.
- **Config**: `clipboard_config.conf` (Stores API key and Senior Dev prompt).
- **Storage**: Timestamped `.txt` files in `clipboard_reports/`.
- **Resilience**: Automatic 30-second backoff for API quota limits.

## 📋 Requirements
```bash
 pip install pyperclip google-genai

