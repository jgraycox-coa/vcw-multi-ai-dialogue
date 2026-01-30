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

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP.md](SETUP.md) | Step-by-step guide to setting up the framework from scratch |
| [CONFIGURATION.md](CONFIGURATION.md) | How to configure experiments and adapt for other frameworks |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [TUTORIAL.md](TUTORIAL.md) | 6-module tutorial for understanding the code |

**New to this framework?** Start with [SETUP.md](SETUP.md), then explore [TUTORIAL.md](TUTORIAL.md) to understand how the code works.

---

## Repository Structure

```
vcw-multi-ai-dialogue/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── vcw_integration_v4.py        # Main orchestration framework
├── SETUP.md                     # Setup guide
├── CONFIGURATION.md             # Configuration guide
├── TROUBLESHOOTING.md           # Troubleshooting guide
├── TUTORIAL.md                  # Code tutorial
├── prompts/
│   ├── vcw_prompts_v3.py        # Prompt generation module
│   ├── vcw_background_document.md  # VCW theoretical foundations
│   └── PROMPTS_OVERVIEW.md      # Prompt system documentation
├── data/
│   └── vcw_combined_dataset.json   # Complete experimental data
├── analysis/
│   └── analysis_results.md      # Summary statistics
└── docs/
    ├── full_dialogue_corpus.md  # Complete dialogue transcripts
    └── results_summary.md       # Results overview
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- API keys for Anthropic (Claude), Google (Gemini), and OpenAI (GPT-4o)

### Installation

```bash
git clone https://github.com/jgraycox-coa/vcw-multi-ai-dialogue.git
cd vcw-multi-ai-dialogue
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API keys:

```
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Running an Experiment

```bash
python vcw_integration_v4.py --condition 1 --turns 6
```

For detailed setup instructions, see [SETUP.md](SETUP.md).

---

## Methodology

The framework assigns four distinct roles to AI systems:

1. **Proposer**: Presents and defends an alignment framework
2. **Responder**: Critically evaluates the proposed framework
3. **Monitor**: Evaluates each exchange for argument quality
4. **Translator**: Produces plain-language summaries

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
- **Middle (Turns 3-5)**: Deepening engagement
- **Synthesis (Turn 6)**: Consolidation and common ground

---

## Key Findings

1. **Cross-Architecture Engagement**: All three AI architectures successfully engaged with complex Peace Studies concepts
2. **Complementary Critique**: Different architectures surface different objections (verification, scalability, bias)
3. **Dialogue Deepening**: 42% increase in message complexity from Early to Middle phase
4. **Emergent Synthesis**: Novel insights emerged through dialogue that neither party initially held

---

## Adapting for Other Alignment Frameworks

This methodology can be used to test alignment proposals other than VCW:

1. Modify `prompts/vcw_background_document.md` with your framework's foundations
2. Adjust prompts in `prompts/vcw_prompts_v3.py` to fit your framework
3. Run experiments across desired model combinations
4. Analyze results using provided data structures

For detailed instructions, see [CONFIGURATION.md](CONFIGURATION.md).

---

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

---

## License

MIT License - see LICENSE file for details.

---

## Acknowledgments

This research was conducted in collaboration with Claude (Anthropic), which contributed to experimental design, analysis, and manuscript preparation. The experimental framework orchestrated dialogues across Claude, Gemini (Google), and GPT-4o (OpenAI).
