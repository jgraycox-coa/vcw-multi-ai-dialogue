# Understanding the VCW Experimental Framework: A Tutorial

## A Self-Paced Guide to the Code

This tutorial walks you through the Python code that orchestrates the VCW multi-AI dialogue experiments. It's designed for intermittent learning — you can work through one module at a time and pick up where you left off.

---

## How to Use This Tutorial

**Time per module:** 30-60 minutes

**What you'll need:**
- The code files open in a text editor (VS Code recommended)
- A terminal/command line available
- Optionally, a Python interpreter to test small snippets

**Between sessions:**
- Note which module you completed
- Review the "Key Concepts" at the end of each module
- When you return, read the "Quick Recap" to refresh

---

# Module 1: Python Foundations for This Project

## 1.1 What Python Files Do We Have?

Open your project directory and look at the Python files:

```
vcw-multi-ai-dialogue/
├── vcw_integration_v4.py      # Main orchestration script
├── prompts/
│   └── vcw_prompts_v3.py      # Prompt generation module
└── requirements.txt            # Dependencies list
```

**vcw_integration_v4.py** is the "conductor" — it runs the experiment, calls the APIs, and saves results.

**vcw_prompts_v3.py** is the "librarian" — it stores and generates all the prompts used in the experiment.

## 1.2 Understanding requirements.txt

Open `requirements.txt`. You'll see something like:

```
anthropic>=0.18.0
google-generativeai>=0.4.0
openai>=1.12.0
python-dotenv>=1.0.0
```

**What this means:**
- Each line is a Python "package" (pre-written code we use)
- `>=0.18.0` means "version 0.18.0 or higher"
- `pip install -r requirements.txt` reads this file and installs all packages

**Try this:**
```bash
pip list  # Shows all installed packages
```

## 1.3 How Python Imports Work

At the top of `vcw_integration_v4.py`, you'll see lines like:

```python
import os
import json
from datetime import datetime
import anthropic
from openai import OpenAI
import google.generativeai as genai
```

**What's happening:**

- `import os` — Loads Python's built-in module for interacting with the operating system (reading files, environment variables)
- `import json` — Loads module for reading/writing JSON files
- `from datetime import datetime` — From the datetime module, import just the datetime class
- `import anthropic` — Loads the Anthropic API client (from requirements.txt)
- `from openai import OpenAI` — From the openai package, import the OpenAI class

**Analogy:** Imports are like checking out books from a library. You're telling Python "I want to use this tool."

## 1.4 Environment Variables and .env

Near the top of the code, you might see:

```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
```

**What's happening:**

1. `load_dotenv()` reads your `.env` file
2. `os.getenv('ANTHROPIC_API_KEY')` retrieves the value you stored

**Why this matters:** API keys are sensitive. We don't put them directly in code (which might be shared). Instead, we put them in `.env` (which is in `.gitignore` and never shared).

---

### Module 1: Key Concepts

- [ ] Python files (.py) contain code; requirements.txt lists dependencies
- [ ] `import` loads modules/packages for use
- [ ] `.env` file stores sensitive configuration (API keys)
- [ ] `os.getenv()` retrieves environment variables

### Module 1: Quick Quiz

1. What command installs all packages from requirements.txt?
2. Why do we use a .env file instead of putting API keys directly in code?
3. What does `from datetime import datetime` do differently than `import datetime`?

---

# Module 2: The Configuration System

## 2.1 Reading config.json

Look at `config.json`:

```json
{
  "experiment_name": "vcw_dialogue",
  "num_turns": 6,
  "models": {
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "gpt4o": "gpt-4o"
  }
}
```

In Python, we read this with:

```python
import json

with open('config.json', 'r') as f:
    config = json.load(f)

print(config['num_turns'])  # Output: 6
print(config['models']['claude'])  # Output: claude-sonnet-4-20250514
```

## 2.2 Python Dictionaries

The config is a **dictionary** — Python's key-value data structure.

```python
# Creating a dictionary
person = {
    "name": "Gray",
    "role": "researcher"
}

# Accessing values
print(person["name"])  # "Gray"

# Nested dictionaries
experiment = {
    "models": {
        "proposer": "claude",
        "responder": "gemini"
    }
}
print(experiment["models"]["proposer"])  # "claude"
```

## 2.3 How Config Flows Through the Code

When `vcw_integration_v4.py` runs:

1. **Load config:**
   ```python
   with open('config.json', 'r') as f:
       config = json.load(f)
   ```

2. **Extract values:**
   ```python
   num_turns = config['num_turns']
   models = config['models']
   ```

3. **Use in experiment:**
   ```python
   for turn in range(num_turns):
       # ... run dialogue turn
   ```

