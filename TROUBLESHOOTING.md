# Troubleshooting Guide: VCW Multi-AI Dialogue Framework

This guide addresses common issues encountered when running the experimental framework.

---

## API Issues

### Rate Limit Errors

**Symptoms:**
- "Rate limit exceeded" error
- "429 Too Many Requests"
- Experiment stops mid-run

**Solutions:**

1. **Add delays between API calls:**
   Edit `config.json`:
   ```json
   "delays": {
     "between_turns": 5,
     "between_api_calls": 2
   }
   ```

2. **Wait and retry:**
   Most rate limits reset within 1-5 minutes. Wait and run again.

3. **Use Claude as Monitor:**
   OpenAI and Gemini have stricter rate limits. Using Claude for Monitor role reduces calls to other APIs:
   ```json
   "monitor_model": "claude-sonnet-4-20250514"
   ```

4. **Run conditions sequentially:**
   Instead of `--all`, run one condition at a time with pauses between.

---

### API Key Errors

**Symptoms:**
- "Invalid API key"
- "Authentication failed"
- "API key not found"

**Solutions:**

1. **Check .env file location:**
   The `.env` file must be in the project root directory (same level as `vcw_integration_v4.py`).

2. **Check .env format:**
   ```
   # Correct
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   
   # Wrong (spaces around =)
   ANTHROPIC_API_KEY = sk-ant-xxxxx
   
   # Wrong (quotes around value)
   ANTHROPIC_API_KEY="sk-ant-xxxxx"
   ```

3. **Verify key is complete:**
   API keys are long. Make sure you copied the entire key.

4. **Check key permissions:**
   Some API keys have usage restrictions. Verify your key has permission for the models being used.

5. **Test keys individually:**
   ```bash
   # Test Anthropic
   python -c "import anthropic; print(anthropic.Anthropic().messages.create(model='claude-sonnet-4-20250514', max_tokens=10, messages=[{'role':'user','content':'hi'}]))"
   ```

---

### Model Not Available Errors

**Symptoms:**
- "Model not found"
- "Invalid model identifier"
- "Access denied for model"

**Solutions:**

1. **Check model names:**
   Model identifiers change. Verify current names:
   - Anthropic: https://docs.anthropic.com/en/docs/models
   - Google: https://ai.google.dev/models
   - OpenAI: https://platform.openai.com/docs/models

2. **Check account access:**
   Some models require specific account tiers or waitlist access.

3. **Update model names in config.json:**
   ```json
   "models": {
     "claude": "claude-sonnet-4-20250514",
     "gemini": "gemini-2.0-flash",
     "gpt4o": "gpt-4o"
   }
   ```

---

### Credit/Billing Errors

**Symptoms:**
- "Insufficient credits"
- "Billing limit reached"
- Experiment stops after a few turns

**Solutions:**

1. **Check account balance:**
   - Anthropic: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/usage
   - Google: https://console.cloud.google.com/billing

2. **Add credits:**
   Ensure your accounts have sufficient funds. A full experiment costs ~$20-50.

3. **Run shorter pilots:**
   Use `--turns 3` for testing to minimize costs.

---

## Experiment Issues

### Both Roles Critique Instead of One Defending

**Symptoms:**
- Proposer and Responder both criticize VCW
- No one defends the framework
- Dialogue feels one-sided

**Cause:** Prompt design issue — the Proposer prompt may not clearly instruct defense.

**Solution:**
Check `prompts/vcw_prompts_v3.py` and ensure PROPOSER_PROMPTS contain clear defense instructions:
```python
"You are defending the VCW framework. Present its strongest case..."
```

Not:
```python
"Engage critically with VCW..."  # This causes critiquing
```

---

### Terminology Drift

**Symptoms:**
- AI uses "Cooperative" instead of "Collaborative"
- Framework name changes throughout dialogue
- Inconsistent terminology

**Cause:** Without explicit guidance, models drift toward more common terms in training data.

**Solution:**
Ensure terminology control is present in all prompts:
```python
TERMINOLOGY_NOTE = """
Important: The framework name is Viral Collaborative Wisdom (VCW) — 
not "Cooperative" or "Voluntary." Please use this exact terminology.
"""
```

---

### Output Files Not Created

**Symptoms:**
- No files in `vcw_experiments/` directory
- "Permission denied" errors
- Directory doesn't exist

**Solutions:**

1. **Create the output directory:**
   ```bash
   mkdir -p vcw_experiments
   chmod 755 vcw_experiments
   ```

2. **Check write permissions:**
   ```bash
   ls -la vcw_experiments/
   ```

3. **Run from project root:**
   Make sure you're running from the correct directory:
   ```bash
   pwd  # Should show .../vcw-multi-ai-dialogue
   ```

---

### Incomplete Experiments

**Symptoms:**
- Only intermediate file, no final file
- Experiment stops mid-dialogue
- Partial results

**Causes:**
- API error during run
- Rate limit hit
- Network interruption

**Solutions:**

1. **Check intermediate file:**
   The `*_intermediate.json` contains partial results. You can inspect what completed.

2. **Review error logs:**
   Look at terminal output for specific error messages.

3. **Restart from last successful point:**
   If you know which turn failed, you may be able to resume manually (requires code modification).

4. **Re-run with increased delays:**
   Add more time between API calls to prevent rate limits.

---

## Environment Issues

### Virtual Environment Not Working

**Symptoms:**
- `(venv)` not appearing in prompt
- "Command not found: python"
- Wrong Python version being used

**Solutions:**

1. **Verify venv exists:**
   ```bash
   ls -la venv/
   ```

2. **Recreate if necessary:**
   ```bash
   rm -rf venv/
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Use explicit Python path:**
   ```bash
   ./venv/bin/python vcw_integration_v4.py --condition 1
   ```

---

### Package Import Errors

**Symptoms:**
- "ModuleNotFoundError: No module named 'xxx'"
- Import errors when running script

**Solutions:**

1. **Ensure venv is activated:**
   ```bash
   source venv/bin/activate
   ```

2. **Reinstall requirements:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.9+
   ```

---

## JSON/Data Issues

### JSON Parsing Errors

**Symptoms:**
- "JSONDecodeError"
- "Unexpected character"
- Can't read output files

**Causes:**
- API returned malformed response
- File was corrupted during write
- Encoding issues

**Solutions:**

1. **Validate JSON:**
   ```bash
   python -m json.tool vcw_experiments/your_file.json
   ```

2. **Check for truncation:**
   Open file in text editor and check if it ends properly with `}`.

3. **Look at intermediate file:**
   If final file is corrupted, intermediate may have valid partial data.

---

### Large Output Files

**Symptoms:**
- Files are very large (>100MB)
- Slow to open
- Memory issues when processing

**Solutions:**

1. **Use streaming JSON parser:**
   ```python
   import ijson
   with open('large_file.json', 'rb') as f:
       for item in ijson.items(f, 'messages.item'):
           process(item)
   ```

2. **Extract specific parts:**
   ```bash
   # Get just messages
   python -c "import json; d=json.load(open('file.json')); print(json.dumps(d['messages'], indent=2))"
   ```

---

## Getting Help

If you encounter an issue not covered here:

1. **Check the GitHub Issues:** https://github.com/jgraycox-coa/vcw-multi-ai-dialogue/issues

2. **Provide details when reporting:**
   - Error message (full text)
   - Command you ran
   - Python version (`python --version`)
   - Operating system
   - Relevant config.json settings

3. **Include minimal reproduction:**
   What's the simplest way to trigger the error?
