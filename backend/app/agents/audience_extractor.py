"""Audience Extractor Agent for identifying target audience from content"""

from typing import Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AudienceExtractionState(TypedDict):
    original_text: str
    audience_summary: str
    processing_time: float
    error: str

class AudienceExtractorAgent:
    """Agent for extracting target audience from long-form content"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.2):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for audience extraction"""
        workflow = StateGraph(AudienceExtractionState)
        
        # Add nodes - simplified to just 2 steps
        workflow.add_node("input_processing", self._input_processing_node)
        workflow.add_node("extract_audience", self._audience_summary_node)
        
        # Add edges
        workflow.set_entry_point("input_processing")
        workflow.add_edge("input_processing", "extract_audience")
        workflow.add_edge("extract_audience", END)
        
        return workflow.compile()

    def _input_processing_node(self, state: AudienceExtractionState) -> AudienceExtractionState:
        """Validate and prepare input text"""
        try:
            if not state.get('original_text') or len(state['original_text'].strip()) < 100:
                state['error'] = "Text too short for audience analysis (minimum 100 characters)"
                return state
                
        except Exception as e:
            state['error'] = f"Input processing error: {str(e)}"
        
        return state

    def _audience_summary_node(self, state: AudienceExtractionState) -> AudienceExtractionState:
        """Generate audience summary directly"""
        if state.get('error'):
            return state
        
        try:
            system_prompt = f"""<context>
{state['original_text']}
</context>

<prompt>

What is the audience that is being targeted? give one core audience and why?

</prompt>

<outputExample1>

Core audience: Ambitious digital creators and knowledge workers.

Detail of the audience: This group includes freelancers, aspiring entrepreneurs, content creators (writers, designers, developers), and other online professionals who are trying to build a career on the internet. They are likely feeling overwhelmed by the "hustle culture" of constant output and are concerned about the rise of AI making their skills obsolete. They are looking for a more meaningful and sustainable path to success that values quality and individuality over sheer volume.

Why this is the audience from the original content:

- Addresses their specific activities: The text explicitly mentions skills and activities common to this audience, such as "design, marketing, coding, and copywriting," "churning out endless amounts of content," and building a "personal brand."
- Speaks to their core anxieties: It tackles the fear of being replaced by AI ("You can't compete with machines where speed matters") and the feeling of being a "cog in the machine" by producing low-quality, high-volume work.
- Offers a tailored solution: The advice to become a "digital artisan," focus on "taste" and "curation," and build a business around a unique personal story is directly applicable to someone trying to stand out in the crowded creator economy.
- Uses their language: The article uses terms and references figures (like Naval Ravikant) that are popular and influential within the tech, startup, and creator communities.

</outputExample1>

<outputExample2>

Core audience: Aspiring and current Creator-Entrepreneurs.

Detail of the audience: This group consists of individuals who are using or want to use social media and online platforms to build a business around their personal brand, knowledge, or passion. They range from beginners just starting out (like the author in his dorm room) to more established creators looking to scale their income (like Abigail Peugh). They are looking for tools, inspiration, and a roadmap to turn their followers into a sustainable business.

Why this is the audience from the original content:

- Direct Address: The author explicitly states, "I hope it helps you in navigating your own journey as a Creator-Entrepreneur!" This sets the intention of the letter for a public, creator-focused audience beyond the initial investors.
- Relatable Founder Story: The letter begins with a personal narrative of starting as a creator, filming TikToks, not knowing how to make money, and the feeling of making a "first dollar." This journey is designed to resonate directly with the struggles and aspirations of other creators.
- Focus on Creator Pain Points: The text highlights common problems that creators face, such as patching together "dozens of different subscriptions," building an email list, launching digital products, and the high cost of tools like Mailchimp. Stan is positioned as the all-in-one solution.
- Inspirational Success Stories: The letter features the success of a "Middle Class Creator," Abigail Peugh, who made over $1 million on the platform. This serves as a powerful and attainable case study for the target audience, showing them what's possible.
- Shared Language and Vision: The author talks about "passive income," "converting followers into customers," and building a world where "anyone, anywhere could make a living doing what they love," which are core goals and concepts within the creator community.

</outputExample2>

<outputFormat>
Core audience: [here]

Detail of the audience: [here]

Why this is the audience from the original content:

[here in bullets]

</outputFormat>"""

            user_prompt = "Analyze the content and identify the core target audience following the format provided."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            state['audience_summary'] = response.content.strip()
            
        except Exception as e:
            state['error'] = f"Audience summary error: {str(e)}"
        
        return state

    async def extract_audience(self, text: str) -> Dict[str, Any]:
        """Main method to extract audience from text"""
        start_time = datetime.now()
        
        initial_state = AudienceExtractionState(
            original_text=text,
            audience_summary="",
            processing_time=0.0,
            error=""
        )
        
        try:
            logger.info(f"Starting audience extraction for {len(text)} characters of text")
            
            result = self.graph.invoke(initial_state)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if result.get('error'):
                logger.error(f"Audience extraction failed: {result['error']}")
                return {
                    'success': False,
                    'error': result['error'],
                    'audience_summary': "",
                    'processing_time': processing_time
                }
            
            logger.info(f"Successfully extracted audience in {processing_time:.2f} seconds")
            return {
                'success': True,
                'audience_summary': result['audience_summary'],
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logger.error(f"Audience extraction graph execution error: {str(e)}")
            
            return {
                'success': False,
                'error': f"Graph execution error: {str(e)}",
                'audience_summary': "",
                'processing_time': processing_time
            }

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status information for health checks"""
        return {
            "agent_name": "audience_extractor",
            "status": "healthy",
            "model": "gemini-2.5-flash",
            "capabilities": ["audience_identification", "demographic_analysis"],
            "graph_nodes": ["input_processing", "extract_audience"]
        } 