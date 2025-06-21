import requests
from datetime import datetime
from typing import Dict, Any
from .base_platform import BaseSocialPlatform, PostRequest, PostResult

class LinkedInPlatform(BaseSocialPlatform):
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.access_token = credentials.get("access_token")
        self.person_id = credentials.get("person_id")  # LinkedIn person URN
        self.base_url = "https://api.linkedin.com/v2"
    
    def get_platform_name(self) -> str:
        return "linkedin"
    
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
            
            # Prepare LinkedIn post data
            post_data = {
                "author": f"urn:li:person:{self.person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": request.content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                json=post_data,
                headers=headers
            )
            
            if response.status_code == 201:
                post_id = response.headers.get("x-restli-id")
                return PostResult(
                    success=True,
                    platform=self.platform_name,
                    post_id=post_id,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}",
                    posted_at=datetime.utcnow().isoformat()
                )
            else:
                error_msg = f"LinkedIn API error: {response.status_code} - {response.text}"
                return PostResult(
                    success=False,
                    platform=self.platform_name,
                    error=error_msg,
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
        if len(content) > 3000:
            return {"valid": False, "error": "Content exceeds 3000 character limit"}
        if not content.strip():
            return {"valid": False, "error": "Content cannot be empty"}
        return {"valid": True}
    
    def get_character_limit(self) -> int:
        return 3000
    
    def verify_credentials(self) -> bool:
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/me", headers=headers)
            return response.status_code == 200
        except Exception:
            return False 