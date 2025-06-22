"""
Performance optimization configuration for the AI agents.
This file contains optimized settings for maximum speed while maintaining quality.
"""

import os
from typing import Dict, Any

class PerformanceConfig:
    """Optimized configuration for maximum speed"""
    
    # Model Selection (Speed Optimized)
    FAST_MODEL = "gemini-1.5-flash"  # Fastest available model
    BALANCED_MODEL = "gemini-1.5-pro"  # Balance of speed and quality
    QUALITY_MODEL = "gemini-2.5-pro"  # Highest quality but slower
    
    # Temperature Settings (Lower = Faster)
    FAST_TEMPERATURE = 0.0  # Fastest responses, most deterministic
    BALANCED_TEMPERATURE = 0.1  # Good balance
    CREATIVE_TEMPERATURE = 0.3  # More creative but slower
    
    # Timeout Settings (Aggressive for speed)
    API_TIMEOUT = 10.0  # Seconds - fail fast
    MAX_RETRIES = 2  # Reduce retries for speed
    
    # Token Limits (Shorter = Faster)
    MAX_OUTPUT_TOKENS = {
        'topic_extraction': 500,  # Keep topics concise
        'emotion_analysis': 300,  # Short emotion analysis
        'content_generation': 600,  # Reasonable content length
        'style_matching': 400  # Brief style adjustments
    }
    
    # Concurrency Settings
    MAX_CONCURRENT_REQUESTS = 10  # Increase API concurrency
    THREAD_POOL_SIZE = 8  # Optimize thread pool
    
    @classmethod
    def get_speed_optimized_config(cls) -> Dict[str, Any]:
        """Get configuration optimized for maximum speed"""
        return {
            'model_name': cls.FAST_MODEL,
            'temperature': cls.FAST_TEMPERATURE,
            'timeout': cls.API_TIMEOUT,
            'max_retries': cls.MAX_RETRIES,
            'max_output_tokens': 500,  # Global limit for speed
            'top_p': 0.8,  # Slightly restrict sampling for speed
            'top_k': 20,  # Limit token consideration for speed
        }
    
    @classmethod
    def get_balanced_config(cls) -> Dict[str, Any]:
        """Get configuration balancing speed and quality"""
        return {
            'model_name': cls.BALANCED_MODEL,
            'temperature': cls.BALANCED_TEMPERATURE,
            'timeout': cls.API_TIMEOUT * 1.5,
            'max_retries': 3,
            'max_output_tokens': 800,
            'top_p': 0.9,
            'top_k': 40,
        }
    
    @classmethod
    def get_agent_specific_config(cls, agent_type: str) -> Dict[str, Any]:
        """Get optimized config for specific agent types"""
        base_config = cls.get_speed_optimized_config()
        
        if agent_type == 'topic_extraction':
            base_config.update({
                'max_output_tokens': cls.MAX_OUTPUT_TOKENS['topic_extraction'],
                'temperature': 0.0,  # Most deterministic for topics
            })
        elif agent_type == 'emotion_analysis':
            base_config.update({
                'max_output_tokens': cls.MAX_OUTPUT_TOKENS['emotion_analysis'],
                'temperature': 0.0,  # Consistent emotion classification
            })
        elif agent_type == 'content_generation':
            base_config.update({
                'max_output_tokens': cls.MAX_OUTPUT_TOKENS['content_generation'],
                'temperature': 0.2,  # Slight creativity for content
            })
        elif agent_type == 'style_matching':
            base_config.update({
                'max_output_tokens': cls.MAX_OUTPUT_TOKENS['style_matching'],
                'temperature': 0.1,  # Consistent style adaptation
            })
        
        return base_config

# Environment variable overrides (for easy deployment config)
def get_env_optimized_config() -> Dict[str, Any]:
    """Get configuration from environment with speed optimizations"""
    return {
        'model_name': os.getenv("GOOGLE_MODEL_NAME", PerformanceConfig.FAST_MODEL),
        'temperature': float(os.getenv("GOOGLE_TEMPERATURE", str(PerformanceConfig.FAST_TEMPERATURE))),
        'timeout': float(os.getenv("GOOGLE_TIMEOUT", str(PerformanceConfig.API_TIMEOUT))),
        'max_retries': int(os.getenv("GOOGLE_MAX_RETRIES", str(PerformanceConfig.MAX_RETRIES))),
        'max_output_tokens': int(os.getenv("GOOGLE_MAX_TOKENS", "500")),
    }

# Speed Optimization Tips
OPTIMIZATION_TIPS = {
    'model_selection': "Use gemini-1.5-flash for 2-3x speed improvement over gemini-2.5-pro",
    'temperature': "Lower temperature (0.0-0.1) = faster, more deterministic responses",
    'token_limits': "Shorter max_output_tokens = faster generation",
    'concurrency': "Parallel processing can improve throughput by 3-5x",
    'caching': "Cache frequent requests to avoid redundant API calls",
    'prompt_optimization': "Shorter, more specific prompts = faster responses",
    'error_handling': "Fail fast with lower timeouts and retry limits"
} 