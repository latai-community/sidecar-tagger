# Setup Guide

Complete installation instructions for Sidecar-tagger.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**
- **Git**
- **A Google Gemini API Key** (See [Configure API Keys](#3-configure-api-keys))
- **ExifTool** (external system dependency):
  - Windows: `winget install exiftool`
  - macOS: `brew install exiftool`
  - Linux: `sudo apt-get install -y libimage-exiftool-perl`

---

## 1. Clone the Repository

```bash
git clone https://github.com/latai-community/sidecar-tagger.git
cd sidecar-tagger
```

---

## 2. Python Setup

It is highly recommended to use a virtual environment to avoid conflicts with other Python projects.

### Windows 11 (PowerShell)

```powershell
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

### macOS

> **Important:** macOS ships with Python 3.9.x by default. Sidecar-tagger requires Python 3.11+.
> If you get a version error, install Python 3.12 with [pyenv](https://github.com/pyenv/pyenv):

```bash
# Install pyenv
brew install pyenv

# Add pyenv to your shell
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.12 and set it for this project
pyenv install 3.12
pyenv local 3.12

# Create and activate the virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
```

### Linux

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

> **Note for Linux users:** If your distribution ships with Python < 3.11, install a newer version using [pyenv](https://github.com/pyenv/pyenv) or your package manager's Python 3.11+ package.

---

## 3. Configure API Keys

The engine requires a **Google Gemini API Key** for Layer 4 analysis.

1. **Get your key:** Visit the [Google AI Studio](https://aistudio.google.com/app/apikey) to generate a free or pay-as-you-go API key.
2. **Setup your environment file:**
   - Copy the example file: `cp .env.example .env`
   - Open `.env` and replace `your_api_key_here` with your actual key.

**Example `.env` file:**
```env
# Your actual key looks like this: AIzaSy...
GEMINI_API_KEY=AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6
GEMINI_MODEL=gemini-2.0-flash
LLM_PROVIDER=gemini
```

---

## 4. Install Dependencies

Ensure your virtual environment is activated, then run:

```bash
pip install -e ".[dev]"
```

---

## 5. Available Model Discovery

If you receive a `404: model not found` error, your API key might not have access to the default model in your region. You can use the included discovery script to find models you **can** use.

**Quick test (recommended - no quota used):**
```bash
# Windows
.\.venv\Scripts\python.exe list_models.py

# Linux / macOS
python3 list_models.py
```

This uses `count_tokens` to verify model availability without spending your quota.

**Full test (uses quota):**
```bash
# Windows
.\.venv\Scripts\python.exe list_models.py --mode full

# Linux / macOS
python3 list_models.py --mode full
```

This uses actual `generate_content` requests to confirm models respond correctly. Useful to check if your quota is exhausted.

**Update your .env:**
After running the script, copy the recommended model name from the output and update your `.env` file:
```env
GEMINI_MODEL=gemini-2.5-flash
```

---

## Troubleshooting

### Windows "Execution Policy" Error
If you cannot activate the virtual environment on Windows, run this command in an Administrator PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "ImportError: cannot import name..."
If tests fail with an `ImportError`, ensure you have installed the requirements (`pip install -e ".[dev]"`) and that you are running `pytest` from the project root with the virtual environment activated.

### "GEMINI_API_KEY not found"
Ensure your `.env` file is in the root directory and contains the correct variable name: `GEMINI_API_KEY`.

### "Could not find a version that satisfies the requirement"
This error means your system Python is older than 3.11. Sidecar-tagger requires Python 3.11+.

**Fix:** Install Python 3.12 with [pyenv](https://github.com/pyenv/pyenv):
```bash
brew install pyenv
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
pyenv install 3.12
pyenv local 3.12
```

Then recreate your virtual environment:
```bash
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### "model not found" or "404" Error
Your API key may not have access to the configured model in your region. Run the [model discovery script](#5-available-model-discovery) to find available models.
