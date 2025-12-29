# TECHNICAL_SPECS.md - Gemini Bridge v1.2

## 1. System Overview
Gemini Bridge is a Python-based utility designed to facilitate automated source code analysis using the Google Gemini Pro Generative AI model. It specializes in processing individual source files and header files to provide structural and logical improvement suggestions.

---

## 2. Architecture & Data Flow

### 2.1 Component Diagram


### 2.2 Execution Flow
1. **Initialization**: The script checks for `gbridge_config.conf`. If missing, it generates a default template.
2. **Environment Check**: It ensures the `analysis_reports/` directory exists.
3. **Input Sanitization**:
   - Accepts full system paths.
   - Automatically strips surrounding quotes (`"` and `'`) often added by Windows file explorers.
4. **Processing**:
   - Reads the target file content (UTF-8).
   - Injects code into the predefined prompt template.
5. **API Interaction**: Communicates with `google-genai` using the `gemini-flash-latest` model.
6. **Reporting**: Extracts the file's base name (via `os.path.basename`) and saves a timestamped report.

---

## 3. Configuration Details

The system uses `configparser` for persistent settings:

| Section | Key | Description | Standard |
|:---|:---|:---|:---|
| **SETTINGS** | `api_key` | Google GenAI API Key | User-defined |
| **SETTINGS** | `model_id` | AI Model identifier | `gemini-flash-latest` |
| **SETTINGS** | `attempts` | Max retries for API failures | `3` |
| **PROMPT** | `template` | The context sent to the AI | Senior Dev Persona |

---

## 4. Error Handling & Stability

### 4.1 Path Resilience
The tool specifically addresses Windows-specific pathing issues:
- **Errno 22 Fix**: Uses `os.path.basename` for output filenames to prevent illegal characters (like `:` or `\`) from appearing in the report's filename.
- **Quote Stripping**: Handles paths copied from Windows Explorer that include `"C:\Path\..."`.

### 4.2 Network & Quota Management
The script implements a retry-loop with a backoff strategy:
- **HTTP 429 (Too Many Requests)**: Triggered when the API quota is exhausted. The script waits **30 seconds** before retrying.
- **General Exceptions**: Other errors trigger a shorter wait time to handle transient network issues.

---

## 5. Security Protocols
- **Credential Isolation**: The `bridge_config.conf` is isolated from the codebase and should be ignored by version control via `.gitignore`.
- **Local Storage**: All analysis results are stored locally in the `analysis_reports/` folder to prevent accidental data leaks.

---

## 6. Version History
* **v1.0.0**: Basic Python-to-Gemini connection.
* **v1.1.0**: Multi-file support (.h, .c, .py) and Finnish localization.
* **v1.2.0**: Full English localization, Windows path sanitization, and automated report directory management. (Current Standard)
