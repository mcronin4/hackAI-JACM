from typing import Dict, List, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime
from app.config.platform_configs import PlatformConfigManager


class ContentGenerationState(TypedDict):
    original_text: str
    topics: List[Dict[str, Any]]
    target_platforms: List[str]
    original_url: str
    current_topic: Dict[str, Any]
    content_strategy: str
    generated_content: str
    call_to_action: str
    final_post: str
    processing_time: float
    error: str


class ContentGeneratorAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.platform_config = PlatformConfigManager()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for content generation"""
        workflow = StateGraph(ContentGenerationState)
        
        # Add nodes - simplified workflow
        workflow.add_node("input_processing", self._input_processing_node)
        workflow.add_node("strategy_planning", self._content_strategy_node)
        workflow.add_node("content_generation", self._content_generation_node)
        workflow.add_node("formatting", self._formatting_node)
        
        # Add edges - simple linear workflow
        workflow.set_entry_point("input_processing")
        workflow.add_edge("input_processing", "strategy_planning")
        workflow.add_edge("strategy_planning", "content_generation")
        workflow.add_edge("content_generation", "formatting")
        workflow.add_edge("formatting", END)
        
        return workflow.compile()
    

    
    def _input_processing_node(self, state: ContentGenerationState) -> ContentGenerationState:
        """Process and validate input data"""
        try:
            # Validate required fields
            if not state.get('topics') or len(state['topics']) == 0:
                state['error'] = "No topics provided"
                return state
            
            if not state.get('original_text'):
                state['error'] = "Original text is required"
                return state
            
            if not state.get('original_url'):
                state['error'] = "Original URL is required"
                return state
            
            # Set current topic (assumes we're processing one topic at a time)
            state['current_topic'] = state['topics'][0]
            
            # Validate platform support
            if not state.get('target_platforms'):
                state['target_platforms'] = ["twitter"]
            
            current_platform = state['target_platforms'][0]  # Process first platform
            if not self.platform_config.is_platform_supported(current_platform):
                state['error'] = f"Unsupported platform: {current_platform}"
                return state
            

                
        except Exception as e:
            state['error'] = f"Error in input processing: {str(e)}"
        
        return state
    
    def _content_strategy_node(self, state: ContentGenerationState) -> ContentGenerationState:
        """Determine content strategy based on topic and platform"""
        if state.get('error'):
            return state
        
        try:
            # Always use single_tweet strategy for Twitter
            state['content_strategy'] = "single_tweet"
            
        except Exception as e:
            state['error'] = f"Error in content strategy: {str(e)}"
        
        return state
    
    def _content_generation_node(self, state: ContentGenerationState) -> ContentGenerationState:
        """Generate integrated content with CTA based on topic and emotion"""
        if state.get('error'):
            return state
        
        try:
            current_topic = state['current_topic']
            platform = state['target_platforms'][0]
            config = self.platform_config.get_config(platform)
            
            # Twitter shortens URLs to ~23 characters
            # Target range: 210-240 characters for content
            min_content_length = 210
            max_content_length = 240
            
            system_prompt = f"""You are a social media content creator. Write a Twitter post with integrated call-to-action.

ABSOLUTE REQUIREMENTS:
- MUST be between {min_content_length}-{max_content_length} characters EXACTLY
- NEVER exceed {max_content_length} characters - this will break the system
- Count every character including spaces and punctuation
- Do NOT include URLs (they are added separately)

CONTENT REQUIREMENTS:
- Topic: {current_topic['topic_name']}
- Emotion: {current_topic['primary_emotion']}
- Include natural call-to-action in the text
- Make it engaging and valuable

CHARACTER COUNT VERIFICATION:
Before responding, count your characters. Your response must be {min_content_length}-{max_content_length} characters.

RESPONSE FORMAT:
Return ONLY the post text. No explanations, no formatting, no URLs."""

            user_prompt = f"Create a complete {platform} post for this topic: {current_topic['topic_name']}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # The response contains the integrated content + CTA
            complete_content = response.content.strip()
            
            # Store the complete content as generated_content
            state['generated_content'] = complete_content
            
            # CTA is integrated into generated_content, set call_to_action to empty for compatibility
            state['call_to_action'] = ""
            
        except Exception as e:
            state['error'] = f"Error in content generation: {str(e)}"
        
        return state
    


    
    def _formatting_node(self, state: ContentGenerationState) -> ContentGenerationState:
        """Format the final post with integrated content+CTA and URL"""
        if state.get('error'):
            return state
        
        try:
            # Build the final post with integrated content+CTA approach
            components = []
            
            # Add the integrated content (which already includes the CTA)
            if state['generated_content']:
                components.append(state['generated_content'])
            
            # Add URL separately
            if state['original_url']:
                components.append(state['original_url'])
            
            # Join components with a single space
            state['final_post'] = ' '.join(components)
            
        except Exception as e:
            state['error'] = f"Error in formatting: {str(e)}"
        
        return state
    
    def generate_content_for_topic(
        self, 
        topic: Dict[str, Any], 
        original_text: str, 
        original_url: str, 
        platform: str = "twitter"
    ) -> Dict[str, Any]:
        """Main method to generate content for a single topic"""
        start_time = datetime.now()
        
        # Validate platform support
        if not self.platform_config.is_platform_supported(platform):
            return {
                'success': False,
                'error': f"Unsupported platform: {platform}",
                'final_post': "",
                'content_strategy': "",
                'call_to_action': "",
                'processing_time': 0.0
            }
        
        initial_state = ContentGenerationState(
            original_text=original_text,
            topics=[topic],
            target_platforms=[platform],
            original_url=original_url,
            current_topic={},
            content_strategy="",
            generated_content="",
            call_to_action="",
            final_post="",
            processing_time=0.0,
            error=""
        )
        
        try:
            result = self.graph.invoke(initial_state)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if result.get('error'):
                return {
                    'success': False,
                    'error': result['error'],
                    'final_post': "",
                    'content_strategy': result.get('content_strategy', ""),
                    'call_to_action': result.get('call_to_action', ""),
                    'processing_time': processing_time
                }
            
            return {
                'success': True,
                'final_post': result['final_post'],
                'content_strategy': result['content_strategy'],
                'call_to_action': result['call_to_action'],
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': False,
                'error': f"Graph execution error: {str(e)}",
                'final_post': "",
                'content_strategy': "",
                'call_to_action': "",
                'processing_time': processing_time
            }
