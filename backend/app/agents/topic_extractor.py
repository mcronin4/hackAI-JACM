from typing import Dict, List, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re
from datetime import datetime


class TopicExtractionState(TypedDict):
    text: str
    topics: List[Dict[str, Any]]
    processing_time: float
    error: str


class TopicExtractorAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.1):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for topic extraction"""
        workflow = StateGraph(TopicExtractionState)
        
        # Add nodes
        workflow.add_node("extract_topics", self._extract_topics_node)
        workflow.add_node("validate_topics", self._validate_topics_node)
        workflow.add_node("format_response", self._format_response_node)
        
        # Add edges
        workflow.set_entry_point("extract_topics")
        workflow.add_edge("extract_topics", "validate_topics")
        workflow.add_edge("validate_topics", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _extract_topics_node(self, state: TopicExtractionState) -> TopicExtractionState:
        """Extract topics from the input text using LLM"""
        try:
            system_prompt = """You are an expert topic extraction agent. Your task is to analyze the given text and identify distinct topics.

For each topic, provide:
- A clear, concise topic name
- A relevant excerpt from the text that demonstrates this topic
- A confidence score (0.0 to 1.0) for how well this topic is represented

Guidelines:
- Extract 2-5 meaningful topics from the text
- Each topic should be distinct and meaningful
- Excerpts should be 1-3 sentences that best represent the topic
- Topics should cover the main themes and subjects in the text
- Avoid overlapping or redundant topics

Return your response as a valid JSON array with this exact structure:
[
  {
    "topic_name": "string describing the topic",
    "content_excerpt": "relevant text excerpt", 
    "confidence_score": 0.85
  }
]

Only return the JSON array, no additional text or formatting."""

            user_prompt = f"Extract topics from this text:\n\n{state['text']}"
            
            # Use a more robust message construction
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_content = response.content.strip()
            
            # Parse the JSON response with better error handling
            try:
                # Try direct JSON parsing first
                topics_data = json.loads(response_content)
                if not isinstance(topics_data, list):
                    raise ValueError("Response is not a list")
                
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from the response
                json_match = re.search(r'\[.*?\]', response_content, re.DOTALL)
                if json_match:
                    try:
                        topics_data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        raise ValueError("Could not parse JSON from LLM response")
                else:
                    # If no JSON found, create a fallback topic
                    topics_data = [{
                        "topic_name": "Main theme from the provided text",
                        "content_excerpt": state['text'][:200] + "..." if len(state['text']) > 200 else state['text'],
                        "confidence_score": 0.7
                    }]
            
            # Add topic IDs and validate structure
            topics_with_ids = []
            for i, topic in enumerate(topics_data, 1):
                if isinstance(topic, dict) and 'topic_name' in topic:
                    validated_topic = {
                        'topic_id': i,
                        'topic_name': str(topic.get('topic_name', f'Topic {i}')),
                        'content_excerpt': str(topic.get('content_excerpt', state['text'][:100])),
                        'confidence_score': float(topic.get('confidence_score', 0.8))
                    }
                    topics_with_ids.append(validated_topic)
            
            # Ensure we have at least one topic
            if not topics_with_ids:
                topics_with_ids = [{
                    'topic_id': 1,
                    'topic_name': 'Main theme from the provided text',
                    'content_excerpt': state['text'][:200] + "..." if len(state['text']) > 200 else state['text'],
                    'confidence_score': 0.7
                }]
            
            state['topics'] = topics_with_ids
                    
        except Exception as e:
            state['error'] = f"Error in topic extraction: {str(e)}"
            state['topics'] = []
        
        return state
    
    def _validate_topics_node(self, state: TopicExtractionState) -> TopicExtractionState:
        """Validate and clean up extracted topics"""
        if state.get('error'):
            return state
        
        try:
            validated_topics = []
            for topic in state['topics']:
                # Ensure required fields exist
                if not all(key in topic for key in ['topic_id', 'topic_name', 'content_excerpt']):
                    continue
                
                # Clean and validate topic data
                validated_topic = {
                    'topic_id': int(topic['topic_id']),
                    'topic_name': str(topic['topic_name']).strip(),
                    'content_excerpt': str(topic['content_excerpt']).strip(),
                    'confidence_score': float(topic.get('confidence_score', 0.8))
                }
                
                # Skip if topic name or excerpt is empty
                if not validated_topic['topic_name'] or not validated_topic['content_excerpt']:
                    continue
                
                validated_topics.append(validated_topic)
            
            # Keep all validated topics (no artificial limit)
            state['topics'] = validated_topics
            
        except Exception as e:
            state['error'] = f"Error in topic validation: {str(e)}"
            state['topics'] = []
        
        return state
    
    def _format_response_node(self, state: TopicExtractionState) -> TopicExtractionState:
        """Format the final response"""
        if state.get('error'):
            return state
        
        # Calculate processing time if not already set
        if 'processing_time' not in state:
            state['processing_time'] = 0.0
        
        return state
    
    def extract_topics(self, text: str) -> Dict[str, Any]:
        """Main method to extract topics from text"""
        start_time = datetime.now()
        
        initial_state = TopicExtractionState(
            text=text,
            topics=[],
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
                    'topics': [],
                    'total_topics': 0,
                    'processing_time': processing_time
                }
            
            return {
                'success': True,
                'topics': result['topics'],
                'total_topics': len(result['topics']),
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'success': False,
                'error': f"Graph execution error: {str(e)}",
                'topics': [],
                'total_topics': 0,
                'processing_time': processing_time
            } 