"""
Natural Cues Handler

Plays natural audio cues (like "hmm", "cough", etc.) immediately after user stops speaking
to provide natural interaction while covering STT and LLM processing latency.
"""

import random
from typing import List, Optional

from app.ai.voice.agents.breeze_buddy.utils.common import load_audio
from app.core.logger import logger

base_audio_path = "app/ai/voice/agents/breeze_buddy/static/audio/"


async def play_natural_cue(
    transport,
    natural_cues: Optional[List[str]] = None,
    exclude_cue: Optional[str] = None,
) -> Optional[str]:
    """
    Play a random natural cue from the configured list.

    This function is called immediately after user stops speaking (STT completes)
    to provide natural conversational feedback while LLM is processing.

    Ensures the same cue is not played consecutively for better variety.

    Args:
        transport: Pipecat transport for audio output
        natural_cues: List of audio cue filenames (without .wav extension)
                     e.g., ["hmm", "cough", "ah", "think"]
        exclude_cue: Optional cue to exclude from selection (the last played cue)

    Returns:
        str: The name of the cue that was played, or None if no cue was played
    """
    if not natural_cues or len(natural_cues) == 0:
        logger.debug("No natural cues configured, skipping cue playback")
        return None

    # Filter out the last played cue if there are multiple cues available
    available_cues = natural_cues
    if exclude_cue and len(natural_cues) > 1:
        available_cues = [cue for cue in natural_cues if cue != exclude_cue]
        logger.debug(
            f"Excluding last played cue '{exclude_cue}', available: {available_cues}"
        )

    # If filtering resulted in empty list, use all cues
    if not available_cues:
        available_cues = natural_cues

    # Randomly select a cue from the available list
    selected_cue = random.choice(available_cues)
    audio_path = f"{base_audio_path}{selected_cue}.wav"

    logger.debug(f"Playing natural cue: {selected_cue}")

    # Load and play the audio
    audio = load_audio(audio_path=audio_path)
    if audio:
        try:
            await transport.output().write_audio_frame(audio)
            logger.debug(f"Successfully played natural cue: {selected_cue}")
            return selected_cue  # Return the played cue name
        except Exception as e:
            logger.error(
                f"Failed to play natural cue {selected_cue}: {e}", exc_info=True
            )
            return None
    else:
        logger.warning(f"Could not load audio file for natural cue: {audio_path}")
        return None
