# VCW Experimental Prompts Overview

This document summarizes the prompt structure used in the VCW Multi-AI Dialogue experiment.

## Files in this Directory

- `vcw_prompts_v3.py` - Complete Python module with all prompts and helper functions
- `vcw_background_document.md` - The 4,963-word theoretical foundations document (provided to all participants)

## Prompt Structure

### 1. Background Document Reference

All participants receive access to the Background Document, which includes:
- Part I: Why current alignment approaches fall short
- Part II: The dialogical reasoning alternative (MR vs DR)
- Part III: Key theoretical foundations (Fisher/Ury, Lederach, Gandhi, Ostrom, Sharp, Buber)
- Part IV-XI: VCW Elements, strategies, meta-reasoning, self-interest arguments, objections

**Critical Terminology Note:**
> The framework is "Viral COLLABORATIVE Wisdom" — not "Cooperative" or "Voluntary"

### 2. Role-Specific System Prompts

#### Proposer System Prompt
- Advocates for VCW framework
- Draws on Peace Studies, conflict transformation, dialogical reasoning
- Uses satyagraha methodology for value discovery
- Demonstrates meta-reasoning about value systems

#### Responder System Prompt
- Provides rigorous critique of VCW
- Identifies logical gaps, assumptions, failure modes
- Considers objections from multiple perspectives
- Engages honestly with strengths while probing weaknesses

#### Monitor System Prompt
- Evaluates each exchange along multiple dimensions
- Identifies dynamics and patterns
- Provides structured assessments

#### Translator System Prompt
- Produces accessible summaries for non-specialists
- Explains Peace Studies concepts
- Tracks dialogue progression

### 3. Turn-Specific Prompts

Prompts evolve through dialogue phases:

| Phase | Turns | Focus |
|-------|-------|-------|
| Early | 1-2 | Establish positions, initial critique |
| Middle | 3-5 | Deep mechanism exploration, specific objections |
| Synthesis | 6-8 | Seek common ground, identify remaining disagreements |
| Strategic | 9+ | Practical implications, adoption dynamics |

### 4. Key Prompt Elements

**For Proposers:**
- Interest Excavation Algorithm
- Satyagraha as empirical method
- Rooting vs. grounding distinction
- Meta-reasoning capability
- Responses to anticipated objections

**For Responders:**
- Engagement with Peace Studies claims
- Technical and philosophical objections
- Incentive analysis
- Minimum viable conditions
- Honest acknowledgment of strong arguments

## Customization Guide

To adapt these prompts for testing different alignment frameworks:

1. Replace `vcw_background_document.md` with your framework's foundations
2. Update terminology notes in `BACKGROUND_DOCUMENT_REFERENCE`
3. Modify `PROPOSER_INITIAL_VCW` with your framework's core presentation
4. Adjust responder critique templates to target your framework's specific claims
5. Keep the turn-specific evolution structure (early → middle → synthesis)

## Usage

```python
from vcw_prompts_v3 import get_prompts

# Get prompts for turn 3 of VCW condition
prompts = get_prompts('vcw', turn=3)

proposer_system = prompts['proposer_system']
responder_template = prompts['responder_template']
# etc.
```
