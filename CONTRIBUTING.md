# 🛡️ Contributing to HorizonSentinel

Thank you for your interest in contributing to HorizonSentinel!

---

### Clone the Repository
```Bash
git clone https://github.com/reory/horizon_sentinel.git
cd horizon_sentinel
```
### Install Dependencies
Install the required packages to sync your runtime environment:  
```Bash
uv add beautifulsoup4 playwright pydantic httpx fastapi cryptography pytest hypothesis
```
### Install Headless Browser Binaries
Playwright requires headless Chromium dependencies to parse dynamic single-page applications (SPAs):  
```Bash
uv run playwright install chromium
```

---

## 🧪 Testing & Code Quality
We maintain code stability through pytest and property-based testing via hypothesis.  Run the complete test suite:  
```Bash
uv run pytest
```
- Verify code coverage: 
Your test runs automatically generate a terminal coverage report mapping back to the core modules.

- Ensure that any code changes maintain or improve this coverage footprint. 

- Verify the full application pipeline: 
Always ensure the core orchestrator loop runs successfully before submitting code:
```Bash
uv run run.py
```

---

## 🚀 Pull Request Workflow

We welcome structural improvements, bug fixes, and roadmap feature integrations.

- Branch Out: Create a focused feature branch from main (e.g., feature/slack-webhooks or fix/threshold-regex).
 
- Implement & Test: Write clean, modular Python code matching our strict Pydantic blueprints. Ensure your new code has accompanying tests. 

- Validate: Run uv run pytest and ensure everything passes with zero warnings.

- Submit PR: Open a clean Pull Request against the upstream main branch. Provide a direct, actionable summary of what your change addresses.

Happy Coding 😊