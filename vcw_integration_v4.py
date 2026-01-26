"""
VCW Integration Script v4 - Rate Limit Resilient

ENHANCEMENTS from v3:
- Configurable delays between API calls to prevent rate limit issues
- Automatic retry with exponential backoff when rate limits are hit
- Optional context truncation for monitor to handle very long dialogues
- Robust error handling that saves progress before failing
- Support for very long runs (15, 25+ turns)

USAGE:
    python3.11 vcw_integration_v4.py test              # Test APIs
    python3.11 vcw_integration_v4.py run 6             # Run 6 turns
    python3.11 vcw_integration_v4.py run 15 --delay 5  # 15 turns with 5s delay
    python3.11 vcw_integration_v4.py info              # Show phase info

Author: VCW Experimental Framework
Date: January 2026
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Import the prompts library
try:
    import vcw_prompts_v3 as prompts
except ImportError:
    print("ERROR: vcw_prompts_v3.py not found!")
    print("Copy vcw_prompts_v3.py to your vcw-experiments directory.")
    sys.exit(1)

# Import the main framework
try:
    import vcw_experiment_framework as vcw
except ImportError:
    print("ERROR: vcw_experiment_framework.py not found!")
    sys.exit(1)


class RateLimitHandler:
    """Handles rate limiting with delays and retries."""
    
    def __init__(self, 
                 base_delay: float = 2.0,
                 max_retries: int = 5,
                 backoff_factor: float = 2.0,
                 max_delay: float = 120.0):
        """
        Initialize rate limit handler.
        
        Args:
            base_delay: Seconds to wait between normal API calls
            max_retries: Maximum retry attempts on rate limit
            backoff_factor: Multiply delay by this on each retry
            max_delay: Maximum delay between retries (seconds)
        """
        self.base_delay = base_delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.last_call_time = {}  # Track per-provider
    
    def wait_before_call(self, provider: str):
        """Wait appropriate time before making API call."""
        now = time.time()
        if provider in self.last_call_time:
            elapsed = now - self.last_call_time[provider]
            if elapsed < self.base_delay:
                wait_time = self.base_delay - elapsed
                vcw.logger.debug(f"Waiting {wait_time:.1f}s before {provider} call")
                time.sleep(wait_time)
        self.last_call_time[provider] = time.time()
    
    def call_with_retry(self, func, provider: str, *args, **kwargs):
        """
        Call function with automatic retry on rate limit errors.
        
        Args:
            func: Function to call
            provider: Provider name for logging ('anthropic', 'google', 'openai')
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Result of func call
            
        Raises:
            Exception after max_retries exhausted
        """
        self.wait_before_call(provider)
        
        last_error = None
        delay = self.base_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = any(term in error_str for term in [
                    'rate_limit', 'rate limit', '429', 'too many requests',
                    'tokens per min', 'tpm', 'quota', 'resource_exhausted'
                ])
                
                if is_rate_limit and attempt < self.max_retries:
                    last_error = e
                    wait_time = min(delay, self.max_delay)
                    vcw.logger.warning(
                        f"Rate limit hit for {provider}. "
                        f"Retry {attempt + 1}/{self.max_retries} in {wait_time:.1f}s"
                    )
                    time.sleep(wait_time)
                    delay *= self.backoff_factor
                else:
                    raise e
        
        raise last_error


class DialogueContextManager:
    """Manages dialogue context, including truncation for long runs."""
    
    def __init__(self, max_tokens_for_monitor: int = 25000):
        """
        Initialize context manager.
        
        Args:
            max_tokens_for_monitor: Approximate max tokens to send to monitor
                                   (helps avoid rate limits on long runs)
        """
        self.max_tokens_for_monitor = max_tokens_for_monitor
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (1 token ≈ 4 chars for English)."""
        return len(text) // 4
    
    def truncate_for_monitor(self, dialogue_history: str, 
                             keep_recent_turns: int = 3) -> str:
        """
        Truncate dialogue history for monitor if too long.
        
        Keeps the opening, first critique, and most recent N turns.
        
        Args:
            dialogue_history: Full dialogue history
            keep_recent_turns: Number of recent turns to always include
            
        Returns:
            Possibly truncated dialogue history
        """
        estimated_tokens = self.estimate_tokens(dialogue_history)
        
        if estimated_tokens <= self.max_tokens_for_monitor:
            return dialogue_history
        
        # Split into sections by role markers
        sections = []
        current_section = []
        
        for line in dialogue_history.split('\n'):
            if line.startswith('PROPOSER:') or line.startswith('RESPONDER:'):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        if len(sections) <= keep_recent_turns * 2 + 2:
            return dialogue_history
        
        # Keep opening (first 2 sections) and recent turns
        opening = sections[:2]
        recent = sections[-(keep_recent_turns * 2):]
        
        truncated = (
            '\n\n'.join(opening) +
            '\n\n[... Earlier exchanges omitted for brevity. ' +
            f'Showing opening and last {keep_recent_turns} turns ...]\n\n' +
            '\n\n'.join(recent)
        )
        
        vcw.logger.info(
            f"Truncated dialogue for monitor: {estimated_tokens} -> "
            f"{self.estimate_tokens(truncated)} estimated tokens"
        )
        
        return truncated


