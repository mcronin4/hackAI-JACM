from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re
from datetime import datetime


class EmotionTargetingState(TypedDict):
    topics: List[Dict[str, Any]]
    audience_context: str
    emotion_analysis: List[Dict[str, Any]]
    processing_time: float
    error: str


class EmotionTargetingAgent:
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.1):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.graph = self._build_graph()
        
        # The 5 core emotion themes for marketing
        self.emotion_themes = {
            "encourage_dreams": "Encourage Their Dreams - Inspire aspiration, growth, and positive future outcomes",
            "justify_failures": "Justify Their Failures - Validate struggles, provide external explanations, remove self-blame",
            "allay_fears": "Allay Their Fears - Provide reassurance, reduce anxiety, offer safety and security",
            "confirm_suspicions": "Confirm Their Suspicions - Validate existing doubts, provide 'I knew it!' moments",
            "unite_against_challenges": "Unite Against Common Challenges - Identify shared obstacles, mutual frustrations, collective concerns"
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for emotion targeting analysis"""
        workflow = StateGraph(EmotionTargetingState)
        
        # Add nodes
        workflow.add_node("analyze_emotions", self._analyze_emotions_node)
        workflow.add_node("validate_targeting", self._validate_targeting_node)
        workflow.add_node("format_response", self._format_response_node)
        
        # Add edges
        workflow.set_entry_point("analyze_emotions")
        workflow.add_edge("analyze_emotions", "validate_targeting")
        workflow.add_edge("validate_targeting", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _analyze_emotions_node(self, state: EmotionTargetingState) -> EmotionTargetingState:
        """Analyze each topic against the 5 emotion themes and select the best match"""
        try:
            if not state['topics']:
                state['error'] = "No topics provided for emotion analysis"
                return state
            
            emotion_analysis = []
            
            for topic in state['topics']:
                # Create prompt for this specific topic
                system_prompt = f"""<role>
Your task is to analyze the given topic and determine which of these 5 emotional themes it should target for marketing purposes
</role>

<context>
<originalContent>
{state['original_text'] if 'original_text' in state else 'Not provided'}
</originalContent>

<targetAudience>
{state.get('audience_context', 'No audience context provided')}
</targetAudience>

<coreIdea>
{topic['topic_name']}
</coreIdea>

<referenceText>
{topic['content_excerpt']}
</referenceText>
</context>

<prompt>
Using the core idea, reference text, target audience, and the context itself. Which of the following does this idea evoke and why?

Consider the target audience when selecting the emotion - different audiences will respond to different emotional appeals.

Encourage Their Dreams - Content that inspires aspiration, growth, positive future outcomes, and achievement
Justify Their Failures - Content that validates struggles, provides external explanations, removes self-blame
Allay Their Fears - Content that provides reassurance, reduces anxiety, offers safety and security
Confirm Their Suspicions - Content that validates existing doubts, provides "I knew it!" moments
Unite Against Common Challenges - Content that identifies shared obstacles, mutual frustrations, collective concerns
</prompt>

<structure>
{{
"primary_emotion": "encourage_dreams|justify_failures|allay_fears|confirm_suspicions|unite_against_challenges",
"emotion_description" : "A short description of the emotion theme",
"emotion_confidence": 0.85,
"reasoning": "The why. Detailed explanation of why this emotion theme is the best match for this topic"
}}
</structure>"""

                user_prompt = f"Analyze Topic ID {topic['topic_id']} and return the JSON response following the structure provided."
                
                try:
                    # Use a more direct approach to avoid message formatting issues
                    full_prompt = f"{system_prompt}\n\nUser Query:\n{user_prompt}"
                    response = self.llm.invoke([HumanMessage(content=full_prompt)])
                except Exception as api_error:
                    # Fallback: try with just the user prompt
                    response = self.llm.invoke([HumanMessage(content=user_prompt)])
                
                # Parse the JSON response
                try:
                    emotion_data = json.loads(response.content)
                    
                    # Validate required fields
                    if not all(key in emotion_data for key in ['primary_emotion', 'emotion_confidence', 'reasoning']):
                        raise ValueError("Missing required fields in emotion analysis")
                    
                    # Add topic information to the analysis
                    analysis_result = {
                        'topic_id': topic['topic_id'],
                        'topic_name': topic['topic_name'],
                        'content_excerpt': topic['content_excerpt'],
                        'primary_emotion': emotion_data['primary_emotion'],
                        'emotion_description': emotion_data.get('emotion_description', ''),
                        'emotion_confidence': float(emotion_data['emotion_confidence']),
                        'reasoning': emotion_data['reasoning']
                    }
                    
                    emotion_analysis.append(analysis_result)
                    
                except json.JSONDecodeError:
                    # Fallback: try to extract JSON from the response
                    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                    if json_match:
                        emotion_data = json.loads(json_match.group())
                        analysis_result = {
                            'topic_id': topic['topic_id'],
                            'topic_name': topic['topic_name'],
                            'content_excerpt': topic['content_excerpt'],
                            'primary_emotion': emotion_data.get('primary_emotion', 'encourage_dreams'),
                            'emotion_description': emotion_data.get('emotion_description', 'Default emotion description'),
                            'emotion_confidence': float(emotion_data.get('emotion_confidence', 0.5)),
                            'reasoning': emotion_data.get('reasoning', 'Analysis failed to parse properly')
                        }
                        emotion_analysis.append(analysis_result)
                    else:
                        # Complete fallback
                        analysis_result = {
                            'topic_id': topic['topic_id'],
                            'topic_name': topic['topic_name'],
                            'content_excerpt': topic['content_excerpt'],
                            'primary_emotion': 'encourage_dreams',
                            'emotion_description': 'Inspire aspiration and positive outcomes',
                            'emotion_confidence': 0.3,
                            'reasoning': 'Failed to analyze emotion - defaulted to encourage_dreams'
                        }
                        emotion_analysis.append(analysis_result)
            
            state['emotion_analysis'] = emotion_analysis
            
        except Exception as e:
            state['error'] = f"Error in emotion analysis: {str(e)}"
            state['emotion_analysis'] = []
        
        return state
    
    def _validate_targeting_node(self, state: EmotionTargetingState) -> EmotionTargetingState:
        """Validate and clean up emotion targeting results"""
        if state.get('error'):
            return state
        
        try:
            validated_analysis = []
            valid_emotions = set(self.emotion_themes.keys())
            
            for analysis in state['emotion_analysis']:
                # Validate emotion theme
                if analysis['primary_emotion'] not in valid_emotions:
                    # Default to encourage_dreams if invalid
                    analysis['primary_emotion'] = 'encourage_dreams'
                    analysis['emotion_confidence'] = max(0.1, analysis['emotion_confidence'] - 0.3)
                    analysis['reasoning'] += " (Note: Original emotion was invalid, defaulted to encourage_dreams)"
                
                # Ensure confidence is within valid range
                analysis['emotion_confidence'] = max(0.0, min(1.0, analysis['emotion_confidence']))
                
                # Clean up strings
                analysis['topic_name'] = str(analysis['topic_name']).strip()
                analysis['reasoning'] = str(analysis['reasoning']).strip()
                
                # Handle emotion_description field
                if 'emotion_description' not in analysis or not analysis['emotion_description']:
                    # Provide default emotion description based on the emotion theme
                    emotion_descriptions = {
                        'encourage_dreams': 'Inspire aspiration and positive outcomes',
                        'justify_failures': 'Validate struggles and remove self-blame',
                        'allay_fears': 'Provide reassurance and security',
                        'confirm_suspicions': 'Validate existing doubts and concerns',
                        'unite_against_challenges': 'Unite against common challenges'
                    }
                    analysis['emotion_description'] = emotion_descriptions.get(
                        analysis['primary_emotion'], 
                        'Emotional targeting for engagement'
                    )
                else:
                    analysis['emotion_description'] = str(analysis['emotion_description']).strip()
                
                # Skip only if topic_name is completely missing
                if not analysis['topic_name']:
                    continue
                
                # Provide default reasoning if missing
                if not analysis['reasoning']:
                    analysis['reasoning'] = f"Emotion analysis for {analysis['topic_name']}"
                
                validated_analysis.append(analysis)
            
            state['emotion_analysis'] = validated_analysis
            
        except Exception as e:
            state['error'] = f"Error in emotion validation: {str(e)}"
            state['emotion_analysis'] = []
        
        return state
    
    def _format_response_node(self, state: EmotionTargetingState) -> EmotionTargetingState:
        """Format the final response"""
        if state.get('error'):
            return state
        
        # Calculate processing time if not already set
        if 'processing_time' not in state:
            state['processing_time'] = 0.0
        
        return state
    
    def analyze_emotions(self, topics: List[Dict[str, Any]], audience_context: str = "") -> Dict[str, Any]:
        """Main method to analyze emotion targeting for topics"""
        start_time = datetime.now()
        
        initial_state = EmotionTargetingState(
            topics=topics,
            audience_context=audience_context,
            emotion_analysis=[],
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
                    'emotion_analysis': [],
                    'total_analyzed': 0,
                    'processing_time': processing_time
                }
            
            return {
                'success': True,
                'emotion_analysis': result['emotion_analysis'],
                'total_analyzed': len(result['emotion_analysis']),
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': False,
                'error': f"Graph execution error: {str(e)}",
                'emotion_analysis': [],
                'total_analyzed': 0,
                'processing_time': processing_time
            } 