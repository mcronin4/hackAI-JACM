from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin" 

class PostRequest(BaseModel):
    content: str
    thread_id: Optional[str] = None  # For replies/threading

class PostResult(BaseModel):
    success: bool
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    posted_at: str

class BaseSocialPlatform(ABC):
    """Abstract base class for all social media platforms"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.platform_name = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name"""
        pass
    
    @abstractmethod
    async def post(self, request: PostRequest) -> PostResult:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content for platform-specific requirements"""
        pass
    
    @abstractmethod
    def verify_credentials(self) -> bool:
        """Verify platform credentials are valid"""
        pass
    
    @abstractmethod
    def get_character_limit(self) -> int:
        """Get platform character limit"""
        pass 