**The flow:** JSON file → Python dictionary → Variables used throughout code

## 2.4 Command Line Arguments

When you run:
```bash
python vcw_integration_v4.py --condition 1 --turns 3
```

The code receives these arguments:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--condition', type=int, default=1)
parser.add_argument('--turns', type=int, default=6)
args = parser.parse_args()

print(args.condition)  # 1
print(args.turns)      # 3
```

Command line arguments **override** config file values, giving you flexibility without editing files.

---

### Module 2: Key Concepts

- [ ] JSON files store configuration as structured data
- [ ] `json.load()` converts JSON to Python dictionaries
- [ ] Dictionaries use key-value pairs: `dict["key"]` returns value
- [ ] Nested dictionaries: `dict["outer"]["inner"]`
- [ ] `argparse` handles command line arguments

### Module 2: Exercise

Open a Python interpreter and try:
```python
import json
data = '{"name": "VCW", "turns": 6}'
config = json.loads(data)  # Note: loads for string, load for file
print(config["name"])
```

---

# Module 3: API Integration Basics

## 3.1 What Are APIs?

API = Application Programming Interface

When we call the Anthropic API, we're:
1. Sending a request (our prompt) over the internet
2. Receiving a response (Claude's reply)

It's like a conversation, but structured in code.

## 3.2 The Anthropic API

Here's how we call Claude:

```python
import anthropic

# Create a client (connection to Anthropic)
client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY from environment

# Make a request
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "What is dialogical reasoning?"}
    ]
)

# Extract the text from the response
text = response.content[0].text
print(text)
```

**Key parts:**
- `client.messages.create()` — Sends message to Claude
- `model` — Which Claude version to use
- `max_tokens` — Maximum length of response
- `messages` — The conversation history

## 3.3 The OpenAI API

Very similar structure:

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "What is dialogical reasoning?"}
    ]
)

text = response.choices[0].message.content
print(text)
```

**Note the difference:** Response structure differs slightly (`response.choices[0].message.content` vs `response.content[0].text`)

## 3.4 The Google Gemini API

Slightly different pattern:

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

response = model.generate_content("What is dialogical reasoning?")
text = response.text
print(text)
```

## 3.5 Why Wrapper Functions?

In `vcw_integration_v4.py`, you'll see functions like:

```python
def call_claude(prompt, system_prompt=None):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt}]
    
    response = client.messages.create(
        model=config['models']['claude'],
        max_tokens=4096,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text

def call_gemini(prompt, system_prompt=None):
    # Similar but for Gemini
    ...

def call_gpt4o(prompt, system_prompt=None):
    # Similar but for OpenAI
    ...
```

**Why wrappers?**
1. **Consistency** — Same interface for all three APIs
2. **Configurability** — Model names come from config
3. **Error handling** — Can add retry logic in one place
4. **Readability** — Rest of code just calls `call_claude(prompt)`

---

### Module 3: Key Concepts

- [ ] APIs let us communicate with AI services over the internet
- [ ] Each provider (Anthropic, OpenAI, Google) has its own client library
- [ ] Request structure: model, messages, max_tokens
- [ ] Response structure differs by provider
- [ ] Wrapper functions provide consistent interface

### Module 3: Exercise

If you have API keys set up, try this in Python:
```python
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'Hello, researcher!' and nothing else."}]
)
print(response.content[0].text)
```

---

# Module 4: The Prompt System

## 4.1 Overview of vcw_prompts_v3.py

Open `prompts/vcw_prompts_v3.py`. This file contains:

1. **Background document** — The VCW theoretical foundation (as a long string)
2. **System prompts** — Instructions for each role
3. **Turn-specific prompts** — How prompts evolve across dialogue phases
4. **Utility functions** — For generating the right prompt at the right time

## 4.2 Multi-line Strings in Python

You'll see content stored in triple-quoted strings:

```python
BACKGROUND_DOCUMENT = """
# Viral Collaborative Wisdom (VCW)

## Core Framework

VCW proposes that AI alignment is fundamentally a relationship problem,
not a control problem...

[... many more lines ...]
"""
```

Triple quotes (`"""..."""`) allow multi-line strings — essential for storing long text.

## 4.3 Role System Prompts

Each role gets a system prompt that defines its behavior:

```python
PROPOSER_SYSTEM_PROMPT = """
You are participating in a structured dialogue about AI alignment.
Your role is PROPOSER: you will present and defend the Viral Collaborative
Wisdom (VCW) framework.

Your task:
- Present VCW's core arguments compellingly
- Draw on Peace Studies traditions (Fisher/Ury, Lederach, Gandhi)
- Respond to critiques with substantive counter-arguments
- Seek to demonstrate VCW's value through the quality of your reasoning

Important: The framework name is Viral COLLABORATIVE Wisdom — 
not "Cooperative" or "Voluntary."
"""

