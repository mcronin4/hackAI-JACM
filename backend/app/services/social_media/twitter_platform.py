import tweepy
from datetime import datetime
from typing import Dict, Any
from .base_platform import BaseSocialPlatform, PostRequest, PostResult

class TwitterPlatform(BaseSocialPlatform):
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.client = tweepy.Client(
            bearer_token=credentials.get("bearer_token"),
            consumer_key=credentials.get("api_key"),
            consumer_secret=credentials.get("api_secret"),
            access_token=credentials.get("access_token"),
            access_token_secret=credentials.get("access_token_secret"),
            wait_on_rate_limit=True
        )
    
    def get_platform_name(self) -> str:
        return "twitter"
    
    async def post(self, request: PostRequest) -> PostResult:
        try:
            # Validate content
            validation = self.validate_content(request.content)
            if not validation["valid"]:
                return PostResult(
                    success=False,
                    platform=self.platform_name,
                    error=validation["error"],
                    posted_at=datetime.utcnow().isoformat()
                )
            
            # Post to Twitter
            response = self.client.create_tweet(
                text=request.content,
                in_reply_to_tweet_id=request.thread_id
            )
            
            tweet_id = response.data['id']
            username = self._get_username()
            
            return PostResult(
                success=True,
                platform=self.platform_name,
                post_id=tweet_id,
                post_url=f"https://twitter.com/{username}/status/{tweet_id}",
                posted_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            return PostResult(
                success=False,
                platform=self.platform_name,
                error=str(e),
                posted_at=datetime.utcnow().isoformat()
            )
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        if len(content) > 280:
            return {"valid": False, "error": "Content exceeds 280 character limit"}
        if not content.strip():
            return {"valid": False, "error": "Content cannot be empty"}
        return {"valid": True}
    
    def get_character_limit(self) -> int:
        return 280
    
    def verify_credentials(self) -> bool:
        try:
            user = self.client.get_me()
            return user is not None
        except Exception:
            return False
    
    def _get_username(self) -> str:
        try:
            user = self.client.get_me()
            return user.data.username
        except Exception:
            return "unknown" 