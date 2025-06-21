import os
import logging
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TranscriptionError(Exception):
    """Custom exception for transcription errors."""
    pass

class TranscriptionService:
    """
    A service for transcribing audio files using the Deepgram API.
    """
    def __init__(self):
        """Initializes the TranscriptionService."""
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables.")
        self.deepgram_client = DeepgramClient(self.api_key)

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribes the given audio file and returns the transcript.

        Args:
            audio_file_path: The local path to the audio file (e.g., MP3).

        Returns:
            The full transcript as a single string.
            
        Raises:
            TranscriptionError: If the transcription process fails.
        """
        if not os.path.exists(audio_file_path):
            raise TranscriptionError(f"Audio file not found at path: {audio_file_path}")

        try:
            with open(audio_file_path, "rb") as audio_file:
                buffer_data = audio_file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            logger.info(f"Sending audio file '{os.path.basename(audio_file_path)}' to Deepgram for transcription...")
            # Using the 'nova-2' model for high accuracy
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
            )

            response = self.deepgram_client.listen.prerecorded.v("1").transcribe_file(payload, options)
            
            transcript = response.results.channels[0].alternatives[0].transcript
            
            logger.info("Successfully received transcript from Deepgram.")
            return transcript

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}", exc_info=True)
            raise TranscriptionError(f"Failed to transcribe audio file. Reason: {e}") 