from pathlib import Path
import os
import logging
from typing import Dict, Any
from datetime import datetime
import time
import yt_dlp

from .transcription_service import TranscriptionService, TranscriptionError


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeConversionError(Exception):
    """Custom exception for YouTube conversion errors"""
    pass


class YouTubeService:
    """
    Service for converting YouTube videos to MP3 using the robust yt-dlp library.
    """

    def __init__(self, downloads_dir: str = None):
        """
        Initialize the YouTube service.
        """
        if downloads_dir:
            self.downloads_dir = downloads_dir
        else:
            # Assumes service is in app/services, puts downloads in backend/downloads
            backend_dir = Path(__file__).resolve().parents[2]
            self.downloads_dir = os.path.join(backend_dir, "downloads")
        
        os.makedirs(self.downloads_dir, exist_ok=True)
        logger.info(f"MP3 files will be saved to: {self.downloads_dir}")

    def _on_progress(self, d):
        """A hook for yt-dlp to report progress."""
        if d['status'] == 'downloading':
            # Log progress, but not too frequently
            percent = d.get('_percent_str', '0.0%').strip()
            # A bit of a hack to only log every ~10%
            if '.0' in percent or '.5' in percent:
                logger.info(
                    f"Downloading... {percent} of {d.get('_total_bytes_str', 'N/A')} at {d.get('_speed_str', 'N/A')}"
                )
        if d['status'] == 'finished':
            logger.info("Download finished. Post-processing (conversion) will start now...")

    def convert_to_mp3(self, url: str) -> Dict[str, Any]:
        """
        Downloads a YouTube video's audio and converts it to MP3 using yt-dlp.
        """
        start_time = time.time()
        
        output_template = os.path.join(self.downloads_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # Standard MP3 quality
            }],
            'outtmpl': output_template,
            'logger': logging.getLogger('yt_dlp'), # Use a dedicated logger
            'progress_hooks': [self._on_progress],
        }
        
        try:
            logger.info(f"Starting yt-dlp process for URL: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Construct the final mp3 filename based on the template
                mp3_filename = os.path.join(self.downloads_dir, f"{info['title']}.mp3")

                if not os.path.exists(mp3_filename):
                    raise YouTubeConversionError(
                        f"Conversion failed. Expected file not found at: {mp3_filename}"
                    )

                logger.info(f"Successfully processed video to {os.path.basename(mp3_filename)}")
                
                # Step 4: Transcribe the resulting MP3 file
                transcript = None
                try:
                    logger.info(f"Starting transcription for {os.path.basename(mp3_filename)}...")
                    transcription_service = TranscriptionService()
                    transcript = transcription_service.transcribe_audio(mp3_filename)
                    logger.info("Transcription successful.")
                except (ValueError, TranscriptionError) as e:
                    # If transcription fails (e.g., no API key), log it but don't fail the whole process
                    logger.warning(f"Could not transcribe audio: {e}")
                    # The process can continue, transcript will just be null.
                
                file_size = os.path.getsize(mp3_filename)
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "video_id": info.get("id"),
                    "video_title": info.get("title"),
                    "video_duration": info.get("duration"),
                    "audio_stream": {
                        "url": mp3_filename,
                        "format": "mp3",
                        "size": f"{file_size} bytes"
                    },
                    "transcript": transcript,
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat(),
                    "error": None
                }

        except Exception as e:
            logger.error(f"yt-dlp failed to convert video: {e}", exc_info=True)
            processing_time = time.time() - start_time
            return {
                "success": False,
                "video_id": None,
                "video_title": None,
                "audio_stream": None,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the YouTube service"""
        return {
            "service": "youtube-conversion (yt-dlp)",
            "status": "active",
            "dependencies": ["yt-dlp", "ffmpeg (system)", "deepgram-sdk"],
            "downloads_directory": self.downloads_dir,
            "timestamp": datetime.now().isoformat()
        }
