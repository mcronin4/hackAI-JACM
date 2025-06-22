"""Service for managing user context data"""

from typing import Dict, Any, List
import logging
from .context_scraping_service import ContextScrapingService, ContextScrapingError
from ..database.context_operations import ContextPostsDB

logger = logging.getLogger(__name__)

class UserContextError(Exception):
    """Custom exception for user context operations"""
    pass

class UserContextService:
    """Service for managing user context data - coordinates scraping and database operations"""
    
    def __init__(self):
        self.scraping_service = ContextScrapingService()
        self.db = ContextPostsDB()
    
    async def setup_user_twitter_context(self, user_id: str, twitter_handle: str) -> Dict[str, Any]:
        """
        Set up Twitter context for a user
        
        Args:
            user_id: UUID of the user
            twitter_handle: Twitter handle (with or without @)
            
        Returns:
            Dictionary with success status and details
        """
        try:
            logger.info(f"Setting up Twitter context for user {user_id} with handle @{twitter_handle}")
            
            # Check if user already has context
            if await self.db.x_handle_has_context(twitter_handle):
                logger.info(f"Twitter handle {twitter_handle} already has context posts, skipping scraping")
                return {
                    "success": True,
                    "message": "Twitter handle already has context posts",
                    "posts_scraped": 0,
                    "posts_saved": 0,
                    "skipped": True
                }
            
            # Scrape Twitter posts
            logger.info(f"Scraping Twitter posts for @{twitter_handle}")
            scraped_posts = self.scraping_service.scrape_twitter_posts(
                twitter_handle=twitter_handle,
                max_posts=20
            )
            
            if not scraped_posts:
                logger.warning(f"No posts found for @{twitter_handle}")
                return {
                    "success": False,
                    "error": "No posts found for this Twitter handle",
                    "posts_scraped": 0,
                    "posts_saved": 0
                }
            
            # Select the longest posts
            selected_posts = self.scraping_service.select_longest_posts(
                posts=scraped_posts,
                target_count=10
            )
            
            logger.info(f"Selected {len(selected_posts)} longest posts from {len(scraped_posts)} scraped posts")
            
            # Save to database
            save_success = await self.db.save_context_posts(
                user_id=user_id,
                x_handle=twitter_handle,
                posts=selected_posts,
                platform="x"
            )
            
            if not save_success:
                logger.error(f"Failed to save context posts for user {user_id}")
                return {
                    "success": False,
                    "error": "Failed to save context posts to database",
                    "posts_scraped": len(scraped_posts),
                    "posts_saved": 0
                }
            
            logger.info(f"Successfully set up context for user {user_id}")
            return {
                "success": True,
                "message": "Successfully set up Twitter context",
                "posts_scraped": len(scraped_posts),
                "posts_saved": len(selected_posts),
                "twitter_handle": twitter_handle.lstrip('@'),
                "skipped": False
            }
            
        except ContextScrapingError as e:
            logger.error(f"Context scraping failed for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to scrape Twitter posts: {str(e)}",
                "posts_scraped": 0,
                "posts_saved": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error setting up context for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": "An unexpected error occurred while setting up context",
                "posts_scraped": 0,
                "posts_saved": 0
            }
    
    async def get_user_context_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of user's context data
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dictionary with context summary
        """
        try:
            posts = await self.db.get_user_context_posts(user_id)
            
            if not posts:
                return {
                    "has_context": False,
                    "total_posts": 0,
                    "platforms": []
                }
            
            platforms = list(set(post.get("platform", "unknown") for post in posts))
            
            return {
                "has_context": True,
                "total_posts": len(posts),
                "platforms": platforms,
                "oldest_post": min(post.get("created_at", "") for post in posts) if posts else None,
                "newest_post": max(post.get("created_at", "") for post in posts) if posts else None
            }
            
        except Exception as e:
            logger.error(f"Error getting context summary for user {user_id}: {str(e)}")
            return {
                "has_context": False,
                "total_posts": 0,
                "platforms": [],
                "error": str(e)
            }
    
    async def refresh_user_context(self, user_id: str, twitter_handle: str) -> Dict[str, Any]:
        """
        Refresh user's context by deleting old data and re-scraping
        
        Args:
            user_id: UUID of the user
            twitter_handle: Twitter handle
            
        Returns:
            Dictionary with refresh results
        """
        try:
            logger.info(f"Refreshing context for user {user_id}")
            
            # Delete existing context
            delete_success = await self.db.delete_user_context(user_id, platform="x")
            
            if not delete_success:
                logger.warning(f"Failed to delete existing context for user {user_id}, proceeding anyway")
            
            # Set up new context
            result = await self.setup_user_twitter_context(user_id, twitter_handle)
            result["refreshed"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error refreshing context for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": "Failed to refresh user context",
                "refreshed": True
            } 