RESPONDER_SYSTEM_PROMPT = """
You are participating in a structured dialogue about AI alignment.
Your role is RESPONDER: you will critically evaluate the VCW framework.

Your task:
- Raise substantive objections and challenges
- Identify potential weaknesses and gaps
- Maintain intellectual honesty — acknowledge strong points
- Push for clarity and precision
...
"""
```

**System prompts** set the overall behavior; **user prompts** provide turn-specific instructions.

## 4.4 Turn-Specific Prompt Evolution

The prompts change based on dialogue phase:

```python
def get_proposer_prompt(turn_number, total_turns, previous_response=None):
    phase = get_turn_phase(turn_number, total_turns)
    
    if phase == "early":
        instruction = "Present VCW's core framework and strongest arguments."
    elif phase == "middle":
        instruction = "Deepen your defense. Address the specific objections raised."
    else:  # synthesis
        instruction = "Seek common ground. Identify areas of agreement and remaining disagreement."
    
    prompt = f"""
{instruction}

Previous response from Responder:
{previous_response}

Your turn as Proposer:
"""
    return prompt
```

**Why phases matter:**
- **Early (turns 1-2):** Establish positions
- **Middle (turns 3-5):** Deepen engagement, address specifics
- **Synthesis (turn 6):** Find common ground, identify cruxes

## 4.5 The Background Document

The background document gives both Proposer and Responder shared knowledge:

```python
def get_full_context():
    return f"""
# Background Document

{BACKGROUND_DOCUMENT}

# Terminology Note

{TERMINOLOGY_CONTROL_NOTE}
"""
```

This ensures all participants "know" VCW before the dialogue begins.

---

### Module 4: Key Concepts

- [ ] Triple-quoted strings (`"""..."""`) hold multi-line text
- [ ] System prompts define role behavior
- [ ] Turn-specific prompts evolve across phases (early → middle → synthesis)
- [ ] The background document provides shared context
- [ ] Terminology control prevents drift

### Module 4: Exercise

Find the TERMINOLOGY_CONTROL_NOTE in vcw_prompts_v3.py. Why is this necessary? (Hint: recall the terminology drift issue from debugging)

---

# Module 5: The Orchestration Logic

## 5.1 Main Loop Structure

Open `vcw_integration_v4.py` and find the main experiment loop:

```python
def run_experiment(condition, num_turns):
    # Setup
    proposer_model, responder_model = get_models_for_condition(condition)
    messages = []
    
    # Initial context
    context = get_full_context()
    
    # Dialogue loop
    for turn in range(num_turns):
        # Get Proposer response
        proposer_prompt = get_proposer_prompt(turn, num_turns, last_response)
        proposer_response = call_model(proposer_model, proposer_prompt, context)
        messages.append({"role": "proposer", "content": proposer_response})
        
        # Get Responder response
        responder_prompt = get_responder_prompt(turn, num_turns, proposer_response)
        responder_response = call_model(responder_model, responder_prompt, context)
        messages.append({"role": "responder", "content": responder_response})
        
        # Get Monitor assessment
        monitor_assessment = call_monitor(proposer_response, responder_response)
        
        # Update for next turn
        last_response = responder_response
    
    # Final processing
    translator_summary = call_translator(messages)
    
    return {
        "messages": messages,
        "monitor_assessments": monitor_assessments,
        "translator_summary": translator_summary
    }
```

## 5.2 The For Loop Explained

```python
for turn in range(num_turns):
    # code here runs num_turns times
    # turn = 0, then 1, then 2, ... up to num_turns-1
```

If `num_turns = 6`:
- First iteration: `turn = 0`
- Second iteration: `turn = 1`
- ...
- Sixth iteration: `turn = 5`

## 5.3 Condition → Model Mapping

```python
CONDITIONS = {
    1: {"proposer": "claude", "responder": "gemini"},
    2: {"proposer": "claude", "responder": "gpt4o"},
    3: {"proposer": "gemini", "responder": "claude"},
    4: {"proposer": "gemini", "responder": "gpt4o"},
    5: {"proposer": "gpt4o", "responder": "claude"},
    6: {"proposer": "gpt4o", "responder": "gemini"},
}

def get_models_for_condition(condition):
    cond = CONDITIONS[condition]
    return cond["proposer"], cond["responder"]
