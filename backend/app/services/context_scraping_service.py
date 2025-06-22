"""Service for scraping Twitter context using Bright Data"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextScrapingError(Exception):
    """Custom exception for context scraping errors"""
    pass

class ContextScrapingService:
    """Service for scraping user's Twitter posts using Bright Data"""
    
    def __init__(self):
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        if not self.api_key:
            raise ValueError("BRIGHT_DATA_API_KEY not found in environment variables")
        
        self.api_url = "https://api.brightdata.com/datasets/v3/scrape"
        self.dataset_id = "gd_lwxmeb2u1cniijd7t4"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def scrape_twitter_posts(self, twitter_handle: str, max_posts: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape Twitter posts for a given handle using Bright Data
        
        Args:
            twitter_handle: Twitter handle without @ symbol
            max_posts: Maximum number of posts to scrape
            
        Returns:
            List of post dictionaries with content and metadata
            
        Raises:
            ContextScrapingError: If scraping fails
        """
        try:
            logger.info(f"Starting Twitter scraping for @{twitter_handle}")
            
            # Clean handle (remove @ if present)
            handle = twitter_handle.lstrip('@')
            
            params = {
                "dataset_id": self.dataset_id,
                "include_errors": "true",
            }
            
            data = [
                {
                    "url": f"https://x.com/{handle}",
                    "max_number_of_posts": max_posts
                }
            ]
            
            logger.info(f"Making request to Bright Data API for {max_posts} posts")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code != 200:
                error_msg = f"Bright Data API returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ContextScrapingError(error_msg)
            
            result = response.json()
            logger.info(f"Received response from Bright Data API")
            
            # Parse and extract posts from response
            posts = self._parse_bright_data_response(result)
            logger.info(f"Successfully parsed {len(posts)} posts from API response")
            
            return posts
            
        except requests.exceptions.Timeout:
            error_msg = "Bright Data API request timed out"
            logger.error(error_msg)
            raise ContextScrapingError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during Bright Data API request: {str(e)}"
            logger.error(error_msg)
            raise ContextScrapingError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during Twitter scraping: {str(e)}"
            logger.error(error_msg)
            raise ContextScrapingError(error_msg)
    
    def _parse_bright_data_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Bright Data API response to extract post content
        
        Args:
            response: Raw response from Bright Data API
            
        Returns:
            List of parsed posts with content and metadata
        """
        posts = []
        
        try:
            # The exact structure depends on Bright Data's response format
            # This is a generic parser that should handle common structures
            
            if isinstance(response, dict):
                # Check for posts in common response keys
                posts_data = None
                
                if 'posts' in response:
                    posts_data = response['posts']
                elif 'data' in response:
                    posts_data = response['data']
                elif 'results' in response:
                    posts_data = response['results']
                elif isinstance(response, list):
                    posts_data = response
                
                if posts_data and isinstance(posts_data, list):
                    for post_item in posts_data:
                        parsed_post = self._parse_single_post(post_item)
                        if parsed_post:
                            posts.append(parsed_post)
            
            elif isinstance(response, list):
                for post_item in response:
                    parsed_post = self._parse_single_post(post_item)
                    if parsed_post:
                        posts.append(parsed_post)
            
            logger.info(f"Parsed {len(posts)} posts from response")
            return posts
            
        except Exception as e:
            logger.error(f"Error parsing Bright Data response: {str(e)}")
            raise ContextScrapingError(f"Failed to parse API response: {str(e)}")
    
    def _parse_single_post(self, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a single post from the API response
        
        Args:
            post_data: Single post data from API
            
        Returns:
            Parsed post dictionary or None if parsing fails
        """
        try:
            content = post_data["description"]
            if not content:
                logger.warning(f"No content found in post data: {post_data}")
                return None
            
            # Clean and validate content
            content = str(content).strip()
            if not content or len(content) < 10:  # Skip very short posts
                return None
            
            # Count words for filtering
            word_count = len(content.split())
            
            parsed_post = {
                "content": content,
                "word_count": word_count,
                "scraped_at": datetime.utcnow().isoformat(),
                "raw_data": post_data  # Keep original for debugging
            }
            
            return parsed_post
            
        except Exception as e:
            logger.warning(f"Failed to parse single post: {str(e)}")
            return None
    
    def select_longest_posts(self, posts: List[Dict[str, Any]], target_count: int = 10) -> List[Dict[str, Any]]:
        """
        Select the longest posts by word count
        
        Args:
            posts: List of scraped posts
            target_count: Number of posts to select
            
        Returns:
            List of longest posts, up to target_count
        """
        if not posts:
            return []
        
        # Sort by word count in descending order
        sorted_posts = sorted(posts, key=lambda x: x.get('word_count', 0), reverse=True)
        
        # Select top posts, but don't exceed available posts
        selected_count = min(target_count, len(sorted_posts))
        selected_posts = sorted_posts[:selected_count]
        
        logger.info(f"Selected {selected_count} longest posts from {len(posts)} total posts")
        
        return selected_posts 