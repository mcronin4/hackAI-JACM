"""Supabase client configuration and connection"""

import os
from supabase import create_client, Client
from typing import Optional
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Singleton Supabase client"""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance
    
    @classmethod
    def _create_client(cls) -> Client:
        """Create Supabase client from environment variables"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file"
            )
        
        try:
            client = create_client(url, key)
            logger.info("Successfully connected to Supabase")
            return client
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {str(e)}")
            raise

def get_supabase_client() -> Client:
    """Convenience function to get Supabase client"""
    return SupabaseClient.get_client() 