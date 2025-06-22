from typing import Dict, List, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json
import time
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .topic_extractor import TopicExtractorAgent, TopicExtractionState
from .emotion_targeting import EmotionTargetingAgent, EmotionTargetingState


class OrchestratorState(TypedDict):
    """State for the orchestrator workflow"""
    # Input
    text: str
    max_topics: int
    
    # Topic extraction results
    topics: List[Dict[str, Any]]
    topic_extraction_time: float
    topic_extraction_error: Optional[str]
    
    # Emotion targeting results
    emotion_analysis: List[Dict[str, Any]]
    emotion_targeting_time: float
    emotion_targeting_error: Optional[str]
    
    # Final results
    final_results: Dict[str, Any]
    total_processing_time: float
    workflow_status: str
    error: Optional[str]


class AgentOrchestrator:
    """
    Orchestrates communication between TopicExtractor and EmotionTargeting agents
    using LangGraph for workflow management.
    """
    
    def __init__(self, temperature: float = 0.1):
        """
        Initialize the orchestrator with both agents.
        
        Args:
            temperature: Model temperature for both agents
        """
        self.temperature = temperature
        
        # Initialize both agents
        self.topic_extractor = TopicExtractorAgent(temperature=temperature)
        self.emotion_targeting = EmotionTargetingAgent(temperature=temperature)
        
        # Build the orchestration graph
        self.graph = self._build_orchestration_graph()
    
    def _build_orchestration_graph(self) -> StateGraph:
        """Build the LangGraph workflow for agent orchestration"""
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes for each step
        workflow.add_node("extract_topics", self._extract_topics_node)
        workflow.add_node("analyze_emotions", self._analyze_emotions_node)
        workflow.add_node("combine_results", self._combine_results_node)
        workflow.add_node("handle_errors", self._handle_errors_node)
        
        # Add edges
        workflow.set_entry_point("extract_topics")
        
        # Conditional edge: if topics extracted successfully, proceed to emotion analysis
        workflow.add_conditional_edges(
            "extract_topics",
            self._should_proceed_to_emotions,
            {
                "continue": "analyze_emotions",
                "error": "handle_errors"
            }
        )
        
        # Conditional edge: if emotions analyzed successfully, combine results
        workflow.add_conditional_edges(
            "analyze_emotions",
            self._should_combine_results,
            {
                "continue": "combine_results",
                "error": "handle_errors"
            }
        )
        
        # Final edges
        workflow.add_edge("combine_results", END)
        workflow.add_edge("handle_errors", END)
        
        return workflow.compile()
    
    def _extract_topics_node(self, state: OrchestratorState) -> OrchestratorState:
        """Extract topics using the TopicExtractor agent"""
        try:
            start_time = time.time()
            
            # Call the topic extractor
            topic_result = self.topic_extractor.extract_topics(
                text=state['text'],
                max_topics=state['max_topics']
            )
            
            # Update state with topic extraction results
            state['topics'] = topic_result.get('topics', [])
            state['topic_extraction_time'] = time.time() - start_time
            state['topic_extraction_error'] = None
            
            # Set workflow status
            state['workflow_status'] = 'topics_extracted'
            
        except Exception as e:
            state['topic_extraction_error'] = str(e)
            state['topics'] = []
            state['topic_extraction_time'] = 0.0
            state['workflow_status'] = 'topic_extraction_failed'
        
        return state
    
    def _analyze_emotions_node(self, state: OrchestratorState) -> OrchestratorState:
        """Analyze emotions using the EmotionTargeting agent"""
        try:
            start_time = time.time()
            
            # Call the emotion targeting agent with the extracted topics
            emotion_result = self.emotion_targeting.analyze_emotions(
                topics=state['topics']
            )
            
            # Update state with emotion analysis results
            state['emotion_analysis'] = emotion_result.get('emotion_analysis', [])
            state['emotion_targeting_time'] = time.time() - start_time
            state['emotion_targeting_error'] = None
            
            # Set workflow status
            state['workflow_status'] = 'emotions_analyzed'
            
        except Exception as e:
            state['emotion_targeting_error'] = str(e)
            state['emotion_analysis'] = []
            state['emotion_targeting_time'] = 0.0
            state['workflow_status'] = 'emotion_analysis_failed'
        
        return state
    
    def _combine_results_node(self, state: OrchestratorState) -> OrchestratorState:
        """Combine results from both agents into a unified response"""
        try:
            # Calculate total processing time
            total_time = state['topic_extraction_time'] + state['emotion_targeting_time']
            state['total_processing_time'] = total_time
            
            # Create combined results
            combined_results = {
                'workflow_summary': {
                    'status': 'completed',
                    'total_processing_time': total_time,
                    'topics_extracted': len(state['topics']),
                    'emotions_analyzed': len(state['emotion_analysis']),
                    'timestamp': datetime.now().isoformat()
                },
                'topic_extraction': {
                    'topics': state['topics'],
                    'processing_time': state['topic_extraction_time'],
                    'error': state['topic_extraction_error']
                },
                'emotion_targeting': {
                    'emotion_analysis': state['emotion_analysis'],
                    'processing_time': state['emotion_targeting_time'],
                    'error': state['emotion_targeting_error']
                },
                'integrated_results': self._create_integrated_results(state)
            }
            
            state['final_results'] = combined_results
            state['workflow_status'] = 'completed'
            state['error'] = None
            
        except Exception as e:
            state['error'] = f"Error combining results: {str(e)}"
            state['workflow_status'] = 'combination_failed'
            state['final_results'] = {}
        
        return state
    
    def _handle_errors_node(self, state: OrchestratorState) -> OrchestratorState:
        """Handle errors and create error response"""
        try:
            # Determine the error source
            if state.get('topic_extraction_error'):
                error_source = 'topic_extraction'
                error_message = state['topic_extraction_error']
            elif state.get('emotion_targeting_error'):
                error_source = 'emotion_targeting'
                error_message = state['emotion_targeting_error']
            else:
                error_source = 'unknown'
                error_message = 'Unknown error occurred'
            
            # Create error response
            error_results = {
                'workflow_summary': {
                    'status': 'failed',
                    'error_source': error_source,
                    'error_message': error_message,
                    'timestamp': datetime.now().isoformat()
                },
                'topic_extraction': {
                    'topics': state.get('topics', []),
                    'processing_time': state.get('topic_extraction_time', 0.0),
                    'error': state.get('topic_extraction_error')
                },
                'emotion_targeting': {
                    'emotion_analysis': state.get('emotion_analysis', []),
                    'processing_time': state.get('emotion_targeting_time', 0.0),
                    'error': state.get('emotion_targeting_error')
                }
            }
            
            state['final_results'] = error_results
            state['workflow_status'] = 'failed'
            state['error'] = error_message
            
        except Exception as e:
            state['error'] = f"Error handling errors: {str(e)}"
            state['workflow_status'] = 'error_handling_failed'
            state['final_results'] = {}
        
        return state
    
    def _should_proceed_to_emotions(self, state: OrchestratorState) -> str:
        """Determine if we should proceed to emotion analysis"""
        if state.get('topic_extraction_error') or not state.get('topics'):
            return "error"
        return "continue"
    
    def _should_combine_results(self, state: OrchestratorState) -> str:
        """Determine if we should combine results"""
        if state.get('emotion_targeting_error'):
            return "error"
        return "continue"
    
    def _create_integrated_results(self, state: OrchestratorState) -> List[Dict[str, Any]]:
        """Create integrated results combining topics with their emotion analysis"""
        integrated = []
        
        # Create a mapping of topic_id to emotion analysis
        emotion_map = {
            analysis['topic_id']: analysis 
            for analysis in state.get('emotion_analysis', [])
        }
        
        # Combine topics with their emotion analysis
        for topic in state.get('topics', []):
            topic_id = topic.get('topic_id')
            emotion_data = emotion_map.get(topic_id, {})
            
            integrated_topic = {
                'topic_id': topic_id,
                'topic_name': topic.get('topic_name'),
                'content_excerpt': topic.get('content_excerpt'),
                'confidence_score': topic.get('confidence_score'),
                'emotion_targeting': {
                    'primary_emotion': emotion_data.get('primary_emotion'),
                    'emotion_confidence': emotion_data.get('emotion_confidence'),
                    'reasoning': emotion_data.get('reasoning')
                } if emotion_data else None
            }
            
            integrated.append(integrated_topic)
        
        return integrated
    
    def process_text(self, text: str, max_topics: int = 10) -> Dict[str, Any]:
        """
        Main method to process text through the entire workflow.
        
        Args:
            text: Input text to process
            max_topics: Maximum number of topics to extract
            
        Returns:
            Dictionary containing the complete workflow results
        """
        try:
            # Initialize the state
            initial_state = OrchestratorState(
                text=text,
                max_topics=max_topics,
                topics=[],
                topic_extraction_time=0.0,
                topic_extraction_error=None,
                emotion_analysis=[],
                emotion_targeting_time=0.0,
                emotion_targeting_error=None,
                final_results={},
                total_processing_time=0.0,
                workflow_status='started',
                error=None
            )
            
            # Execute the workflow
            final_state = self.graph.invoke(initial_state)
            
            return final_state['final_results']
            
        except Exception as e:
            return {
                'workflow_summary': {
                    'status': 'failed',
                    'error_source': 'orchestrator',
                    'error_message': str(e),
                    'timestamp': datetime.now().isoformat()
                },
                'topic_extraction': {'topics': [], 'processing_time': 0.0, 'error': str(e)},
                'emotion_targeting': {'emotion_analysis': [], 'processing_time': 0.0, 'error': str(e)},
                'integrated_results': []
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the status of the orchestrator and its agents"""
        return {
            'orchestrator': {
                'status': 'active',
                'temperature': self.temperature,
                'graph_compiled': self.graph is not None
            },
            'topic_extractor': {
                'status': 'active' if self.topic_extractor else 'inactive',
                'temperature': self.topic_extractor.temperature if self.topic_extractor else None
            },
            'emotion_targeting': {
                'status': 'active' if self.emotion_targeting else 'inactive',
                'temperature': self.temperature  # Emotion targeting uses the same temperature
            }
        }

    async def process_text_parallel(self, text: str, max_topics: int = 10) -> Dict[str, Any]:
        """
        Process text through the workflow with topic-level parallelization.
        After topic extraction, each topic is processed independently through emotion analysis.
        
        Args:
            text: Input text to process
            max_topics: Maximum number of topics to extract
            
        Returns:
            Dictionary containing the complete workflow results
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Extract topics (sequential)
            topic_start = time.time()
            topic_result = self.topic_extractor.extract_topics(
                text=text,
                max_topics=max_topics
            )
            topic_extraction_time = time.time() - topic_start
            
            if not topic_result['success']:
                return self._create_error_response(
                    f"Topic extraction failed: {topic_result['error']}", 
                    start_time,
                    topic_extraction_time,
                    0.0
                )
            
            if not topic_result['topics']:
                return self._create_error_response(
                    "No topics were extracted from the text", 
                    start_time,
                    topic_extraction_time,
                    0.0
                )
            
            topics = topic_result['topics']
            
            # Step 2: Process each topic through emotion analysis in parallel
            emotion_start = time.time()
            tasks = []
            
            for topic in topics:
                task = self._process_single_topic_emotion(topic)
                tasks.append(task)
            
            # Execute all emotion analysis tasks in parallel
            emotion_results = await asyncio.gather(*tasks, return_exceptions=True)
            emotion_targeting_time = time.time() - emotion_start
            
            # Process results
            emotion_analysis = []
            failed_topics = []
            
            for i, result in enumerate(emotion_results):
                if isinstance(result, Exception):
                    failed_topics.append(f"Topic {topics[i]['topic_id']}: {str(result)}")
                elif result['success']:
                    emotion_analysis.append(result['emotion_analysis'])
                else:
                    failed_topics.append(f"Topic {topics[i]['topic_id']}: {result['error']}")
            
            # Check if any topics failed
            if failed_topics:
                return self._create_error_response(
                    f"Emotion analysis failed for some topics: {'; '.join(failed_topics)}",
                    start_time,
                    topic_extraction_time,
                    emotion_targeting_time
                )
            
            # Create combined results
            total_time = topic_extraction_time + emotion_targeting_time
            
            combined_results = {
                'workflow_summary': {
                    'status': 'completed',
                    'total_processing_time': total_time,
                    'topics_extracted': len(topics),
                    'emotions_analyzed': len(emotion_analysis),
                    'timestamp': datetime.now().isoformat(),
                    'parallelization': 'topic_level'
                },
                'topic_extraction': {
                    'topics': topics,
                    'processing_time': topic_extraction_time,
                    'error': None
                },
                'emotion_targeting': {
                    'emotion_analysis': emotion_analysis,
                    'processing_time': emotion_targeting_time,
                    'error': None,
                    'parallel_execution': True
                },
                'integrated_results': self._create_integrated_results_parallel(topics, emotion_analysis)
            }
            
            return combined_results
            
        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds()
            return self._create_error_response(
                f"Parallel orchestrator execution failed: {str(e)}",
                start_time,
                0.0,
                0.0
            )

    async def _process_single_topic_emotion(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process emotion analysis for a single topic in a thread pool
        """
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                emotion_result = await loop.run_in_executor(
                    executor,
                    self.emotion_targeting.analyze_emotions,
                    [topic],  # Pass as list since method expects list
                    ""  # No audience context in basic orchestrator
                )
            
            if emotion_result['success'] and emotion_result['emotion_analysis']:
                return {
                    'success': True,
                    'emotion_analysis': emotion_result['emotion_analysis'][0]  # Get first result
                }
            else:
                return {
                    'success': False,
                    'error': emotion_result.get('error', 'Unknown emotion analysis error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Emotion analysis execution error: {str(e)}"
            }

    def _create_integrated_results_parallel(self, topics: List[Dict[str, Any]], emotion_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create integrated results for parallel processing"""
        integrated = []
        
        # Create a mapping of topic_id to emotion analysis
        emotion_map = {
            analysis['topic_id']: analysis 
            for analysis in emotion_analysis
        }
        
        # Combine topics with their emotion analysis
        for topic in topics:
            topic_id = topic.get('topic_id')
            emotion_data = emotion_map.get(topic_id, {})
            
            integrated_topic = {
                'topic_id': topic_id,
                'topic_name': topic.get('topic_name'),
                'content_excerpt': topic.get('content_excerpt'),
                'confidence_score': topic.get('confidence_score'),
                'emotion_targeting': {
                    'primary_emotion': emotion_data.get('primary_emotion'),
                    'emotion_confidence': emotion_data.get('emotion_confidence'),
                    'reasoning': emotion_data.get('reasoning')
                } if emotion_data else None
            }
            
            integrated.append(integrated_topic)
        
        return integrated

    def _create_error_response(self, error_message: str, start_time: datetime, topic_time: float, emotion_time: float) -> Dict[str, Any]:
        """Create standardized error response"""
        total_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'workflow_summary': {
                'status': 'failed',
                'error_source': 'orchestrator',
                'error_message': error_message,
                'timestamp': datetime.now().isoformat(),
                'total_processing_time': total_time
            },
            'topic_extraction': {
                'topics': [], 
                'processing_time': topic_time, 
                'error': error_message if topic_time == 0 else None
            },
            'emotion_targeting': {
                'emotion_analysis': [], 
                'processing_time': emotion_time, 
                'error': error_message if emotion_time > 0 else None
            },
            'integrated_results': []
        } 