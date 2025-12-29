# Clipboard Analyzer for CodeBlocks

**Version:** 1.0  
**Part of:** Gemini Bridge Suite

This utility is designed for rapid code reviews during active development in **CodeBlocks** (or any C/C++ IDE). Instead of passing file paths, it captures code directly from your clipboard.



## 🚀 Workflow
1. **Highlight** a function or logic block in CodeBlocks.
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

