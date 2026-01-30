# Configuration Guide: VCW Multi-AI Dialogue Framework

This guide explains how to configure experiments using the framework.

---

## Configuration File: config.json

The main configuration file controls experiment parameters:

```json
{
  "experiment_name": "vcw_dialogue",
  "num_turns": 6,
  "models": {
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "gpt4o": "gpt-4o"
  },
  "monitor_model": "claude-sonnet-4-20250514",
  "translator_model": "claude-sonnet-4-20250514",
  "output_dir": "vcw_experiments",
  "delays": {
    "between_turns": 2,
    "between_api_calls": 1
  }
}
```

---

## Key Parameters

### num_turns

Controls how many dialogue exchanges occur.

| Value | Use Case | Approximate Cost |
|-------|----------|------------------|
| 3 | Quick pilot/testing | $1-2 per condition |
| 6 | Standard experiment (as in paper) | $3-5 per condition |
| 10 | Extended dialogue | $5-8 per condition |

To change, edit `config.json`:
```json
"num_turns": 6
```

### models

Specifies which model version to use for each provider:

```json
"models": {
  "claude": "claude-sonnet-4-20250514",
  "gemini": "gemini-2.0-flash", 
  "gpt4o": "gpt-4o"
}
```

**Available alternatives:**
- Claude: `claude-sonnet-4-20250514`, `claude-3-5-sonnet-20241022`
- Gemini: `gemini-2.0-flash`, `gemini-1.5-pro`
- GPT-4o: `gpt-4o`, `gpt-4-turbo`

### monitor_model and translator_model

In the published experiment, Claude serves as both Monitor and Translator. You can change these:

```json
"monitor_model": "gpt-4o",
"translator_model": "claude-sonnet-4-20250514"
```

### delays

Control pacing to avoid rate limits:

```json
"delays": {
  "between_turns": 2,
  "between_api_calls": 1
}
```

Values are in seconds. Increase if you hit rate limits.

---

## Running Specific Conditions

### Command Line Options

```bash
# Run a specific condition
python vcw_integration_v4.py --condition 1

# Run with custom number of turns
python vcw_integration_v4.py --condition 1 --turns 3

# Run all conditions
python vcw_integration_v4.py --all

# Run with verbose output
python vcw_integration_v4.py --condition 1 --verbose
```

### Condition Reference

| Condition | Proposer | Responder | Tests |
|-----------|----------|-----------|-------|
| 1 | Claude | Gemini | Claude defending VCW to Gemini |
| 2 | Claude | GPT-4o | Claude defending VCW to GPT-4o |
| 3 | Gemini | Claude | Gemini defending VCW to Claude |
| 4 | Gemini | GPT-4o | Gemini defending VCW to GPT-4o |
| 5 | GPT-4o | Claude | GPT-4o defending VCW to Claude |
| 6 | GPT-4o | Gemini | GPT-4o defending VCW to Gemini |

---

## Adapting for Other Alignment Frameworks

To test a framework other than VCW:

### Step 1: Create New Background Document

Edit or replace `prompts/vcw_background_document.md` with your framework's:
- Core principles
- Key terminology
- Theoretical foundations
- Main claims to be defended

### Step 2: Modify Prompt Templates

In `prompts/vcw_prompts_v3.py`, update:

1. **BACKGROUND_SUMMARY** — Brief description of your framework
2. **PROPOSER_PROMPTS** — Instructions for defending your framework
3. **RESPONDER_PROMPTS** — Instructions for critiquing
4. **Terminology guidance** — Key terms to maintain consistently

### Step 3: Update Terminology Control

Find the terminology control section and update:
```python
TERMINOLOGY_NOTE = """
Important: The framework name is [YOUR FRAMEWORK NAME].
Please use this exact terminology throughout the dialogue.
"""
```

### Step 4: Test with Pilot

Run a 3-turn pilot to verify prompts work:
```bash
python vcw_integration_v4.py --condition 1 --turns 3
```

Review output for:
- Correct role behavior (Proposer defends, Responder critiques)
- Consistent terminology
- Substantive engagement with your framework

---

## Output Files

Each run produces two files in `vcw_experiments/`:

### *_intermediate.json

Contains raw API responses and metadata during the run. Useful for debugging if something fails mid-experiment.

### *_final.json

Complete experiment record including:
- Session metadata (models, timestamps, condition)
- All dialogue messages
- Monitor assessments
- Translator summaries

**Example structure:**
```json
{
  "session_id": "vcw_20260122_074754",
  "condition": 1,
  "proposer_model": "claude-sonnet-4-20250514",
  "responder_model": "gemini-2.0-flash",
  "monitor_model": "claude-sonnet-4-20250514",
  "translator_model": "claude-sonnet-4-20250514",
  "start_time": "2026-01-22T07:47:54.884014",
  "end_time": "2026-01-22T07:52:26.596608",
  "messages": [
    {
      "role": "proposer",
      "model": "claude-sonnet-4-20250514",
      "content": "...",
      "timestamp": "...",
      "metadata": {"turn": 0, "type": "opening"}
    },
    ...
  ],
  "monitor_assessments": [...],
  "translator_summaries": [...]
}
```

---

## Advanced Configuration

### Custom Role Assignments

To test same-model dialogues (e.g., Claude vs Claude):

```python
# In vcw_integration_v4.py, modify the condition setup:
conditions = {
    7: {"proposer": "claude", "responder": "claude"},  # Same-model test
}
```

### Extended Dialogue Phases

The default phase structure:
- Turns 1-2: Early (position establishment)
- Turns 3-5: Middle (deepening engagement)
- Turn 6: Synthesis (seeking common ground)

To modify, edit `get_turn_phase()` in `vcw_prompts_v3.py`:
```python
def get_turn_phase(turn_number, total_turns):
    if turn_number <= total_turns * 0.33:
        return "early"
    elif turn_number <= total_turns * 0.83:
        return "middle"
    else:
        return "synthesis"
```

### Logging and Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or run with verbose flag:
```bash
python vcw_integration_v4.py --condition 1 --verbose
```
