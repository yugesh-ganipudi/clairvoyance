"""
Natural Cue Processor

A custom Pipecat processor that plays natural audio cues immediately after
user stops speaking (STT completes) to cover processing latency.
"""

from typing import List, Optional

from pipecat.frames.frames import (
    Frame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameProcessor

from app.ai.voice.agents.breeze_buddy.handlers.internal.natural_cues import (
    play_natural_cue,
)
from app.core.logger import logger


class NaturalCueProcessor(FrameProcessor):
    """
    Processor that plays natural audio cues when user stops speaking.

    This processor monitors for UserStoppedSpeakingFrame events and plays
    a random natural cue to provide conversational feedback while the LLM
    processes the user's input.
    """

    def __init__(self, transport, natural_cues: Optional[List[str]] = None, **kwargs):
        """
        Initialize the Natural Cue Processor.

        Args:
            transport: Pipecat transport for audio output
            natural_cues: List of audio cue filenames (e.g., ["hmm", "cough", "think"])
            **kwargs: Additional arguments passed to FrameProcessor
        """
        super().__init__(**kwargs)
        self._transport = transport
        self._natural_cues = natural_cues
        self._user_speaking = False
        self._last_played_cue: Optional[str] = None  # Track last played cue

        if natural_cues:
            logger.info(f"NaturalCueProcessor initialized with cues: {natural_cues}")
        else:
            logger.info("NaturalCueProcessor initialized but no cues configured")

    async def process_frame(self, frame: Frame, direction):
        """
        Process frames and play natural cues when user stops speaking.

        Args:
            frame: The frame to process
            direction: Direction of the frame flow
        """
        await super().process_frame(frame, direction)

        # Track when user starts speaking
        if isinstance(frame, UserStartedSpeakingFrame):
            self._user_speaking = True
            logger.debug("User started speaking")

        # Play natural cue when user stops speaking
        elif isinstance(frame, UserStoppedSpeakingFrame):
            if self._user_speaking:
                self._user_speaking = False
                logger.debug("User stopped speaking - playing natural cue")

                # Play the natural cue immediately (non-blocking)
                if self._natural_cues:
                    try:
                        played_cue = await play_natural_cue(
                            self._transport,
                            self._natural_cues,
                            exclude_cue=self._last_played_cue,
                        )
                        self._last_played_cue = played_cue  # Remember this cue
                    except Exception as e:
                        logger.error(f"Error playing natural cue: {e}", exc_info=True)

        # Pass the frame downstream
        await self.push_frame(frame, direction)
