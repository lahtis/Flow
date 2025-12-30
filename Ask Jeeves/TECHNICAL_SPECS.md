# Technical Specifications - Project Jeeves (v2.1.0)

This document defines the technical architecture, data handling, and operational logic of the Jeeves system.

---

## 🏗 System Architecture

Jeeves is a Python-based system structured into modular components to ensure high availability and clean separation of concerns.

### Core Components:

| File | Role |
| :--- | :--- |
| **`Jeeves_gui.py`** | **Primary User Interface (UI).** A graphical window for viewing news reports and interacting with Jeeves. |
| **`ask_jeeves.py`** | **Backend Engine & CLI.** Manages RSS ingestion, AI analysis, and provides a direct terminal-based report. |
| **`jeeves_mirror.py`** | **Failover System (Mirror).** Coordinates secondary AI processing via Groq if the primary provider is unavailable. |
| **`jeeves_logic.py`** | **Core Logic Engine.** Orchestrates localization, business rules, and dynamic etiquette logic. |
| **`reset_analysis.py`** | **Maintenance Utility.** Clears analysis flags and performs memory maintenance. |

---

## 💾 Data Management

Unlike previous iterations in C, the Python implementation utilizes dynamic data handling to ensure flexibility and stability.

* **Data Format**: All information is stored and processed using standard JSON objects.
* **Active Memory (`archive/jeeves_memory.json`)**: Stores current news items, AI-generated summaries, and metadata.
* **Automatic Archiving**: To maintain peak performance, the system automatically migrates news items older than 14 days to the `archive/` directory.

---

## 🌍 Localization & Etiquette

Jeeves operates with a sophisticated localization layer to ensure a refined user experience.

* **Metadata Management**: All strings are dynamically loaded from `resources/jeeves_metadata.json`.
* **Language Support**: Primary localization is set to Finnish (`fi`) with a stable English (`en`) fallback.
* **Dynamic Greetings**: The system calculates the appropriate greeting based on the current system time:
    * **05:00 - 10:00**: Good Morning
    * **10:00 - 13:00**: Good Day
    * **13:00 - 17:00**: Good Afternoon
    * **17:00 - 22:00**: Good Evening
    * **22:00 - 05:00**: Good Night

---

## 🤖 AI Integration & Failover Protocol

To ensure uninterrupted service, Jeeves employs a dual-provider AI strategy:

1. **Primary Provider**: Google Gemini 2.0 Flash.
2. **Failover Protocol**: Should the system encounter a `429 Resource Exhausted` error (rate limiting), it immediately switches to the **Groq Mirror** (Llama-3.3-70b).
3. **Efficiency**: Summaries are processed with native Python JSON parsing, removing the need for static buffer limits.

**Brief summary of the project structure**
* UI: Modern and cross-platform (customtkinter).
* Intelligence: Two-stage AI system (google-genai + groq failover).
* Data: Handling of RSS feeds (feedparser) and JSON storage.
* Management: Centralized logic (jeeves_logic.py) and configurations (configparser).
* Stability: Background tasks (threading) and automatic archiving (shutil, datetime).
  
---

## ⚖️ License & Compliance

* **Author**: Tuomas Lähteenmäki
* **License**: GNU GPLv3.
* **Compatibility Note**: This software is the official Python evolution of the original project, optimized for dynamic memory management and enhanced AI stability.

---
*Verified for the user - December 30, 2025*
