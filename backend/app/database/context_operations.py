"""Database operations for user context posts"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class ContextPostsDB:
    """Database operations for existing_context_posts table"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "existing_context_posts"
    
    async def x_handle_has_context(self, x_handle: str) -> bool:
        """Check if user already has context posts in database"""
        try:
            response = self.client.table(self.table_name).select("id").eq("x_handle", x_handle).limit(1).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking user context: {str(e)}")
            return False
    
    async def save_context_posts(self, user_id: str, x_handle: str, posts: List[Dict[str, Any]], platform: str = "x") -> bool:
        """Save context posts for a user"""
        try:
            # Prepare posts for insertion
            posts_to_insert = []
            for post in posts:
                posts_to_insert.append({
                    "user_id": user_id,
                    "x_handle": x_handle,
                    "post_content": post["content"],
                    "platform": platform,
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Insert posts
            response = self.client.table(self.table_name).insert(posts_to_insert).execute()
            
            if response.data:
                logger.info(f"Successfully saved {len(posts_to_insert)} context posts for user {user_id}")
                return True
            else:
                logger.error(f"Failed to save context posts for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving context posts: {str(e)}")
            return False
    
    async def get_user_context_posts(self, user_id: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get context posts for a user by user_id"""
        try:
            query = self.client.table(self.table_name).select("*").eq("user_id", user_id)
            
            if platform:
                query = query.eq("platform", platform)
                
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting context posts: {str(e)}")
            return []
    
    async def get_context_posts_by_handle(self, x_handle: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get context posts for a user by x_handle"""
        try:
            query = self.client.table(self.table_name).select("*").eq("x_handle", x_handle)
            
            if platform:
                query = query.eq("platform", platform)
                
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting context posts by handle: {str(e)}")
            return []
    
    async def delete_user_context(self, user_id: str, platform: Optional[str] = None) -> bool:
        """Delete context posts for a user"""
        try:
            query = self.client.table(self.table_name).delete().eq("user_id", user_id)
            
            if platform:
                query = query.eq("platform", platform)
                
            response = query.execute()
            logger.info(f"Deleted context posts for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting context posts: {str(e)}")
            return False 