class VCWExperimentV4(vcw.VCWExperiment):
    """
    Enhanced experiment class with rate limit handling.
    
    Features:
    - Configurable delays between API calls
    - Automatic retry with exponential backoff
    - Context truncation for very long dialogues
    - Robust error handling with progress saving
    """
    
    def __init__(self, api_keys: dict, output_dir: str = "./vcw_experiments",
                 base_delay: float = 2.0, max_retries: int = 5):
        """
        Initialize experiment with rate limiting.
        
        Args:
            api_keys: API credentials
            output_dir: Output directory
            base_delay: Seconds between API calls (increase for long runs)
            max_retries: Max retries on rate limit
        """
        super().__init__(api_keys, output_dir)
        self.rate_handler = RateLimitHandler(
            base_delay=base_delay,
            max_retries=max_retries
        )
        self.context_manager = DialogueContextManager()
    
    def _get_provider(self, model: str) -> str:
        """Determine provider from model name."""
        if 'claude' in model.lower():
            return 'anthropic'
        elif 'gemini' in model.lower():
            return 'google'
        elif 'gpt' in model.lower():
            return 'openai'
        return 'unknown'
    
    def _get_response_with_retry(self, model: str, prompt: str, 
                                  system_prompt: str = None,
                                  max_tokens: int = 4000,
                                  temperature: float = 0.7) -> str:
        """Get AI response with rate limit handling."""
        provider = self._get_provider(model)
        
        return self.rate_handler.call_with_retry(
            self.ai_interface.get_response,
            provider,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def _get_prompts_for_condition(self, condition: str, turn: int = 1) -> dict:
        """Get prompts for condition with turn number."""
        return prompts.get_prompts(condition, turn)
    
    def run_dialogue_session(self,
                            condition: str,
                            proposer_model: str,
                            responder_model: str,
                            monitor_model: str,
                            translator_model: str,
                            num_turns: int = 3,
                            save_intermediate: bool = True,
                            truncate_monitor_context: bool = True):
        """
        Run dialogue session with rate limit handling.
        
        Args:
            condition: Experimental condition
            proposer_model, responder_model, monitor_model, translator_model: Models
            num_turns: Number of dialogue turns
            save_intermediate: Save after each turn
            truncate_monitor_context: Truncate context sent to monitor for long runs
            
        Returns:
            DialogueSession object (may be partial if interrupted)
        """
        session_id = f"vcw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        vcw.logger.info(f"Starting V4 session {session_id} with {num_turns} turns")
        vcw.logger.info(f"Rate limit handling: {self.rate_handler.base_delay}s delay, "
                       f"{self.rate_handler.max_retries} max retries")
        
        session = vcw.DialogueSession(
            session_id=session_id,
            condition=condition,
            proposer_model=proposer_model,
            responder_model=responder_model,
            monitor_model=monitor_model,
            translator_model=translator_model,
            messages=[],
            monitor_assessments=[],
            human_summaries=[],
            start_time=datetime.now().isoformat()
        )
        
        try:
            # Get initial prompts
            current_prompts = self._get_prompts_for_condition(condition, turn=1)
            
            # Opening statement
            vcw.logger.info("Turn 0: Proposer opening statement")
            proposer_response = self._get_response_with_retry(
                model=proposer_model,
                prompt=current_prompts['proposer_initial'],
                system_prompt=current_prompts['proposer_system']
            )
            
            session.messages.append(vcw.Message(
                role='proposer',
                model=proposer_model,
                content=proposer_response,
                timestamp=datetime.now().isoformat(),
                metadata={'turn': 0, 'type': 'opening', 'phase': 'early'}
            ))
            
            # Main dialogue loop
            for turn in range(1, num_turns + 1):
                phase = prompts.get_turn_phase(turn)
                vcw.logger.info(f"Turn {turn} ({phase} phase) beginning")
                
                # Get turn-specific prompts
                current_prompts = self._get_prompts_for_condition(condition, turn=turn)
                
                # Responder
                dialogue_history = self._format_dialogue_history(session.messages)
                responder_response = self._get_response_with_retry(
                    model=responder_model,
                    prompt=current_prompts['responder_template'].format(
                        dialogue_history=dialogue_history,
                        turn=turn
                    ),
                    system_prompt=current_prompts['responder_system']
                )
                
                session.messages.append(vcw.Message(
                    role='responder',
                    model=responder_model,
                    content=responder_response,
                    timestamp=datetime.now().isoformat(),
                    metadata={'turn': turn, 'type': 'response', 'phase': phase}
                ))
                
                # Monitor (with optional context truncation)
                monitor_assessment = self._conduct_monitoring_v4(
                    session, monitor_model, current_prompts, turn, phase,
                    truncate_context=truncate_monitor_context
                )
                session.monitor_assessments.append(monitor_assessment)
                
                # Proposer rebuttal (except on last turn)
                if turn < num_turns:
                    dialogue_history = self._format_dialogue_history(session.messages)
                    proposer_response = self._get_response_with_retry(
                        model=proposer_model,
                        prompt=current_prompts['proposer_followup'].format(
                            dialogue_history=dialogue_history,
                            critique=responder_response,
                            turn=turn
                        ),
                        system_prompt=current_prompts['proposer_system']
                    )
                    
                    session.messages.append(vcw.Message(
                        role='proposer',
                        model=proposer_model,
                        content=proposer_response,
                        timestamp=datetime.now().isoformat(),
                        metadata={'turn': turn, 'type': 'rebuttal', 'phase': phase}
                    ))
                
                # Translator summary
                human_summary = self._generate_human_summary_v4(
                    session, translator_model, current_prompts, turn, phase,
                    truncate_context=truncate_monitor_context
                )
                session.human_summaries.append(human_summary)
                
                # Save intermediate
                if save_intermediate:
                    self._save_session(session, intermediate=True)
                
                vcw.logger.info(f"Turn {turn} ({phase} phase) completed")
            
            # Final save
            session.end_time = datetime.now().isoformat()
            self._save_session(session, intermediate=False)
            vcw.logger.info(f"Session {session_id} completed successfully")
            
        except Exception as e:
            vcw.logger.error(f"Session interrupted: {e}")
            vcw.logger.info("Saving progress before exit...")
            session.end_time = datetime.now().isoformat()
            self._save_session(session, intermediate=True)
            vcw.logger.info(f"Partial session saved: {session_id}_intermediate.json")
            raise
        
        return session
    
    def _conduct_monitoring_v4(self, session, monitor_model, current_prompts, 
                               turn, phase, truncate_context=True):
        """Monitor with optional context truncation."""
        dialogue_history = self._format_dialogue_history(session.messages)
        
        # Truncate if needed for long dialogues
        if truncate_context:
            dialogue_history = self.context_manager.truncate_for_monitor(
                dialogue_history, keep_recent_turns=3
            )
        
        if turn == 1:
            criteria_response = self._get_response_with_retry(
                model=monitor_model,
                prompt=current_prompts['monitor_criteria_establishment'].format(
                    dialogue_history=dialogue_history
                ),
                system_prompt=current_prompts['monitor_system']
            )
            
            return {
                'turn': turn,
                'phase': phase,
                'type': 'criteria_establishment',
                'criteria': criteria_response,
                'timestamp': datetime.now().isoformat()
            }
        else:
            phase_guidance = current_prompts.get('monitor_phase_guidance', '')
            
            evaluation_prompt = current_prompts['monitor_evaluation_template'].format(
                dialogue_history=dialogue_history,
                turn=turn,
                phase_specific_guidance=phase_guidance
            )
            
            evaluation_response = self._get_response_with_retry(
                model=monitor_model,
                prompt=evaluation_prompt,
                system_prompt=current_prompts['monitor_system']
            )
            
            return {
                'turn': turn,
                'phase': phase,
                'type': 'evaluation',
                'evaluation': evaluation_response,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_human_summary_v4(self, session, translator_model, current_prompts,
                                   turn, phase, truncate_context=True):
        """Generate summary with optional context truncation."""
        dialogue_history = self._format_dialogue_history(session.messages)
        
        if truncate_context:
            dialogue_history = self.context_manager.truncate_for_monitor(
                dialogue_history, keep_recent_turns=3
            )
        
        monitor_history = self._format_monitor_history(session.monitor_assessments)
        phase_description = prompts.get_translator_phase_description(turn)
        
        summary_prompt = current_prompts['translator_template'].format(
            dialogue_history=dialogue_history,
            monitor_history=monitor_history,
            turn=turn,
            phase_description=phase_description
        )
        
        return self._get_response_with_retry(
            model=translator_model,
            prompt=summary_prompt,
            system_prompt=current_prompts['translator_system']
        )
    
    def _format_monitor_history(self, assessments):
        """Format monitor assessments for translator."""
        if not assessments:
            return "No monitor assessments yet."
        
        formatted = []
        for a in assessments:
            if a['type'] == 'criteria_establishment':
                formatted.append(f"Turn {a['turn']} (Criteria): {a['criteria'][:500]}...")
            else:
                formatted.append(f"Turn {a['turn']} ({a['phase']} phase): {a['evaluation'][:500]}...")
        
        return "\n\n".join(formatted)


def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)


def test_api_connections(config: dict) -> bool:
    """Test API connections."""
    api_keys = config.get('api_keys', {})
    
    print("Testing API connections...")
    
    try:
        ai = vcw.AIInterface(api_keys)
        
        print("  Testing Claude...", end=" ", flush=True)
        response = ai.get_response(
            model="claude-sonnet-4-20250514",
            prompt="Say 'Claude OK' in exactly two words.",
            max_tokens=10
        )
        print(f"✓ ({response.strip()[:20]})")
        
        time.sleep(1)  # Small delay between tests
        
        print("  Testing Gemini...", end=" ", flush=True)
        response = ai.get_response(
            model="gemini-2.0-flash",
            prompt="Say 'Gemini OK' in exactly two words.",
            max_tokens=10
        )
        print(f"✓ ({response.strip()[:20]})")
        
        time.sleep(1)
        
        print("  Testing OpenAI...", end=" ", flush=True)
        response = ai.get_response(
            model="gpt-4o",
            prompt="Say 'GPT OK' in exactly two words.",
            max_tokens=10
        )
        print(f"✓ ({response.strip()[:20]})")
        
        print("\nAll APIs working!")
        return True
        
    except Exception as e:
        print(f"\n✗ API test failed: {e}")
        return False


def run_experiment(config: dict, num_turns: int, base_delay: float, 
                   max_retries: int, truncate: bool) -> None:
    """Run experiment with specified parameters."""
    api_keys = config.get('api_keys', {})
    models = config.get('model_combinations', [{}])[0]
    
    print(f"\n{'='*60}")
    print("VCW EXPERIMENT - V4 WITH RATE LIMIT HANDLING")
    print(f"{'='*60}")
    print(f"Turns: {num_turns}")
    print(f"Base delay between calls: {base_delay}s")
    print(f"Max retries on rate limit: {max_retries}")
    print(f"Truncate context for long runs: {truncate}")
    print(f"Phase evolution: early(1-2) → middle(3-5) → synthesis(6-8) → strategic(9+)")
    print(f"\nModels:")
    print(f"  Proposer:   {models.get('proposer', 'claude-sonnet-4-20250514')}")
    print(f"  Responder:  {models.get('responder', 'gemini-2.0-flash')}")
    print(f"  Monitor:    {models.get('monitor', 'gpt-4o')}")
    print(f"  Translator: {models.get('translator', 'claude-sonnet-4-20250514')}")
    
    # Estimate runtime
    estimated_minutes = num_turns * 2 * (1 + base_delay / 60)  # Rough estimate
    print(f"\nEstimated runtime: {estimated_minutes:.0f}-{estimated_minutes*1.5:.0f} minutes")
    print(f"{'='*60}\n")
    
    experiment = VCWExperimentV4(
        api_keys, 
        base_delay=base_delay,
        max_retries=max_retries
    )
    
    try:
        session = experiment.run_dialogue_session(
            condition='vcw',
            proposer_model=models.get('proposer', 'claude-sonnet-4-20250514'),
            responder_model=models.get('responder', 'gemini-2.0-flash'),
            monitor_model=models.get('monitor', 'gpt-4o'),
            translator_model=models.get('translator', 'claude-sonnet-4-20250514'),
            num_turns=num_turns,
            save_intermediate=True,
            truncate_monitor_context=truncate
        )
        
        print(f"\n{'='*60}")
        print(f"EXPERIMENT COMPLETE: {session.session_id}")
        print(f"{'='*60}")
        print(f"Messages: {len(session.messages)}")
        print(f"Monitor assessments: {len(session.monitor_assessments)}")
        print(f"Output: vcw_experiments/{session.session_id}_final.json")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"EXPERIMENT INTERRUPTED")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"Partial results saved to vcw_experiments/")
        print(f"You can resume or analyze partial results.")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='VCW Multi-AI Dialogue Experiments (v4 - Rate Limit Resilient)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3.11 vcw_integration_v4.py test              # Test API connections
  python3.11 vcw_integration_v4.py run 6             # Run 6 turns (default settings)
  python3.11 vcw_integration_v4.py run 10 --delay 5  # 10 turns with 5s delay
  python3.11 vcw_integration_v4.py run 25 --delay 10 # Long run with 10s delay
  python3.11 vcw_integration_v4.py info              # Show phase information

