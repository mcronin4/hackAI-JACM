import sys
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the Python path to find the 'app' module
sys.path.append(str(Path(__file__).resolve().parent))

from app.services.youtube_service import YouTubeService

# Set up logging to be very verbose for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Runs a test of the yt-dlp based YouTube conversion and transcription service."""
    print("--- Starting YouTube Conversion & Transcription Test ---")
    
    # Check for Deepgram API Key
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("\n⚠️ WARNING: DEEPGRAM_API_KEY not found in environment variables.")
        print("   The test will proceed, but transcription is expected to fail.")
        print("   Add your key to the .env file to test transcription.")
    
    service = YouTubeService()
    
    status = service.get_service_status()
    print("\n📊 Service Status:")
    print(json.dumps(status, indent=2))

    # Using a short, public domain video with clear speech
    test_url = "https://www.youtube.com/watch?v=uw0IjQAtHWE" # Short inspirational speech
    
    print(f"\nAttempting to download, convert, and transcribe: {test_url}")
    
    result = service.convert_to_mp3(test_url)
    
    print("\n--- Test Result ---")
    print(json.dumps(result, indent=2, default=str))
    
    if result.get("success"):
        print("\n✅ Download and Conversion PASSED.")
        file_path = result['audio_stream']['url']
        print(f"File should be located at: {file_path}")
        if os.path.exists(file_path):
            print("✅ File verified to exist.")
        else:
            print("❌ File NOT found at the expected path!")
        
        # Verify transcription
        if result.get("transcript"):
            print("\n✅ Transcription PASSED.")
            print(f"   Transcript preview: \"{result['transcript'][:100]}...\"")
        else:
            print("\n❌ Transcription FAILED (or was skipped).")

    else:
        print("\n❌ Test FAILED.")
        print(f"Error: {result.get('error')}")
        print("\nTroubleshooting:")
        print("1. Check the logs above for specific error messages (e.g., from yt-dlp or Deepgram).")
        print("2. CRITICAL: Make sure `ffmpeg` is installed and accessible in your system's PATH.")
        print("3. Check your internet connection and Deepgram API key.")

if __name__ == "__main__":
    main() 