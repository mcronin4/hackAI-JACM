from pydantic import BaseModel
from typing import Dict, Any


class PlatformConfig(BaseModel):
    """Base platform configuration"""
    character_limit: int
    max_hashtags: int
    supports_threads: bool = False
    supports_links: bool = True
    tone_guidelines: str = ""
    formatting_rules: Dict[str, Any] = {}


class TwitterConfig(PlatformConfig):
    """Twitter/X specific configuration"""
    character_limit: int = 280
    max_hashtags: int = 0
    supports_threads: bool = False  # Start with False, will expand later
    supports_links: bool = True
    tone_guidelines: str = "Engaging, conversational, and authentic. Use questions to drive engagement."
    formatting_rules: Dict[str, Any] = {
        "hashtag_placement": "end",  # hashtags at the end of the post
        "link_placement": "end",     # links at the end
        "max_content_length": 90,    # leave room for CTA and links (280 total - ~190 for other components, no hashtags)
        "call_to_action_style": "engaging_question"
    }


class LinkedInConfig(PlatformConfig):
    """LinkedIn configuration for future expansion"""
    character_limit: int = 3000
    max_hashtags: int = 5
    supports_threads: bool = False
    supports_links: bool = True
    tone_guidelines: str = "Professional, insightful, and thought-provoking."
    formatting_rules: Dict[str, Any] = {
        "hashtag_placement": "end",
        "link_placement": "end",
        "max_content_length": 2800,
        "call_to_action_style": "professional_insight"
    }


class PlatformConfigManager:
    """Manages platform configurations"""
    
    def __init__(self):
        self.configs = {
            "twitter": TwitterConfig(),
            "linkedin": LinkedInConfig(),
        }
    
    def get_config(self, platform: str) -> PlatformConfig:
        """Get configuration for a specific platform"""
        platform_lower = platform.lower()
        if platform_lower not in self.configs:
            raise ValueError(f"Unsupported platform: {platform}")
        return self.configs[platform_lower]
    
    def get_supported_platforms(self) -> list:
        """Get list of supported platforms"""
        return list(self.configs.keys())
    
    def is_platform_supported(self, platform: str) -> bool:
        """Check if a platform is supported"""
        return platform.lower() in self.configs 