Recommended delays by run length:
  3-6 turns:   2s delay (default)
  6-10 turns:  5s delay
  10-15 turns: 8s delay
  15+ turns:   10-15s delay
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test API connections')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run dialogue experiment')
    run_parser.add_argument('turns', type=int, help='Number of dialogue turns')
    run_parser.add_argument('--delay', type=float, default=2.0,
                           help='Seconds between API calls (default: 2.0)')
    run_parser.add_argument('--retries', type=int, default=5,
                           help='Max retries on rate limit (default: 5)')
    run_parser.add_argument('--no-truncate', action='store_true',
                           help='Disable context truncation for monitor')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show phase information')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    if args.command == 'info':
        print("VCW v4 Prompt Phase Structure:")
        print("="*50)
        print("\nPhase       Turns    Focus")
        print("-"*50)
        print("Early       1-2      Establish positions, initial critique")
        print("Middle      3-5      Deep engagement with mechanisms")
        print("Synthesis   6-8      Seek common ground, identify gaps")
        print("Strategic   9+       Practical implications, adoption dynamics")
        print("\nRate Limit Handling:")
        print("-"*50)
        print("- Configurable delays between API calls")
        print("- Automatic retry with exponential backoff")
        print("- Context truncation for very long dialogues")
        print("- Progress saved on interruption")
        return
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        print("ERROR: config.json not found!")
        print("Make sure you're in the vcw-experiments directory.")
        return
    
    if args.command == 'test':
        test_api_connections(config)
    
    elif args.command == 'run':
        # Verify APIs first
        if not test_api_connections(config):
            print("\nFix API issues before running experiment.")
            return
        
        run_experiment(
            config,
            num_turns=args.turns,
            base_delay=args.delay,
            max_retries=args.retries,
            truncate=not args.no_truncate
        )


if __name__ == "__main__":
    main()