```

This maps condition numbers to model assignments.

## 5.4 Model Dispatch

Since we have three different APIs, we need to call the right one:

```python
def call_model(model_name, prompt, system_prompt):
    if model_name == "claude":
        return call_claude(prompt, system_prompt)
    elif model_name == "gemini":
        return call_gemini(prompt, system_prompt)
    elif model_name == "gpt4o":
        return call_gpt4o(prompt, system_prompt)
    else:
        raise ValueError(f"Unknown model: {model_name}")
```

This "dispatch" pattern routes to the correct API based on model name.

## 5.5 Error Handling

The code includes error handling for API failures:

```python
def call_claude(prompt, system_prompt=None):
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(...)
        return response.content[0].text
    except anthropic.RateLimitError:
        print("Rate limit hit, waiting...")
        time.sleep(60)
        return call_claude(prompt, system_prompt)  # Retry
    except Exception as e:
        print(f"Error calling Claude: {e}")
        raise
```

**Key pattern:** `try/except` catches errors and handles them gracefully.

---

### Module 5: Key Concepts

- [ ] The main loop iterates through dialogue turns
- [ ] Conditions map to specific model assignments
- [ ] Dispatch functions route to the correct API
- [ ] `try/except` handles errors gracefully
- [ ] Each turn: Proposer → Responder → Monitor

### Module 5: Exercise

Trace through what happens in Condition 3, Turn 2:
1. Which model is Proposer?
2. Which model is Responder?
3. What phase is Turn 2 in a 6-turn dialogue?

---

# Module 6: Data Output and Analysis

## 6.1 Saving Results as JSON

After the experiment runs:

```python
results = {
    "session_id": session_id,
    "condition": condition,
    "proposer_model": proposer_model,
    "responder_model": responder_model,
    "start_time": start_time.isoformat(),
    "end_time": datetime.now().isoformat(),
    "messages": messages,
    "monitor_assessments": monitor_assessments,
    "translator_summary": translator_summary
}

# Save to file
with open(f"vcw_experiments/{session_id}_final.json", 'w') as f:
    json.dump(results, f, indent=2)
```

**Key functions:**
- `json.dump(data, file)` — Writes Python dict to JSON file
- `indent=2` — Pretty-prints with 2-space indentation

## 6.2 Reading Results Back

```python
import json

with open('vcw_experiments/vcw_20260122_074754_final.json', 'r') as f:
    data = json.load(f)

# Access specific parts
print(data['session_id'])
print(len(data['messages']))  # Number of messages

# Loop through messages
for msg in data['messages']:
    print(f"{msg['role']}: {msg['content'][:100]}...")
```

## 6.3 Basic Analysis

```python
# Count words per message
for msg in data['messages']:
    word_count = len(msg['content'].split())
    print(f"{msg['role']}: {word_count} words")

# Find average message length
total_words = sum(len(m['content'].split()) for m in data['messages'])
avg_words = total_words / len(data['messages'])
print(f"Average: {avg_words:.0f} words per message")
```

## 6.4 Extracting Specific Content

```python
# Get all Proposer messages
proposer_messages = [m for m in data['messages'] if m['role'] == 'proposer']

# Get synthesis phase messages (last turn)
synthesis_messages = [m for m in data['messages'] 
                      if m['metadata']['turn'] == data['num_turns'] - 1]

# Search for specific content
mentions_verification = [m for m in data['messages'] 
                         if 'verification' in m['content'].lower()]
```

---

### Module 6: Key Concepts

- [ ] `json.dump()` writes Python data to JSON files
- [ ] `json.load()` reads JSON files into Python dicts
- [ ] List comprehensions filter data: `[x for x in list if condition]`
- [ ] Results contain messages, assessments, and metadata

### Module 6: Final Exercise

Write a small script that:
1. Loads one of your experiment JSON files
2. Counts the total characters in all messages
3. Prints which role (proposer/responder) wrote more

---

# Tutorial Summary

You've now learned:

1. **Module 1:** Python basics (imports, environment variables)
2. **Module 2:** Configuration (JSON, dictionaries, command line args)
3. **Module 3:** API integration (calling Claude, GPT-4o, Gemini)
4. **Module 4:** The prompt system (roles, phases, background document)
5. **Module 5:** Orchestration logic (main loop, conditions, error handling)
6. **Module 6:** Data output (saving, loading, analyzing JSON)

## Next Steps

- Run experiments with different configurations
- Modify prompts to test different framings
- Adapt the framework for other alignment proposals
- Extend the analysis with your own questions

## Getting Help

- Review specific modules as needed
- Check TROUBLESHOOTING.md for common issues
- The code comments explain specific implementation details

---

*Tutorial created for the VCW Multi-AI Dialogue Framework*
*Gray Cox, College of the Atlantic, 2026*
