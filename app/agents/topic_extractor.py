from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
import google.generativeai as genai
import json
import re
import os
from datetime import datetime


class TopicExtractionState(TypedDict):
    text: str
    max_topics: int
    topics: List[Dict[str, Any]]
    processing_time: float
    error: str


class TopicExtractorAgent:
    def __init__(self, temperature: float = 0.1):
        """
        Initialize the TopicExtractorAgent with Gemini (free tier).
        
        Args:
            temperature: Model temperature (0.0 to 1.0)
        """
        self.temperature = temperature
        
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not found or not set properly. "
                "Please add your Google AI API key to the .env file: "
                "GOOGLE_API_KEY=your_actual_api_key_here"
            )
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize Gemini model (free tier)
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.model.temperature = temperature
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model: {str(e)}")
        
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
        """Extract topics from the input text using Gemini"""
        try:
            system_prompt = """You are a topic extraction expert. Extract distinct topics from the given text.
            <role>
You are a content analyst with 10 years of experience. You specialize in transforming long-form content into concise, high-impact short-form pieces.
</role>

<content>
</content>

<example>
<contentExample>
The Creator Economy is a wasteland.

Once the darling of the VC hype cycle, it’s failed to live up to expectations.

We’re seeing layoffs across the board, VC funding has dried up, and views have taken a nosedive.

Dozens of Creator Economy startups have shut down. Should we be worried?

More painfully though, we’re seeing Creators burn out left and right as the constant pressure from platforms like Instagram and TikTok pushes them to the brink.

We were promised the future of work: a career where you got paid to work on your own terms, doing what you love.

Instead, we got dancing thirst traps and overfunded startups.

So where did it all go wrong?

And how do we save the Creator Economy?

### **A Glimmer of Hope**

Fortunately, things aren’t anywhere near as bleak as they seem.

In fact, we’re seeing extremely bright spots here at Stan.

Specifically, we’re seeing an *entirely* *new* class of Creators emerge that I believe will pioneer the future of the Creator Economy.

We’ve seen this emerging class of Creators launch durable, six-figure businesses while building a life on their own terms: maximizing time with their family, finding fulfillment in their work, *and* making a lot of money.

They’ve pioneered a sustainable business model that the entire Creator Economy needs to adopt if we’re to survive this so-called ‘Winter’.

But in order to explain to you how this emerging class of Creators has succeeded in spite of the rest of the market’s struggles, I first need to explain why the Creator Economy hasn’t worked out so far.

And why so many Creator startups are going out of business…

### **The Dirty Secret of the Creator Economy**

I believe that being a Creator is the *most* difficult form of entrepreneurship.

As a Creator, not only are you required to create quality content week-after-week.

But you’re also required to build a successful business.

Both of these tasks are independently difficult, so when you layer on the emotional toil that comes with putting yourself online, you start to see how building a Creator Business becomes a near-impossible task.

Creators are tasked with being ‘Solopreneurs’: they’re their own boss, manager, agent, producer, business builder, and CEO.

90%+ of entrepreneurs fail building a *regular* business — so how can we expect a Creator business, with its added complexity, to fare any better?

It’s why we’ve only seen a certain kind of Creator succeed long-term: those that are strong on *both* sides of their brain — they’re able to channel their creative right side, as well as their logical left.

Unfortunately, this is a combination we rarely witness:

We all know starving artists.

And we all know robotic businesspeople.

But rarely do we encounter a “Creator-Entrepreneur”: the exceptional artist who also relentlessly gets s*** done , day in and day out.

I often tell Creators they need to be Taylor Swift: a talented creative, and an even savvier marketer.

But the difficulty of building a Creator Business extends beyond the sheer demand it places on the Creator.

Creator Businesses are also difficult to grow.

By definition, a Creator Business’ success is tied to the output of the underlying Creator.

And because a single human can only do so much, Creator Businesses face roadblocks like:

1. **Solopreneur Risk:** Creators are under an immense amount of pressure as both the Business’ CEO and its Brand. If the Creator burns out, then there is no Business. It’s crucial that Creators take care of themselves vigilantly.
2. **Difficulty to Scale:** Creators are often one-person teams, which means they are constantly the bottleneck for ‘scale’. Creators must learn how to delegate and scale teams if they are to break through the seven-figure mark.
3. **Platform Risk:** Creators have historically depended on the Platforms (YouTube, Instagram, TikTok) for distribution; too often I have seen a Creator’s engagement evaporate due to algorithmic shifts outside of their control.
4. **Fickle Revenue Streams:** Creators often make the mistakes of relying primarily on ad and brand deal revenue for income; this kind of ‘3rd party' income is low quality and fickle. The only Creators we’ve seen that have built durable, long-term businesses are those who create and sell their own branded products.

If we were to look at today’s Creator Businesses through the lens of an investor - we’d almost certainly say no. Today’s Creator Businesses have:

1. High Founder Burnout Risk
2. Limited Scalability
3. High Platform Risk
4. Inconsistent Revenue Streams

Mark Cuban would likely say… “I’M OUT”…

All of this points to how building a Creator Business is an extremely uphill battle.

And leads us to calling out the dirtiest secret of the Creator Economy:

***The Dirty Secret of the Creator Economy: In their current form, Creator Businesses are Fundamentally Bad Businesses***

So when we reflect on why all of these startups didn’t work out — it starts to become obvious.

How possibly could startups in the Creator Economy make money when the underlying Creators themselves weren’t making any money?

Until we find a way for Creators to generate a sustainable living for themselves, no other part of the Creator Economy can thrive.

And this is why we’re so obsessed with solving the Creator Monetization problem here at Stan — if we can figure out a model for how Creators can generate a sustainable, long-term income, then we can truly build a Creator Economy we’re proud of.

Fortunately for us, we’re not in this alone.

We’re lucky to get to support a generation of talented Creators who are already pioneering a new model forward…

### **“Creator-Entrepreneurs”: A New Hope**

For all of the shouting of a reckoning, I’d actually argue that there’s never been a better time to be building in the Creator Economy.

What we’re seeing right now isn’t so much a “winter” as it is a reset back to reality.

The fundamentals of the Creator Economy are healthier than ever.

And there’s an emerging class of Creators that’s proving this out.

The fundamentals of the Creator Economy are healthier than ever: Social Media is eating the world. Everyone wants to work for themselves. And Creators are becoming the new Brands.

These are the Creators we proudly call “Creator-Entrepreneurs”, and they’re solving all of the problems of scalability and inconsistent revenue that I had mentioned before.

They are gritty, hardworking small business owners — and I believe that they are the future of the Creator Economy.

They see social media not just as a way to creatively express themselves, but also as a keen business opportunity.

And they’ve already started to solve many of the challenges Creator Businesses have historically struggled with:

- **They’re building their own Platforms:** Creators like Coach Benny, a dating coach, are circumventing Platform Risk by using Stan to build their own email lists & private communities, owning their audience on their own terms rather than being gated by an algorithm
- **They’re building consistent, recurring income streams:** Creators like Guided Fit Mama, a personal trainer, are using Stan to building passive, recurring income streams through memberships, paid communities, and courses that bring in income even when the Creator isn’t posting
- **They’re scaling into multiple-person operations:** Creators like Austin Hankwitz, a finance Creator, have used the funds they’ve made from Stan to employ a whole team (including a COO and video editors) in order to scale their own output
- **They’re beating burnout:** We have hundreds of Creators within the #StanFam self-organizing community meetups and finding healthy balances between daily content output and living a life outside of their screens

Here at Stan, we believe that the key to a thriving economy is a thriving middle class.

And fortunately, these Creator-Entrepreneurs are building the Creator Middle Class.

---

Take Creators like Abigail Peugh for example.

Abigail isn’t a glitzy, LA influencer dancing on camera.

She’s a mom, wife and kind-hearted entrepreneur who’s made over $400k on Stan in just the last 12 months.

Abigail’s story is incredible: 1 year ago, Abigail’s husband lost his job due to a stroke; she started posting in June 2022 and has since retired her husband while still being an incredible Stay-at-Home Mom

She’s built a business not off of views and follower count, but by putting in the work to build multiple income streams.

She’s circumvented Platform Risk by building an email list.

And then, she’s used that email list to build Consistent Income for herself by offering her audience easily consumable digital products with a frictionless checkout process.

Astutely, she’s created multiple products priced at different price points in order to serve her audience across their *entire* customer journey, which increases her Customer’s Lifetime Value far beyond if she sold only one product.

From there, she’s supplemented this passive income with a more recurring income stream: her high ticket coaching membership.

And the best part? She’s accomplished all of this while still getting to be present with her daughter as a stay-at-home-mom.

So as we think about what business model the Creator Economy needs to thrive, our Creator-Entrepreneurs have charted us a clear path forward:

1. **Creators Must Own Their Audience:** Creators need to build a *direct* relationship with their audiences, either through email, SMS, or private community. Living and dying by an algorithm is not an acceptable proposition.
2. **Creators Must Build Sustainable Businesses:** Creators need to be able to take time off without worrying about their business. They also need to find a healthy relationship with social media. Both of these are only possible if a Creator builds a sustainable business, which requires both of the below.
3. **Creators Must Create Passive Income Streams:** Creators need as much passive income as possible to supplement their main focus — creating. Leveraging “build once, sell multiple times” products like digital products (ebooks, courses) is the critical lever we’ve seen our most successful Creators use.
4. **Create Must Scale Beyond Themselves:** There are huge opportunities for Creators to use generative AI to create content. And the Creators who learn how to scale a team will be able to watch their brand grow beyond them.
    
    I share all of my learnings scaling as Creator and CEO, just once a month:
    
    **Subscribe**
    

### **The Opportunity Ahead**

When people ask me why I’m not worried about the short-term blips we’re seeing right now, I point to this.

I point to the thousands of Creator-Entrepreneurs that are pioneering an entirely new way to do business: one where you can use social media to build a direct relationship with your target customer, build your own brand, and do it all on your own terms.

When I see this, I get so amped about the future of the Creator Economy.

If we can make the ‘Creator-Entrepreneur’ business model accessible to everyone, then we have an opportunity to build a Creator Economy we’re truly proud of — one where *anyone*, *anywhere* can make a living working for themselves.

So to our Creators, this is my promise to you:

We will not rest until we have done everything possible to support you in your business — the software, the coaching, the mental health resources, and the community.

You name it, we’re going to build it.

Let’s do this. 😤

*P.S. for those of you who believe in the future of the Creator Economy as much as we do here at Stan - and want to play a defining role in pushing it forward - we’re hiring!*
</contentExample>

```
<outlineExtracted>
  <idea>
  The creator economy’s promised freedom has collapsed into burnout, shuttered startups, and vanished VC money.
  </idea>
  <whereFound>
  The Creator Economy is a wasteland.

  Once the darling of the VC hype cycle, it’s failed to live up to expectations.

  We’re seeing layoffs across the board, VC funding has dried up, and views have taken a nosedive.

  Dozens of Creator Economy startups have shut down. Should we be worried?

  More painfully though, we’re seeing Creators burn out left and right as the constant pressure from platforms like Instagram and TikTok pushes them to the brink.

  We were promised the future of work: a career where you got paid to work on your own terms, doing what you love.

  Instead, we got dancing thirst traps and overfunded startups.

  So where did it all go wrong?

  And how do we save the Creator Economy?
  </whereFound>
</outlineExtracted>

```

</example>

<instructions>
You are to take the content and extract out the outline of what the writer is trying to talk about. This outline is the flow of what they want to say. You will look for a section (this is where you find the core idea), then you summarize the idea from it.
</instructions>

<structure>

</structure>
IMPORTANT: Respond with ONLY a valid JSON array. No other text or formatting.

Format each topic as:
{{
  "topic_name": "clear topic name",
  "content_excerpt": "relevant text excerpt", 
  "confidence_score": number between 0.0 and 1.0
}}

Extract 1 to {max_topics} topics. Each topic should be distinct and meaningful.

Example response:
[
  {{
    "topic_name": "Artificial Intelligence",
    "content_excerpt": "AI has revolutionized problem-solving in various industries.",
    "confidence_score": 0.95
  }}
]

CRITICAL: You must respond with ONLY the JSON array. Do not include any explanations, markdown formatting, or additional text. Start with [ and end with ]."""

            user_prompt = f"Extract topics from this text:\n\n{state['text']}"
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt.format(max_topics=state['max_topics'])}\n\n{user_prompt}"
            
            # Call Gemini directly
            try:
                response = self.model.generate_content(full_prompt)
                response_text = response.text
            except Exception as llm_error:
                raise ValueError(f"Gemini API call failed: {str(llm_error)}")
            
            # Parse the JSON response
            try:
                topics_data = json.loads(response_text)
                if not isinstance(topics_data, list):
                    raise ValueError("Response is not a list")
                
                # Add topic IDs
                topics_with_ids = []
                for i, topic in enumerate(topics_data, 1):
                    topic['topic_id'] = i
                    topics_with_ids.append(topic)
                
                state['topics'] = topics_with_ids
                
            except json.JSONDecodeError as json_error:
                # Fallback: try to extract JSON from the response
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        topics_data = json.loads(json_match.group())
                        topics_with_ids = []
                        for i, topic in enumerate(topics_data, 1):
                            topic['topic_id'] = i
                            topics_with_ids.append(topic)
                        state['topics'] = topics_with_ids
                    except json.JSONDecodeError:
                        raise ValueError(f"Could not parse JSON response from Gemini. Raw response: {response_text[:200]}")
                else:
                    raise ValueError(f"Could not extract JSON from Gemini response. Raw response: {response_text[:200]}")
                    
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
            
            # Limit to max_topics
            state['topics'] = validated_topics[:state['max_topics']]
            
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
    
    def extract_topics(self, text: str, max_topics: int = 10) -> Dict[str, Any]:
        """
        Main method to extract topics from text using Gemini.
        
        Args:
            text: The input text to analyze
            max_topics: Maximum number of topics to extract (default: 10)
            
        Returns:
            Dictionary with extraction results:
            {
                'success': bool,
                'topics': List[Dict],
                'total_topics': int,
                'processing_time': float,
                'error': str | None
            }
        """
        start_time = datetime.now()
        
        initial_state = TopicExtractionState(
            text=text,
            max_topics=max_topics,
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