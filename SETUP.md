# Setup Guide: VCW Multi-AI Dialogue Framework

This guide walks you through setting up the experimental framework from scratch.

---

## Prerequisites

### Required Software

- **Python 3.9 or higher** (3.11 recommended)
- **pip** (Python package manager)
- **A terminal/command line interface**
- **A text editor** (VS Code recommended for viewing JSON and Python files)

### Required API Access

You will need API keys from three providers:

| Provider | Model Used | Where to Get Key |
|----------|-----------|------------------|
| Anthropic | Claude (claude-sonnet-4-20250514) | https://console.anthropic.com/ |
| Google | Gemini (gemini-2.0-flash) | https://aistudio.google.com/apikey |
| OpenAI | GPT-4o | https://platform.openai.com/api-keys |

**Cost Note:** Running the full 6-condition experiment costs approximately $20-50 in API credits, depending on dialogue length. A single pilot run costs ~$1-3.

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/jgraycox-coa/vcw-multi-ai-dialogue.git

# Navigate into the directory
cd vcw-multi-ai-dialogue
```

---

## Step 2: Create a Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects.

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

**You'll know it's active when you see `(venv)` at the start of your terminal prompt.**

To deactivate later: `deactivate`

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `anthropic` — Anthropic API client
- `google-generativeai` — Google Gemini API client  
- `openai` — OpenAI API client
- `python-dotenv` — For loading environment variables

---

## Step 4: Configure API Keys

Create a file named `.env` in the project root directory:

```bash
# Create the file
touch .env
```

Open `.env` in a text editor and add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

**Security Note:** The `.env` file is listed in `.gitignore` and will not be uploaded if you push changes. Never commit API keys to version control.

---

## Step 5: Verify API Access

Test that each API is working:

```bash
python -c "
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model='claude-sonnet-4-20250514',
    max_tokens=50,
    messages=[{'role': 'user', 'content': 'Say hello'}]
)
print('Anthropic:', response.content[0].text)
"
```

```bash
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content('Say hello')
print('Google:', response.text)
"
```

```bash
python -c "
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model='gpt-4o',
    messages=[{'role': 'user', 'content': 'Say hello'}],
    max_tokens=50
)
print('OpenAI:', response.choices[0].message.content)
"
```

If all three return greetings, your setup is complete!

---

## Step 6: Run a Test Dialogue

Run a single condition to verify everything works:

```bash
python vcw_integration_v4.py --condition 1 --turns 3
```

This runs:
- **Condition 1:** Claude as Proposer, Gemini as Responder
- **3 turns** (shorter than full experiment for testing)

Output will be saved to `vcw_experiments/` directory.

---

## Common Setup Issues

### "ModuleNotFoundError: No module named 'anthropic'"

Your virtual environment isn't activated. Run:
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### "Invalid API key"

Check that:
1. Your `.env` file is in the project root directory
2. There are no extra spaces around the `=` sign
3. The key is complete (didn't get cut off when copying)

### "Rate limit exceeded"

The APIs have rate limits. Solutions:
- Wait a few minutes and try again
- Reduce the number of turns
- Add delays between API calls (see CONFIGURATION.md)

### "Permission denied" when creating files

Make sure you have write permissions in the directory:
```bash
chmod 755 vcw_experiments
```

---

## Next Steps

- See **CONFIGURATION.md** for how to customize experiments
- See **TROUBLESHOOTING.md** for common runtime issues
- See the **prompts/** directory to understand the prompt system

---

## File Structure After Setup

```
vcw-multi-ai-dialogue/
├── .env                      # Your API keys (created by you)
├── venv/                     # Virtual environment (created by you)
├── vcw_integration_v4.py     # Main orchestration script
├── requirements.txt          # Python dependencies
├── config.json               # Experiment configuration
├── prompts/
│   ├── vcw_prompts_v3.py     # Prompt generation module
│   └── vcw_background_document.md
├── data/                     # Pre-existing experimental data
├── vcw_experiments/          # Output directory (created on first run)
└── ...
```
