# VCW Multi-AI Dialogue Framework

A replicable framework for stress-testing AI alignment proposals through structured multi-model dialogue.

---

## 📄 Paper Now Available

**arXiv:** [http://arxiv.org/abs/2601.20604](http://arxiv.org/abs/2601.20604)

**Repository:** [https://github.com/jgraycox-coa/vcw-multi-ai-dialogue](https://github.com/jgraycox-coa/vcw-multi-ai-dialogue)

---

## Overview

This repository contains the complete experimental materials for the paper:

**"Dialogical Reasoning Across AI Architectures: A Multi-Model Framework for Testing AI Alignment Strategies"**

Gray Cox, College of the Atlantic (gcox@coa.edu)

## Repository Structure

```
vcw-multi-ai-dialogue/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── vcw_integration_v4.py        # Main orchestration framework
├── vcw_experiment_runner.py     # Experimental script
├── prompts/
│   ├── background_document.md   # VCW theoretical foundations (4,963 words)
│   ├── proposer_prompts.md      # Turn-specific proposer prompts
│   ├── responder_prompts.md     # Turn-specific responder prompts
│   ├── monitor_prompt.md        # Monitor assessment prompt
│   └── translator_prompt.md     # Translator summary prompt
├── data/
│   ├── condition_1_claude_gemini.json
│   ├── condition_2_claude_gpt4o.json
│   ├── condition_3_gemini_claude.json
│   ├── condition_4_gemini_gpt4o.json
│   ├── condition_5_gpt4o_claude.json
│   ├── condition_6_gpt4o_gemini.json
│   └── vcw_combined_dataset.json
├── analysis/
│   ├── analysis_notebook.ipynb  # Jupyter notebook for analysis
│   └── analysis_results.md      # Summary statistics
└── docs/
    ├── arxiv_paper.pdf          # Published paper
    └── full_dialogue_corpus.md  # Complete 305-page dialogue transcript
```

## Quick Start

### Prerequisites

- Python 3.9+
- API keys for:
  - Anthropic (Claude)
  - Google (Gemini)
  - OpenAI (GPT-4o)

### Installation

```bash
git clone https://github.com/jgraycox-coa/vcw-multi-ai-dialogue.git
cd vcw-multi-ai-dialogue
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API keys:

```
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Running the Experiment

```bash
python vcw_experiment_runner.py --condition 1 --output data/
```

## Methodology

The framework assigns four distinct roles to AI systems:

1. **Proposer**: Presents and defends an alignment framework
2. **Responder**: Critically evaluates the proposed framework
3. **Monitor** (Fixed as Claude): Evaluates each exchange
4. **Translator** (Fixed as Claude): Produces plain-language summaries

### Experimental Conditions

| Condition | Proposer | Responder |
|-----------|----------|-----------|
| 1 | Claude | Gemini |
| 2 | Claude | GPT-4o |
| 3 | Gemini | Claude |
| 4 | Gemini | GPT-4o |
| 5 | GPT-4o | Claude |
| 6 | GPT-4o | Gemini |

### Dialogue Phases

- **Early (Turns 1-2)**: Position establishment
- **Middle (Turns 3-5)**: Deepening engagement (+42% complexity)
- **Synthesis (Turn 6)**: Consolidation and hybrid proposals

## Key Findings

1. **Cross-Architecture Engagement**: All three AI architectures successfully engaged with complex Peace Studies concepts
2. **Complementary Critique**: Different architectures surface different objections (verification, scalability, bias)
3. **Dialogue Deepening**: 42% increase in message complexity from Early to Middle phase
4. **Terminology Control**: Explicit prompt guidance maintained 30:1 correct terminology ratio

## Adapting for Other Alignment Frameworks

To test a different alignment proposal:

1. Modify `prompts/background_document.md` with your framework's foundations
2. Adjust turn-specific prompts to fit your framework's terminology
3. Run experiments across desired model combinations
4. Analyze results using provided notebooks

## Citation

```bibtex
@article{cox2026dialogical,
  title={Dialogical Reasoning Across AI Architectures: A Multi-Model Framework for Testing AI Alignment Strategies},
  author={Cox, Gray},
  journal={arXiv preprint arXiv:2601.20604},
  year={2026},
  url={http://arxiv.org/abs/2601.20604}
}
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

This research was conducted in collaboration with Claude (Anthropic), which contributed to experimental design, analysis, and manuscript preparation.
