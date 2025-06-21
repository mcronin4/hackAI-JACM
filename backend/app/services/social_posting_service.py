import os
from typing import Dict, Any
from .social_media.platform_factory import PlatformFactory
from .social_media.base_platform import PostRequest, PostResult
from datetime import datetime

class SocialPostingService:
    def __init__(self):
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load credentials for all platforms from environment"""
        return {
            "twitter": {
                "api_key": os.getenv("TWITTER_API_KEY"),
                "api_secret": os.getenv("TWITTER_API_SECRET"),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
                "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
            },
            "linkedin": {
                "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN"),
                "person_id": os.getenv("LINKEDIN_PERSON_ID"),
            }
        }
    
    async def post_to_platform(self, platform_name: str, request: PostRequest) -> PostResult:
        """Post to a specific platform"""
        
        try:
            # Validate platform is supported
            if not PlatformFactory.is_supported(platform_name):
                return PostResult(
                    success=False,
                    platform=platform_name,
                    error=f"Platform '{platform_name}' is not supported",
                    posted_at=datetime.utcnow().isoformat()
                )
            
            # Get credentials
            platform_credentials = self.credentials.get(platform_name.lower())
            if not platform_credentials or not any(platform_credentials.values()):
                return PostResult(
                    success=False,
                    platform=platform_name,
                    error=f"No credentials configured for {platform_name}",
                    posted_at=datetime.utcnow().isoformat()
                )
            
            # Create platform instance
            platform = PlatformFactory.create_platform(platform_name, platform_credentials)
            
            # Verify credentials
            if not platform.verify_credentials():
                return PostResult(
                    success=False,
                    platform=platform_name,
                    error=f"Invalid credentials for {platform_name}",
                    posted_at=datetime.utcnow().isoformat()
                )
            
            # Post content
            return await platform.post(request)
            
        except Exception as e:
            return PostResult(
                success=False,
                platform=platform_name,
                error=f"Posting failed: {str(e)}",
                posted_at=datetime.utcnow().isoformat()
            )
    
    def get_platform_status(self, platform_name: str) -> Dict[str, Any]:
        """Get platform configuration status"""
        try:
            if not PlatformFactory.is_supported(platform_name):
                return {"supported": False, "configured": False}
            
            credentials = self.credentials.get(platform_name.lower())
            if not credentials or not any(credentials.values()):
                return {"supported": True, "configured": False, "error": "No credentials"}
            
            platform = PlatformFactory.create_platform(platform_name, credentials)
            return {
                "supported": True,
                "configured": True,
                "credentials_valid": platform.verify_credentials(),
                "character_limit": platform.get_character_limit()
            }
        except Exception as e:
            return {"supported": True, "configured": False, "error": str(e)}
    
    def get_all_platforms_status(self) -> Dict[str, Any]:
        """Get status for all supported platforms"""
        supported_platforms = PlatformFactory.get_supported_platforms()
        status = {}
        
        for platform in supported_platforms:
            status[platform] = self.get_platform_status(platform)
        
        return status 