## Linux News Automated Fetcher
**Version:** 2.1  
**License:** GPLv3  

---

## 1. Technical Architecture
The application is built on a modular "Flow" architecture, separating the execution logic from the configuration data.

### Components
- **Core Engine (`linux-news.py`)**: Handles API communication, file I/O, and error recovery.
- **Configuration (`config.conf`)**: Uses `configparser` to manage `SETTINGS` (API keys) and `PROMPT` (AI instruction templates).
- **Data Input (`keywords.txt`)**: A newline-separated list used to populate the `{topics}` variable in the prompt template.

---

## 2. API Implementation Details
- **Provider**: Google Gemini AI.
- **Model ID**: Configurable via `config.conf` (Default: `gemini-flash-latest`).
- **Resilience**: Implements a 30-second exponential backoff strategy for `429 Resource Exhausted` errors.
- **Encoding**: Strict **UTF-8** enforcement for all file operations to ensure metadata integrity.

---

## 3. Directory Logic
The script manages its own environment by verifying and creating the following structure:
- `reports/`: Storage for output files (Naming: `news_report_YYYY-MM-DD_HHMM.txt`).
- `config.conf`: Auto-generated if missing.
- `keywords.txt`: Auto-generated if missing.

---

## 4. Maintenance Rules
- **Debugging**: Root cause analysis (API vs. Logic) is required before code changes.
- **Scalability**: The prompt template in `config.conf` allows for language and tone changes without modifying the Python source code.
