from typing import Dict, List
from .base_platform import BaseSocialPlatform
from .twitter_platform import TwitterPlatform
from .linkedin_platform import LinkedInPlatform

class PlatformFactory:
    """Factory for creating social media platform instances"""
    
    _platforms = {
        "twitter": TwitterPlatform,
        "linkedin": LinkedInPlatform,
    }
    
    @classmethod
    def create_platform(
        cls, 
        platform_name: str, 
        credentials: Dict[str, str]
    ) -> BaseSocialPlatform:
        """Create a platform instance"""
        
        platform_class = cls._platforms.get(platform_name.lower())
        if not platform_class:
            raise ValueError(f"Unsupported platform: {platform_name}")
        
        return platform_class(credentials)
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """Get list of supported platforms"""
        return list(cls._platforms.keys())
    
    @classmethod
    def is_supported(cls, platform_name: str) -> bool:
        """Check if platform is supported"""
        return platform_name.lower() in cls._platforms
    
    @classmethod
    def register_platform(
        cls, 
        platform_name: str, 
        platform_class: type
    ):
        """Register a new platform (for extensibility)"""
        cls._platforms[platform_name.lower()] = platform_class 