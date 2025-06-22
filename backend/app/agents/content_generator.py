from typing import Dict, List, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime
from app.config.platform_configs import PlatformConfigManager


class ContentGenerationState(TypedDict):
    original_text: str
    topics: List[Dict[str, Any]]
    target_platforms: List[str]
    original_url: str
    audience_context: str
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
            
            # Original URL is optional - set to empty string if not provided
            if not state.get('original_url'):
                state['original_url'] = ""
            
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
            platform = state['target_platforms'][0]
            
            # Platform-specific content strategies
            if platform.lower() == "twitter":
                state['content_strategy'] = "single_tweet"
            elif platform.lower() == "linkedin":
                state['content_strategy'] = "professional_post"
            else:
                # Default fallback
                state['content_strategy'] = "single_tweet"
            
        except Exception as e:
            state['error'] = f"Error in content strategy: {str(e)}"
        
        return state
    
    def _content_generation_node(self, state: ContentGenerationState) -> ContentGenerationState:
        """Generate integrated content with CTA based on topic, emotion, and platform"""
        if state.get('error'):
            return state
        
        try:
            current_topic = state['current_topic']
            platform = state['target_platforms'][0]
            config = self.platform_config.get_config(platform)
            strategy = state['content_strategy']
            
            # Platform-specific content length targets
            if platform.lower() == "twitter":
                # Twitter: Leave room for URLs (~23 chars) 
                min_content_length = 210
                max_content_length = 240
            elif platform.lower() == "linkedin":
                # LinkedIn: Use more of the available space for professional content
                min_content_length = 500
                max_content_length = 800
            else:
                # Default fallback
                min_content_length = 200
                max_content_length = 250
            
            # Create platform-specific system prompt
            system_prompt = self._create_platform_prompt(
                state, current_topic, platform, config, strategy, 
                min_content_length, max_content_length
            )

            user_prompt = f"Create a complete {platform} post following the structure and requirements provided."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Store the complete content
            state['generated_content'] = response.content.strip()
            
            # CTA is integrated into generated_content
            state['call_to_action'] = ""
            
        except Exception as e:
            state['error'] = f"Error in content generation: {str(e)}"
        
        return state
    
    def _create_platform_prompt(self, state: ContentGenerationState, current_topic: Dict[str, Any], 
                               platform: str, config, strategy: str, min_length: int, max_length: int) -> str:
        """Create platform-specific prompts for content generation"""
        
        base_context = f"""<context>

<originalContent>
{state['original_text']}
</originalContent>

<targetAudience>
{state.get('audience_context', 'No audience context provided')}
</targetAudience>

<coreIdea>
{current_topic['topic_name']}
</coreIdea>

<referenceText>
{current_topic.get('content_excerpt', '')}
</referenceText>

<emotionalAlignment>
{current_topic.get('primary_emotion', 'encourage_dreams')}
</emotionalAlignment>

<reasonForEmotion>
{current_topic.get('reasoning', 'Emotional targeting for engagement')}
</reasonForEmotion>

<platform>{platform}</platform>
<contentStrategy>{strategy}</contentStrategy>
<toneGuidelines>{config.tone_guidelines}</toneGuidelines>

</context>"""

        if strategy == "single_tweet":
            return base_context + f"""

<prompt>
You are creating a Twitter post based on the context.

Here's how to approach it:

1. Start with the core idea and connect it to the emotional alignment
2. Make it engaging and conversational (Twitter style) 
3. Use practical examples that resonate
4. Write in the same style as the originalContent
5. Create content that drives engagement through questions or relatable scenarios
6. BE CONCISE - Twitter requires brevity and punch

Example approach:
- Hook: Connect the topic to the emotion in a relatable way
- Body: Provide a practical example or scenario  
- Engagement: End in a way that encourages interaction

Make sure to write in the same style as the originalContent but KEEP IT BRIEF.

CRITICAL CHARACTER LIMIT REQUIREMENTS:
- MUST be between {min_length}-{max_length} characters EXACTLY
- NEVER exceed {max_length} characters - this will break the system
- Count every character including spaces and punctuation
- Do NOT include URLs (they are added separately)
- Tone: {config.tone_guidelines}
- PRIORITIZE BREVITY over elaboration - this is Twitter, not an essay

</prompt>

<structure>
[place the content here]
</structure>"""

        elif strategy == "professional_post":
            return base_context + f"""

<prompt>
You are creating a LinkedIn post based on the context.

Here's how to approach professional content:

1. Start with the core idea but frame it professionally and thoughtfully
2. Connect it to the emotional alignment in a way that's appropriate for a professional audience
3. Provide deeper insights, examples, or actionable advice
4. Write in the same style as the originalContent but elevated for professional context
5. Create content that sparks professional discussion and reflection

Structure approach:
- Opening: Professional hook that connects topic to emotion
- Development: Deeper exploration with examples or insights
- Professional insight: Actionable takeaway or thought-provoking conclusion

Make sure to write in the same style as the originalContent but adapted for professional discourse.

ABSOLUTE REQUIREMENTS:
- MUST be between {min_length}-{max_length} characters EXACTLY
- NEVER exceed {max_length} characters - this will break the system
- Count every character including spaces and punctuation
- Do NOT include URLs (they are added separately)
- Tone: {config.tone_guidelines}
- Style: Professional, insightful, and thought-provoking

</prompt>

<structure>
[place the content here]
</structure>"""

        else:
            # Fallback for unknown strategies
            return base_context + f"""

<prompt>
Create a {platform} post based on the context provided.

ABSOLUTE REQUIREMENTS:
- MUST be between {min_length}-{max_length} characters EXACTLY
- NEVER exceed {max_length} characters
- Count every character including spaces and punctuation
- Do NOT include URLs (they are added separately)
- Tone: {config.tone_guidelines}

</prompt>

<structure>
[place the content here]
</structure>"""
    
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
        original_url: str = "", 
        platform: str = "twitter",
        audience_context: str = ""
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
            audience_context=audience_context,
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
