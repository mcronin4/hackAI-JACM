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
        
        # Use default client - timeout is handled by httpx at the request level
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
            # Get file size for logging
            file_size = os.path.getsize(audio_file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            with open(audio_file_path, "rb") as audio_file:
                buffer_data = audio_file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            logger.info(f"Sending audio file '{os.path.basename(audio_file_path)}' ({file_size_mb:.1f} MB) to Deepgram for transcription...")
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
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                logger.error(f"Deepgram transcription timed out for {file_size_mb:.1f} MB file: {e}")
                raise TranscriptionError(f"Transcription timed out for large file ({file_size_mb:.1f} MB). Try with a shorter video or check your internet connection.")
            elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                logger.error(f"Deepgram API authentication failed: {e}")
                raise TranscriptionError("Transcription failed: Invalid or missing Deepgram API key. Please check your DEEPGRAM_API_KEY environment variable.")
            else:
                logger.error(f"Deepgram transcription failed: {e}", exc_info=True)
                raise TranscriptionError(f"Failed to transcribe audio file. Reason: {e}") 