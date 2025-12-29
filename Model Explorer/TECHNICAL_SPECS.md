## Component: Model Explorer (Utility)
**Version:** 1.0.0  
**License:** GPLv3  
**Author:** Tuomas Lähteenmäki

### Description
Model Explorer (Utility) is a small but important utility program (maintenance tool). Its purpose is to keep you up to date on which AI models you can use at any given time.

### Core Functionalities
1. **Model Discovery**: A maintenance tool to keep your suite up-to-date with the latest AI models.
2. **Metadata Listing**: 
    - **Feature**: Lists all available `model_id` variants (e.g., `gemini-flash-latest`).
    - **Feature**: Displays supported actions for each model.

### Technical Implementation
- **Config**: Uses `model_checker.conf` for API key isolation.
- **Library**: Powered by `google-genai` Python SDK.
- **Protocol**: Direct REST query via the `client.models.list()` method.
