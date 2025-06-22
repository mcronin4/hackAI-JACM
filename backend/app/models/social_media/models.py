from pydantic import BaseModel, Field
from typing import Optional

class PlatformPostRequest(BaseModel):
    content: str = Field(..., description="Post content", min_length=1)
    thread_id: Optional[str] = Field(None, description="Optional thread/reply ID")

class PlatformPostResponse(BaseModel):
    success: bool
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    posted_at: str

class PlatformStatusResponse(BaseModel):
    supported: bool
    configured: bool
    credentials_valid: Optional[bool] = None
    character_limit: Optional[int] = None
    error: Optional[str] = None

class AllPlatformsStatusResponse(BaseModel):
    platforms: dict 