"""
Performance-optimized versions of AI agents.
These agents are specifically tuned for speed while maintaining quality.
"""

from typing import Dict, List, Any, Optional
import asyncio
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Note: These imports would need to be adjusted based on your actual project structure
# from ..utils.cache_manager import cache_topics, cache_emotions, cache_content, cache_style
# from ..performance_config import PerformanceConfig
import logging

logger = logging.getLogger(__name__)

class OptimizedTopicExtractor:
    """High-speed topic extraction with caching and optimized prompts"""
    
    def __init__(self):
        # Speed-optimized configuration
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Fastest model
            temperature=0.0,  # Most deterministic
            max_output_tokens=500,  # Limit output for speed
            timeout=10.0,  # Fail fast
            max_retries=2  # Fewer retries
        )
    
    def extract_topics(self, text: str, max_topics: int = 5) -> Dict[str, Any]:
        """Extract topics with aggressive speed optimization"""
        start_time = time.time()
        
        try:
            # Ultra-concise prompt for speed
            prompt = f"""Extract {max_topics} key topics from this text. Return JSON only:

Text: {text[:2000]}...

Format:
{{"topics": [{{"id": 1, "name": "Topic Name", "excerpt": "brief quote", "confidence": 0.9}}], "success": true}}"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Fast JSON parsing
            import json
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result.update({
                    'processing_time': time.time() - start_time,
                    'total_topics': len(result.get('topics', [])),
                    'cached': False
                })
                return result
            
            # Fallback
            return {
                'success': False,
                'error': 'Failed to parse response',
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

class OptimizedEmotionAnalyzer:
    """High-speed emotion analysis with minimal prompting"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            max_output_tokens=300,
            timeout=10.0,
            max_retries=2
        )
        
        # Pre-defined emotion categories for speed
        self.emotions = ["encourage_dreams", "justify_failures", "allay_fears", 
                        "confirm_suspicions", "unite_against_challenges"]
    
    def analyze_emotions(self, topics: List[Dict[str, Any]], audience_context: str = "") -> Dict[str, Any]:
        """Fast emotion analysis with caching"""
        start_time = time.time()
        
        try:
            results = []
            
            for topic in topics:
                # Ultra-fast prompt
                prompt = f"""Topic: {topic['topic_name']}
Context: {topic.get('content_excerpt', '')}

Pick best emotion: {', '.join(self.emotions)}

JSON: {{"primary_emotion": "encourage_dreams", "confidence": 0.9, "reasoning": "brief reason"}}"""

                response = self.llm.invoke([HumanMessage(content=prompt)])
                
                # Fast parsing
                import json, re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    emotion_data = json.loads(json_match.group())
                    results.append({
                        'topic_id': topic.get('topic_id', topic.get('id')),
                        'topic_name': topic['topic_name'],
                        'content_excerpt': topic.get('content_excerpt', ''),
                        **emotion_data
                    })
            
            return {
                'success': True,
                'emotion_analysis': results,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

class OptimizedContentGenerator:
    """High-speed content generation with smart caching"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,  # Slight creativity for content
            max_output_tokens=600,
            timeout=10.0,
            max_retries=2
        )
    
    def generate_content_for_topic(
        self, 
        topic: Dict[str, Any], 
        original_text: str, 
        original_url: str = "", 
        platform: str = "twitter",
        audience_context: str = ""
    ) -> Dict[str, Any]:
        """Ultra-fast content generation"""
        start_time = time.time()
        
        try:
            # Platform-specific optimization
            if platform == "twitter":
                max_chars = 240
                style = "concise, engaging"
            elif platform == "linkedin":
                max_chars = 600
                style = "professional, insightful"
            else:
                max_chars = 300
                style = "clear, engaging"
            
            # Minimal prompt for speed
            prompt = f"""Create {platform} post ({max_chars} chars max):

Topic: {topic['topic_name']}
Emotion: {topic.get('primary_emotion', 'encourage_dreams')}
Style: {style}

Post:"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Quick validation
            if len(content) > max_chars:
                content = content[:max_chars-3] + "..."
            
            return {
                'success': True,
                'final_post': content,
                'content_strategy': f"{platform}_{topic.get('primary_emotion', 'default')}",
                'call_to_action': "",
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

class TurboContentPipeline:
    """Ultra-fast content pipeline using all optimizations"""
    
    def __init__(self):
        self.topic_extractor = OptimizedTopicExtractor()
        self.emotion_analyzer = OptimizedEmotionAnalyzer()
        self.content_generator = OptimizedContentGenerator()
    
    async def turbo_process(
        self,
        text: str,
        target_platforms: List[str] = None,
        original_url: str = ""
    ) -> Dict[str, Any]:
        """Process content at maximum speed"""
        start_time = time.time()
        
        if target_platforms is None:
            target_platforms = ["twitter"]
        
        try:
            # Step 1: Fast topic extraction
            topic_result = self.topic_extractor.extract_topics(text, max_topics=3)  # Fewer topics for speed
            
            if not topic_result['success']:
                return {'success': False, 'error': topic_result['error']}
            
            topics = topic_result['topics']
            
            # Step 2: Process topics in parallel with aggressive concurrency
            async def process_topic_ultra_fast(topic):
                # Emotion analysis
                emotion_result = self.emotion_analyzer.analyze_emotions([topic])
                if not emotion_result['success']:
                    return None
                
                enhanced_topic = emotion_result['emotion_analysis'][0]
                
                # Content generation for all platforms in parallel
                content_tasks = []
                for platform in target_platforms:
                    content_tasks.append(
                        asyncio.get_event_loop().run_in_executor(
                            None,
                            self.content_generator.generate_content_for_topic,
                            enhanced_topic, text, original_url, platform, ""
                        )
                    )
                
                content_results = await asyncio.gather(*content_tasks)
                
                # Collect results
                final_results = []
                for i, content_result in enumerate(content_results):
                    if content_result['success']:
                        platform = target_platforms[i]
                        final_results.append({
                            'platform': platform,
                            'content': content_result['final_post'],
                            'topic_name': enhanced_topic['topic_name'],
                            'emotion': enhanced_topic['primary_emotion']
                        })
                
                return final_results
            
            # Process all topics in parallel
            topic_tasks = [process_topic_ultra_fast(topic) for topic in topics]
            all_results = await asyncio.gather(*topic_tasks)
            
            # Flatten results
            final_posts = []
            for topic_results in all_results:
                if topic_results:
                    final_posts.extend(topic_results)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'posts': final_posts,
                'total_posts': len(final_posts),
                'processing_time': processing_time,
                'speed_optimized': True,
                'topics_processed': len(topics)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

# Performance test utilities
async def benchmark_pipeline_speed(text: str, iterations: int = 5) -> Dict[str, Any]:
    """Benchmark the optimized pipeline speed"""
    turbo_pipeline = TurboContentPipeline()
    
    times = []
    for i in range(iterations):
        start = time.time()
        result = await turbo_pipeline.turbo_process(text)
        elapsed = time.time() - start
        times.append(elapsed)
        
        if not result['success']:
            return {'error': f'Benchmark failed on iteration {i+1}'}
    
    return {
        'avg_time': sum(times) / len(times),
        'min_time': min(times),
        'max_time': max(times),
        'total_time': sum(times),
        'iterations': iterations,
        'posts_per_second': iterations / sum(times) if sum(times) > 0 else 0
    } 