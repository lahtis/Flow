# Linux News Automated Fetcher

A professional Python-based tool designed to automate the tracking and summarization of Linux and Open Source ecosystem updates using Google Gemini AI.

## 🚀 Features
- **AI-Powered Summaries**: Leveraging Gemini 2.0 Flash to provide concise technical reports.
- **Dynamic Keywords**: Customizable search topics via an external text file.
- **Decoupled Configuration**: Separate settings for API keys, models, and search prompts.
- **Robust Error Handling**: Built-in retry logic for API rate limits (Error 429).
- **Automated Archiving**: Saves timestamped reports in an organized directory.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/lahtis/linux-news-fetcher.git](https://github.com/YourUsername/linux-news-fetcher.git)

   cd Flow/Linux-News

2. **Install dependencies**:
   ```bash
    pip install google-genai

3. **Initialize: Run the script once to generate the default configuration files**:
   ```bash
    python linux-news.py

4. **Configuration: Add your Gemini API Key to config.conf.**
  Usage
  Simply run the script:
   ```bash
   python linux-news.py
   
- Your reports will be generated in the reports/ directory.

5. **License**
Licensed under the GPLv3 License.



