import os
import logging
import requests
import tempfile
import time
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
import json

logger = logging.getLogger(__name__)

"""
    description: Utilizes Deepgram API for trancription
    input: Audio file
    output: Transcript of the audio file
"""


class TranscriptionError(Exception):
    """Custom exception for transcription errors"""
    pass


class TranscriptionService:
    """
    Audio transcription service using multiple APIs.
    
    Supports:
    - OpenAI Whisper API
    - Google Speech-to-Text
    - AssemblyAI
    - RapidAPI transcription services
    """
    
    def __init__(self):
        """Initialize the transcription service with API configurations"""
        # OpenAI Whisper API
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Google Speech-to-Text
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # AssemblyAI
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
        
        # RapidAPI
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        
        # Check if at least one API is configured
        if not any([self.openai_api_key, self.google_api_key, self.assemblyai_api_key, self.rapidapi_key]):
            raise ValueError(
                "No transcription API keys found. Please configure at least one of: "
                "OPENAI_API_KEY, GOOGLE_API_KEY, ASSEMBLYAI_API_KEY, or RAPIDAPI_KEY"
            )
    
    def transcribe_with_openai(self, audio_file: BinaryIO, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper API.
        
        Args:
            audio_file: Audio file object
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.openai_api_key:
            raise TranscriptionError("OpenAI API key not configured")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            files = {
                "file": audio_file,
                "model": (None, "whisper-1"),
                "language": (None, language)
            }
            
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                timeout=60
            )
            
            if response.status_code != 200:
                raise TranscriptionError(f"OpenAI API error: {response.text}")
            
            data = response.json()
            
            return {
                "success": True,
                "text": data.get("text", ""),
                "language": language,
                "provider": "openai",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "language": language,
                "provider": "openai",
                "error": str(e)
            }
    
    def transcribe_with_google(self, audio_file: BinaryIO, language: str = "en-US") -> Dict[str, Any]:
        """
        Transcribe audio using Google Speech-to-Text API.
        
        Args:
            audio_file: Audio file object
            language: Language code (e.g., 'en-US', 'es-ES', 'fr-FR')
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.google_api_key:
            raise TranscriptionError("Google API key not configured")
        
        try:
            # Read audio file content
            audio_content = audio_file.read()
            
            # Encode as base64
            import base64
            audio_b64 = base64.b64encode(audio_content).decode('utf-8')
            
            url = f"https://speech.googleapis.com/v1/speech:recognize?key={self.google_api_key}"
            
            data = {
                "config": {
                    "encoding": "MP3",
                    "sampleRateHertz": 16000,
                    "languageCode": language,
                    "enableAutomaticPunctuation": True
                },
                "audio": {
                    "content": audio_b64
                }
            }
            
            response = requests.post(url, json=data, timeout=60)
            
            if response.status_code != 200:
                raise TranscriptionError(f"Google API error: {response.text}")
            
            result = response.json()
            
            # Extract transcription text
            transcript = ""
            if "results" in result:
                for res in result["results"]:
                    if "alternatives" in res and res["alternatives"]:
                        transcript += res["alternatives"][0]["transcript"] + " "
            
            return {
                "success": True,
                "text": transcript.strip(),
                "language": language,
                "provider": "google",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "language": language,
                "provider": "google",
                "error": str(e)
            }
    
    def transcribe_with_rapidapi(self, audio_file: BinaryIO, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio using RapidAPI transcription services.
        
        Args:
            audio_file: Audio file object
            language: Language code
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.rapidapi_key:
            raise TranscriptionError("RapidAPI key not configured")
        
        try:
            # Try multiple RapidAPI transcription endpoints
            endpoints = [
                {
                    "name": "speech_recognition",
                    "host": "speech-recognition-api.p.rapidapi.com",
                    "url": "https://speech-recognition-api.p.rapidapi.com/transcribe",
                    "files_key": "audio"
                },
                {
                    "name": "voice_recognition",
                    "host": "voice-recognition-api.p.rapidapi.com",
                    "url": "https://voice-recognition-api.p.rapidapi.com/transcribe",
                    "files_key": "file"
                }
            ]
            
            for endpoint in endpoints:
                try:
                    headers = {
                        "X-RapidAPI-Key": self.rapidapi_key,
                        "X-RapidAPI-Host": endpoint["host"]
                    }
                    
                    files = {
                        endpoint["files_key"]: audio_file
                    }
                    
                    data = {
                        "language": language
                    }
                    
                    response = requests.post(
                        endpoint["url"],
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Extract text from response (format may vary)
                        text = ""
                        if "text" in result:
                            text = result["text"]
                        elif "transcript" in result:
                            text = result["transcript"]
                        elif "result" in result:
                            text = result["result"]
                        
                        return {
                            "success": True,
                            "text": text,
                            "language": language,
                            "provider": f"rapidapi_{endpoint['name']}",
                            "error": None
                        }
                
                except Exception as e:
                    logger.warning(f"RapidAPI endpoint {endpoint['name']} failed: {str(e)}")
                    continue
            
            raise TranscriptionError("All RapidAPI transcription endpoints failed")
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "language": language,
                "provider": "rapidapi",
                "error": str(e)
            }
    
    def transcribe_audio(self, audio_file: BinaryIO, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio using the best available API.
        
        Args:
            audio_file: Audio file object
            language: Language code
            
        Returns:
            Dictionary containing transcription results
        """
        start_time = time.time()
        
        # Try APIs in order of preference
        apis_to_try = []
        
        if self.openai_api_key:
            apis_to_try.append(("openai", lambda: self.transcribe_with_openai(audio_file, language)))
        
        if self.google_api_key:
            apis_to_try.append(("google", lambda: self.transcribe_with_google(audio_file, language)))
        
        if self.rapidapi_key:
            apis_to_try.append(("rapidapi", lambda: self.transcribe_with_rapidapi(audio_file, language)))
        
        for api_name, api_func in apis_to_try:
            try:
                logger.info(f"Trying transcription with {api_name}")
                
                # Reset file pointer
                audio_file.seek(0)
                
                result = api_func()
                
                if result["success"]:
                    result["processing_time"] = time.time() - start_time
                    result["timestamp"] = datetime.now().isoformat()
                    logger.info(f"Successfully transcribed with {api_name}")
                    return result
                
            except Exception as e:
                logger.warning(f"API {api_name} failed: {str(e)}")
                continue
        
        # If all APIs failed
        processing_time = time.time() - start_time
        return {
            "success": False,
            "text": "",
            "language": language,
            "provider": "none",
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "error": "All transcription APIs failed"
        }
    
    def transcribe_from_url(self, audio_url: str, language: str = "en") -> Dict[str, Any]:
        """
        Download audio from URL and transcribe it.
        
        Args:
            audio_url: URL to the audio file
            language: Language code
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            # Download the audio file
            response = requests.get(audio_url, timeout=60)
            response.raise_for_status()
            
            # Create a temporary file-like object
            import io
            audio_file = io.BytesIO(response.content)
            
            # Transcribe the audio
            return self.transcribe_audio(audio_file, language)
            
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "language": language,
                "provider": "none",
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": f"Failed to download or transcribe audio: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the transcription service"""
        return {
            "service": "transcription",
            "status": "active",
            "apis_configured": {
                "openai": bool(self.openai_api_key),
                "google": bool(self.google_api_key),
                "assemblyai": bool(self.assemblyai_api_key),
                "rapidapi": bool(self.rapidapi_key)
            },
            "timestamp": datetime.now().isoformat()
        } 