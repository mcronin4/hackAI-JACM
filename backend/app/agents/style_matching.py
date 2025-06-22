from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime
import re
from difflib import SequenceMatcher


class StyleMatchingState(TypedDict):
    original_content: str
    context_posts: List[str]
    platform: str
    target_length: int
    similar_posts: List[Dict[str, Any]]
    style_analysis: str
    adapted_content: str
    final_content: str
    processing_time: float
    error: str
    skipped: bool


class StyleMatchingAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.2):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for style matching"""
        workflow = StateGraph(StyleMatchingState)
        
        # Add nodes
        workflow.add_node("input_validation", self._input_validation_node)
        workflow.add_node("similarity_analysis", self._similarity_analysis_node)
        workflow.add_node("analyze_style", self._style_analysis_node)
        workflow.add_node("content_adaptation", self._content_adaptation_node)
        workflow.add_node("length_enforcement", self._length_enforcement_node)
        
        # Add edges
        workflow.set_entry_point("input_validation")
        workflow.add_edge("input_validation", "similarity_analysis")
        workflow.add_edge("similarity_analysis", "analyze_style")
        workflow.add_edge("analyze_style", "content_adaptation")
        workflow.add_edge("content_adaptation", "length_enforcement")
        workflow.add_edge("length_enforcement", END)
        
        return workflow.compile()
    
    def _input_validation_node(self, state: StyleMatchingState) -> StyleMatchingState:
        """Validate input and determine if style matching should proceed"""
        try:
            # Check if we have context posts
            if not state.get('context_posts') or len(state['context_posts']) == 0:
                state['skipped'] = True
                state['final_content'] = state['original_content']
                return state
            
            # Validate required fields
            if not state.get('original_content'):
                state['error'] = "Original content is required"
                return state
            
            if not state.get('platform'):
                state['error'] = "Platform is required"
                return state
            
            # Set default target length if not provided
            if not state.get('target_length'):
                state['target_length'] = 240  # Default for Twitter content portion
            
            state['skipped'] = False
            
        except Exception as e:
            state['error'] = f"Error in input validation: {str(e)}"
        
        return state
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using sequence matching"""
        # Clean and normalize texts
        clean1 = re.sub(r'[^\w\s]', '', text1.lower())
        clean2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, clean1, clean2).ratio()
    
    def _similarity_analysis_node(self, state: StyleMatchingState) -> StyleMatchingState:
        """Find the top 3 most similar posts to the original content"""
        if state.get('error') or state.get('skipped'):
            return state
        
        try:
            similarities = []
            original_content = state['original_content']
            
            for post in state['context_posts']:
                if post.strip():  # Skip empty posts
                    similarity = self._calculate_similarity(original_content, post)
                    similarities.append({
                        'post': post,
                        'similarity_score': similarity
                    })
            
            # Sort by similarity and take top 3
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            state['similar_posts'] = similarities[:3]
            
            # If no similar posts found, skip style matching
            if not state['similar_posts']:
                state['skipped'] = True
                state['final_content'] = state['original_content']
            
        except Exception as e:
            state['error'] = f"Error in similarity analysis: {str(e)}"
        
        return state
    
    def _style_analysis_node(self, state: StyleMatchingState) -> StyleMatchingState:
        """Analyze the writing style of similar posts"""
        if state.get('error') or state.get('skipped'):
            return state
        
        try:
            similar_posts_text = "\n\n".join([f"Post {i+1}: {post['post']}" 
                                            for i, post in enumerate(state['similar_posts'])])
            
            system_prompt = f"""<context>
You are a writing style analyst. Analyze the writing style of the following posts to create a brief style guide.

<posts>
{similar_posts_text}
</posts>
</context>

<task>
Analyze the writing style and provide a concise style description focusing on:
1. Tone (casual, professional, conversational, etc.)
2. Structure (short sentences, long paragraphs, bullet points, etc.)
3. Voice (first person, second person, authoritative, friendly, etc.)
4. Common phrases or expressions
5. Punctuation patterns (use of dashes, ellipses, exclamation marks, etc.)

Keep the analysis brief but specific - focus on patterns that can be replicated.
</task>"""

            user_prompt = "Analyze the writing style of these posts and provide a concise style guide."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            state['style_analysis'] = response.content.strip()
            
        except Exception as e:
            state['error'] = f"Error in style analysis: {str(e)}"
        
        return state
    
    def _content_adaptation_node(self, state: StyleMatchingState) -> StyleMatchingState:
        """Adapt the content to match the analyzed style while preserving meaning"""
        if state.get('error') or state.get('skipped'):
            return state
        
        try:
            similar_posts_examples = "\n\n".join([f"Example {i+1}: {post['post']}" 
                                                for i, post in enumerate(state['similar_posts'])])
            
            system_prompt = f"""<context>
You are a content adaptation specialist. Your job is to adapt content to match a specific writing style while STRICTLY preserving the original meaning and emotional intent.

<originalContent>
{state['original_content']}
</originalContent>

<styleGuide>
{state['style_analysis']}
</styleGuide>

<styleExamples>
{similar_posts_examples}
</styleExamples>
</context>

<criticalRules>
1. PRESERVE MEANING: The core message, facts, and emotional intent must remain identical
2. PRESERVE EMOTION: The emotional tone and impact must stay the same
3. ADAPT STYLE ONLY: Only change tone, voice, structure, and expression patterns
4. USE EXAMPLES: Reference the concrete examples to match the style patterns
5. NO CONTENT CHANGES: Do not add new ideas, remove key points, or alter the substance
</criticalRules>

<task>
Adapt the original content to match the writing style shown in the examples, following the style guide. Focus on:
- Matching the tone and voice patterns
- Using similar sentence structures
- Incorporating similar expressions or phrase patterns
- Following similar punctuation styles

Output only the adapted content - no explanations or additional text.
</task>"""

            user_prompt = "Adapt the content to match the style while preserving all meaning and emotion."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            state['adapted_content'] = response.content.strip()
            
        except Exception as e:
            state['error'] = f"Error in content adaptation: {str(e)}"
        
        return state
    
    def _length_enforcement_node(self, state: StyleMatchingState) -> StyleMatchingState:
        """Enforce character length limits while maintaining style and meaning"""
        if state.get('error') or state.get('skipped'):
            return state
        
        try:
            adapted_content = state['adapted_content']
            target_length = state['target_length']
            
            # If content is within target length, use as-is
            if len(adapted_content) <= target_length:
                state['final_content'] = adapted_content
                return state
            
            # If too long, intelligently trim while preserving style
            system_prompt = f"""<context>
You need to shorten this content to exactly {target_length} characters or fewer while maintaining the writing style and core meaning.

<contentToShorten>
{adapted_content}
</contentToShorten>

<currentLength>{len(adapted_content)}</currentLength>
<targetLength>{target_length}</targetLength>
</context>

<task>
Shorten the content by:
1. Removing less essential words or phrases
2. Using more concise expressions
3. Maintaining the core message and emotional impact
4. Preserving the writing style and tone
5. Ensuring the result is EXACTLY {target_length} characters or fewer

Count every character including spaces and punctuation. Output only the shortened content.
</task>"""

            user_prompt = f"Shorten to {target_length} characters maximum while preserving style and meaning."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            shortened_content = response.content.strip()
            
            # Final validation of length
            if len(shortened_content) <= target_length:
                state['final_content'] = shortened_content
            else:
                # Fallback: use original if shortening failed
                state['final_content'] = state['original_content'][:target_length].rsplit(' ', 1)[0]
            
        except Exception as e:
            state['error'] = f"Error in length enforcement: {str(e)}"
        
        return state
    
    def match_style(
        self,
        original_content: str,
        context_posts: List[str],
        platform: str = "twitter",
        target_length: int = 240
    ) -> Dict[str, Any]:
        """Main method to perform style matching"""
        start_time = datetime.now()
        
        initial_state = StyleMatchingState(
            original_content=original_content,
            context_posts=context_posts,
            platform=platform,
            target_length=target_length,
            similar_posts=[],
            style_analysis="",
            adapted_content="",
            final_content="",
            processing_time=0.0,
            error="",
            skipped=False
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
                    'final_content': original_content,  # Fallback to original
                    'style_analysis': result.get('style_analysis', ''),
                    'similar_posts_count': len(result.get('similar_posts', [])),
                    'skipped': result.get('skipped', False),
                    'processing_time': processing_time
                }
            
            return {
                'success': True,
                'final_content': result['final_content'],
                'style_analysis': result.get('style_analysis', ''),
                'similar_posts_count': len(result.get('similar_posts', [])),
                'skipped': result.get('skipped', False),
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': False,
                'error': f"Graph execution error: {str(e)}",
                'final_content': original_content,  # Fallback to original
                'style_analysis': '',
                'similar_posts_count': 0,
                'skipped': True,
                'processing_time': processing_time
            } 