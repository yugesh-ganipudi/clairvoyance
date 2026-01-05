-- Migration: Add natural_cues configuration support
-- Description:
--   Documents the natural_cues array in configurations JSONB column
--   Natural cues are audio files (e.g., "hmm", "cough") that play immediately 
--   after user stops speaking to cover STT and LLM processing latency

-- Add comment to document natural_cues configuration
COMMENT ON COLUMN template.configurations IS 'JSONB object containing template configurations:
- tts_voice_name: Voice for TTS (e.g., "rhea", "sara")
- stt_language: Language hints for STT (e.g., "en", "hi")
- payload_based_language_selection: Enable language detection from payload
- natural_cues: Array of audio cue names to play after user stops speaking (e.g., ["hmm", "cough", "think"])
  These cues play immediately after STT completes to provide natural interaction while LLM processes.
  Example: {"natural_cues": ["hmm", "cough", "ah"]}';

-- No schema changes needed as configurations is already JSONB
-- Merchants can now add natural_cues array to their template configurations
