import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.content_pipeline import ContentPipelineService, ContentPipelineError
from app.models import Topic, EnhancedTopic, GeneratedContent
import asyncio


class TestContentPipelineService:
    """Test suite for the unified content pipeline service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ContentPipelineService()
        
        # Mock data
        self.sample_text = """But most people go about this the wrong way.

They are still learning skills and building projects for the old paradigm of work.

They launch 10 startups. They churn out endless amounts of content. They stack skills like design, marketing, coding, and copywriting because they think that will increase their value to the point of making more money.

They’re obsessed with output at the expense of what’s worth putting out.

They do many things with poor quality rather than one thing with undeniable quality.

We’re experiencing the death of thoughtful creation. The world is being filled with more factories rather than gardeners. Why?

Because creation has never been more accessible.

You can type a sentence into AI and have it spit out a mobile app.
You can generate a month’s worth of content in a day and schedule it to all social platforms.
You can drag an image into ChatGPT, turn it into a prompt, and recreate it in your own style.
The future of work is a battle between speed and art. When anyone can create anything at the click of a button, it loses all value at the click of a button, and we no longer value ourselves because we are deeply aware that we sold our soul to the mechanical life machines were meant to help us escape.

You can’t compete with machines where speed matters.

That leaves humans with the domains of meaning, play, and signal.

If you want to get ahead of everyone else, the answer doesn’t lie in churning out an infinite amount of content in hopes that you’ll win the numbers game. Instead, the answer lies in less.

Consuming less. Producing less. Doing less.

It sounds counterintuitive, but this isn’t anything new.

It’s how the world’s most successful creatives, strategists, and visionaries created the books, products, and scientific and cultural breakthroughs that have persisted throughout history.

Robots Work, Humans Play
The elegance of the future is not in man versus machine but in their division of labor: silicon sanding the rough edges of necessity so carbon can ascend to meaning. We will abolish baristas and canonize chefs, silence agents and encore actors. It is the same selfish instinct in both arenas—purge friction, preserve narrative—driving a world where the driest chores are done by circuits and the juiciest stories are told by people who bleed.

– Chris Paik

To understand where humans will thrive, we must first look at where they won’t.

When the task is about speed, accuracy, or utility, humans become a massive inconvenience. These are the driving forces of automation.

We can’t stand the server who writes down your order but still gets it wrong. The long lines at the DMV just to be met by a worker who declines your request because they’re in a bad mood. The Uber driver who tries to make small talk when you’re late for a meeting.

But when our mind leaves the state of needing to do something for the sake of a perfect outcome – when we engage in leisure – we crave something entirely different.

We crave something interesting.

We crave the potential for failure.

We crave the very thing that our mind runs on:

Story. Drama. Novelty. Myth and meaning. We pay good money for it, too.

Rather than the Starbucks barista who makes us a quick pick me up that often tastes like the beans were roasted in the fire of hell, we drive out of our way to visit the warm local coffee shop where the owner knows you by name.

While we prefer to have a quick bite delivered to our front door without seeing the other person, we travel across the world for the best food imaginable in a location we’ve always dreamed of visiting.

During work, we want bullet point summaries. During a wedding, we want handwritten vows. AI can throw a perfect ball, yet we pack stadiums and can’t pull our attention away from the final batter in the ninth inning.

But that doesn’t eliminate the necessity of work. We still need work to be done if we want to control our leisure. The solution then is to leverage machines to reduce what we perceive as work and increase our time spent in leisure to produce a meaningful story worth sharing with the world.

In other words, you become irreplaceable through risk and story, then embed it in everything you create. You embrace failure as the fuel to becoming irreplaceable.

This is one hidden fact about history. Advancements in technology have freed up room for leisure, allowing people to discover and pursue new interests. Unfortunately, parents and schooling with values of past generations convinced us that it was noble to work more, without realizing they were setting us up for a mediocre life.

In early Agrarian societies, when the horse-drawn plow was invented, leading to a surplus in food, individuals had the free time to invent mathematics and writing. This was the first time in history when a large number of people could engage in such activities, including deep contemplation, leading to the Axial period, which birthed the philosophies from Gautama Buddha, Lao Tzu, Socrates, and more.

In comes the Industrial Age, and while many still endure grueling and meaningless work, we have sports, film, content creation, artisan shops, and deep experiences available as “work.” Play-centric jobs – or callings – aren’t anything new. And artisan work that could be automated isn’t purchased for the sake of speed and convenience. Sure, many people burn themselves out in these jobs because they’ve lived in a state of survival so long it’s become who they are, but many others see these less as jobs and more as a way of life.

A leisure economy has been emerging right before our eyes.

Further, if we look at Steve Jobs, Charles Darwin, and the various thinkers who’ve changed the world with their creations, we learn that the pinnacle of their creative ability stemmed from rest, walks, and leisure. Leisure, for all I’m concerned, is the process of discovery and exploration. The act of pursuing your own interests.

As robots eliminate work, humans ascend to play.

The Greatest Skill Isn’t Creation, It’s Curation
You and I are not like cows. We’re not meant to graze all day. We’re meant to hunt like lions. We’re closer to carnivores in our omnivorous development than we are to herbivores. As an intellectual athlete, you want to function like an athlete. Which means you train hard, then you sprint, then you rest, then you reassess. This idea that you’re going to have linear output just by cranking every day at the same amount of time sitting… That’s machines. Machines are meant to work 9-5, not humans.

— Naval

The work we choose defines who we are.

And if we choose to engage in a system with the goal of efficiency and optimization, we become that goal. We become a cog in the machine. This paints a brutal picture of hyper-specialization. When you narrow your mind to one dimension, you become a slave to it.

Before industrialization, slaves were expected to perform a small set of tasks for the entirety of their lives. Around 80% of free American workers, on the other hand, were self-employed farmers or artisans. They were expected to pursue their interests and do many things throughout their lives, because they were expected to direct their own labor. Today, only about 10% of Americans are self-employed.

The Industrial Revolution (think schools and mass employment) changed our relationship to work. Slowly, then all at once, millions of people were moved into work with predefined tasks mediated by the direction of others.

Just like that, self-governance as a value disappeared, and we willingly set ourselves up to be replaced by a machine.

No matter how much I think it through, and I’ve spent the past 5 years writing about this, the primary solution for most people, especially those who desire creativity and autonomy, is to become a modern artisan. A digital artisan, that is. A savant in the age of information.

A radical shift from producing for someone else to producing for yourself.

It’s cliche at this point, and worth stating as a reminder, but never before have you had access to the tools, resources, and people required to sustain artisan-level work that feels like play. You don’t need to be the next billionaire, you simply need to survive (with a little breathing room).

You can access any information.

You can build anything without years of acquiring the skill.

You can garner the attention of an audience of supporters to get paid for being yourself.

AI can churn out infinite content at the click of a button, and that’s the point.

Remember, you can’t compete with a machine when it comes to speed and utility. When someone wants unbiased news and pure “how to” advice, they will search for it and be annoyed with any type of friction. AI-generated content can be extremely useful when we need information fast.

But when we aren’t searching for anything specific, which is most of the time, we crave something different.

We read a fiction book. We throw on a video about an interesting idea. We listen to a podcast with two of our favorite personalities. We listen to new music. We crave a story, an idea, a signal in the noise that lights our brain on fire.

In the realm of wisdom, insight, depth, and meaning – robots have no business.

We care about what other people have put care into.

If the local coffee shop were going to be put out of business due to cost and speed, it would have already, yet they’re filled to the brim despite their $7 cup of coffee.

It doesn’t matter if it costs Hermes $300 to make a handbag that sells for $80,000. What matters is the brand. The story. The who. The craftsmanship and detail. That’s what people pay a premium for. The fact that China can create the same luxury goods for a few bucks is only relevant to the wrong audience.

But there’s another reason – a replicable reason – behind why people are willing to spend their hard-earned cash on artisanal goods:

Taste.

When anyone can create anything, discernment and restraint matter. Curation begins to matter more than creation. Memorizing academic facts and being a library of information isn’t a status symbol anymore. What matters are the limited ideas that you choose to occupy your mind.

The question is no longer about if you can make it.

It’s whether or not you should.

How To Develop And Deploy Taste
To develop taste, you need to build something of your own, because taste can’t be outsourced.

Taste is a skill that comes with practice and dedication to your craft.

This alone explains why most people are falling behind. They’re obsessed with quantity instead of quality. They create to make money rather than make money to create. They learn any skill that promises quick money, and we all know how that ends up.

You need a purpose as a filter for the faucet of information that we’re over-exposed to on a daily basis. You need to be ruthless with who and what has access to your mind. You need to normalize the fact that text messages, social media feeds, and unprecedented access to the silence that breeds creativity is not something our brains are wired for.

People with good taste have a mind that rejects information that feels off. They look at a design, product, or post and feel that there is something missing, that something needs to be scrapped altogether, or that it shouldn’t have been a thing in the first place.

The greatest minds of our time are not consuming more. Because quality outputs stem from quality inputs. What you give your attention to shapes how you think, and when you don’t choose what you are building or who you are building for, you become a slave. Not physical, but mental. Your creativity is both stifled and exhausted through work directed by anyone but yourself.

When machines can think about everything all at once, our job is to have standards.

To filter the information we allow into our brain.

To curate the ideas that deserve to be crafted.

To choose the work that we can’t pull ourselves away from.

But how? All of this sounds nice and insightful, but how do we actually do this?

How do we direct our own career with taste as our north star?

Prioritize Risk, Iteration, and Craft
Don’t focus on what you are good at.

Focus on what you do uniquely, and that can only be uncovered through doing, not thinking.

You discover where your uniqueness lies in creating a story worth sharing with others. Your personal story, stemming from your personal consciousness that nobody – not even AI – has access to in its entirety, is the most unique thing on this planet. You will find it difficult to compete in the future if you lean into anything other than the interesting string of failures and successes that bring a relatable yet novel perspective to anything you create.

The only way to create a story worth telling is to prioritize risk. To make a deliberate choice in the direction you take. To avoid conforming to anyone, anything, any belief, or any worldview and instead create your own path through the rejection and questioning of those things.

Beyond that, taste is born through iteration.

It’s a never-ending process. I thought the first newsletter I wrote was pretty good, but when I look back, it’s the most disgusting thing I’ve seen in my life. I think my newsletters are pretty good now, and while they’re much better than what they used to be, I’ll look back in a year

A designer, filmmaker, or programmer can look back on past iterations of their work and notice a tangible difference in the development of their taste.

People who never start, or quit after two weeks, will never make it for this reason. You may think you have taste… I mean it’s easy to look at something in the world and agree that something was made with taste, but when you sit down to replicate it, you’ll notice that the delta between yours and theirs is vast.

It doesn’t matter how much you study, when you start, taste starts increasing from zero.

Create Something With Care, Until You Care
Following your passion is bad advice.

Not because it’s wrong, but because it’s misleading.

You don’t follow your passion. You cultivate it by doing something with enthusiasm for a long enough time until discover the depth of that craft, leading to a burning passion for it. You generate passion in the pursuit of a goal you may not have wanted to pursue, but you saw it as necessary to reach the life you want, so you shut your mind off and did it anyway.

The first step to becoming irreplaceable is to set aside at least one hour a day for pure craftsmanship. In other words, building a project. A creation. Something that both you and others can use and benefit from. This is a critical shift from consumer to producer that must happen.

It doesn’t matter what this project is because any career or job-specific skill you learn now won’t matter in the future. You build a project for the development of agency and taste, not the monetary outcome of performing with speed and accuracy in the marketplace.

A meaningful project shapes who you are and how you think. It literally rewires your mind. It teaches you how to learn. It silently builds the soft skills necessary for the future like perception, adaptability, and resilience. It forces you to focus on acquiring techniques between various skills rather than a career-specific skill, which transfers over into anything else you create.

Garner Attention, Build Trust
You can start a local business.

You can create physical products or goods.

But for those reading this, I’m confident that 95% or more of you have a creative edge. You understand the leverage that can be built on the internet. You see how the digital world allows you to direct your own career. With that, the project you build should reflect that.

You don’t need capital to set up shop online. You don’t need to be in the right physical location to connect with the right people. You don’t need a record label, publisher, or employer to give you work. But you do need attention and trust.

Remember, anyone can create anything. That is one of the most liberating statements we’ve ever been able to say with confidence.

In that case, how do you stand out?

By integrating everything we’ve talked about so far.

First, build a personal brand, or a brand with personality, and publish your work in public. Your story must be front and center.

Second, curate your inputs for tasteful outputs. Become a beacon of signal in a world of unbearable noise. Pursue your interests and share ideas you care about. Soon enough, and with the right amount of iteration, others will care, too.

Third, build a meaningful project and turn it into a product. Music. Writing. Designs. Software. Anything. Because the brutal reality is: If you don’t sell a product, you will be forced to sell a product for someone else. Your labor, and thus your mind, will be directed by someone else. In order to sell a product, you need attention, but you don’t need to sell your soul to do so.

Give yourself 6-12 months.

2-4 hours a day of pure focus.

I can’t give you the path, because you can’t replicate my story.

I am confident that I’ve given the right people enough to work with to figure it out.

Good luck.

– Dan"""
        self.sample_url = "https://example.com/ai-article"
        
        self.mock_topics = [
            {
                'topic_id': 1,
                'topic_name': 'Artificial Intelligence',
                'content_excerpt': 'AI is revolutionizing the way we work',
                'confidence_score': 0.9
            },
            {
                'topic_id': 2,
                'topic_name': 'Future of Work',
                'content_excerpt': 'revolutionizing the way we work and live',
                'confidence_score': 0.8
            }
        ]
        
        self.mock_enhanced_topics = [
            {
                'topic_id': 1,
                'topic_name': 'Artificial Intelligence',
                'content_excerpt': 'AI is revolutionizing the way we work',
                'primary_emotion': 'encourage_dreams',
                'emotion_confidence': 0.85,
                'reasoning': 'This topic inspires future possibilities and growth'
            },
            {
                'topic_id': 2,
                'topic_name': 'Future of Work',
                'content_excerpt': 'revolutionizing the way we work and live',
                'primary_emotion': 'allay_fears',
                'emotion_confidence': 0.75,
                'reasoning': 'This topic addresses concerns about workplace changes'
            }
        ]
        
        self.mock_generated_content = [
            {
                'topic_id': 1,
                'platform': 'twitter',
                'final_post': 'AI is transforming our world! Discover how artificial intelligence is creating new opportunities for growth and innovation. Ready to embrace the future? https://example.com/ai-article',
                'content_strategy': 'single_tweet',
                'hashtags': [],
                'call_to_action': 'Ready to embrace the future?',
                'success': True,
                'error': None,
                'processing_time': 1.2
            },
            {
                'topic_id': 2,
                'platform': 'twitter',
                'final_post': 'The future of work is here, and it\'s more exciting than scary! Learn how technology is creating better opportunities for everyone. Join the revolution! https://example.com/ai-article',
                'content_strategy': 'single_tweet',
                'hashtags': [],
                'call_to_action': 'Join the revolution!',
                'success': True,
                'error': None,
                'processing_time': 1.1
            }
        ]

    @pytest.mark.asyncio
    async def test_process_content_success_full_flow(self):
        """Test successful processing through all three agents"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock topic extraction
            mock_topic_extract.return_value = {
                'success': True,
                'topics': self.mock_topics,
                'total_topics': 2,
                'processing_time': 0.5
            }
            
            # Mock emotion analysis
            mock_emotion_analyze.return_value = {
                'success': True,
                'emotion_analysis': self.mock_enhanced_topics,
                'total_analyzed': 2,
                'processing_time': 0.8
            }
            
            # Mock content generation (called twice, once per topic)
            mock_content_gen.side_effect = [
                self.mock_generated_content[0],
                self.mock_generated_content[1]
            ]
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url,
                max_topics=5,
                target_platforms=['twitter']
            )
            
            # Verify the result
            assert result['success'] is True
            assert len(result['generated_posts']) == 2
            assert result['total_topics'] == 2
            assert result['successful_generations'] == 2
            assert result['processing_time'] > 0
            
            # Verify the generated posts
            posts = result['generated_posts']
            assert posts[0] == self.mock_generated_content[0]['final_post']
            assert posts[1] == self.mock_generated_content[1]['final_post']
            
            # Verify agent calls
            mock_topic_extract.assert_called_once_with(self.sample_text, 5)
            mock_emotion_analyze.assert_called_once()
            assert mock_content_gen.call_count == 2

    @pytest.mark.asyncio
    async def test_process_content_topic_extraction_failure(self):
        """Test handling of topic extraction failure"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract:
            
            # Mock topic extraction failure
            mock_topic_extract.return_value = {
                'success': False,
                'error': 'Failed to parse topics from LLM response',
                'topics': [],
                'total_topics': 0,
                'processing_time': 0.5
            }
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify failure handling
            assert result['success'] is False
            assert 'Failed to parse topics' in result['error']
            assert result['generated_posts'] == []
            assert result['total_topics'] == 0

    @pytest.mark.asyncio
    async def test_process_content_emotion_analysis_failure(self):
        """Test handling of emotion analysis failure"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze:
            
            # Mock successful topic extraction
            mock_topic_extract.return_value = {
                'success': True,
                'topics': self.mock_topics,
                'total_topics': 2,
                'processing_time': 0.5
            }
            
            # Mock emotion analysis failure
            mock_emotion_analyze.return_value = {
                'success': False,
                'error': 'LLM API error during emotion analysis',
                'emotion_analysis': [],
                'total_analyzed': 0,
                'processing_time': 0.8
            }
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify failure handling
            assert result['success'] is False
            assert 'emotion analysis' in result['error']
            assert result['generated_posts'] == []

    @pytest.mark.asyncio
    async def test_process_content_generation_partial_failure(self):
        """Test handling when some content generation fails"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock successful topic extraction and emotion analysis
            mock_topic_extract.return_value = {
                'success': True,
                'topics': self.mock_topics,
                'total_topics': 2,
                'processing_time': 0.5
            }
            
            mock_emotion_analyze.return_value = {
                'success': True,
                'emotion_analysis': self.mock_enhanced_topics,
                'total_analyzed': 2,
                'processing_time': 0.8
            }
            
            # Mock partial content generation failure
            mock_content_gen.side_effect = [
                self.mock_generated_content[0],  # First succeeds
                {  # Second fails
                    'topic_id': 2,
                    'platform': 'twitter',
                    'final_post': '',
                    'content_strategy': '',
                    'hashtags': [],
                    'call_to_action': '',
                    'success': False,
                    'error': 'Content generation timeout',
                    'processing_time': 0.1
                }
            ]
            
            # Execute the pipeline
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify failure handling (entire flow should fail)
            assert result['success'] is False
            assert 'Content generation failed for some topics' in result['error']
            assert result['generated_posts'] == []

    @pytest.mark.asyncio
    async def test_process_content_invalid_input(self):
        """Test handling of invalid input parameters"""
        
        # Test empty text
        result = await self.service.process_content(
            text="",
            original_url=self.sample_url
        )
        assert result['success'] is False
        assert 'empty' in result['error'].lower()
        
        # Test empty URL
        result = await self.service.process_content(
            text=self.sample_text,
            original_url=""
        )
        assert result['success'] is False
        assert 'url' in result['error'].lower()
        
        # Test invalid max_topics
        result = await self.service.process_content(
            text=self.sample_text,
            original_url=self.sample_url,
            max_topics=0
        )
        assert result['success'] is False
        assert 'max_topics' in result['error'].lower()

    @pytest.mark.asyncio
    async def test_process_content_default_parameters(self):
        """Test that default parameters are applied correctly"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock successful responses
            mock_topic_extract.return_value = {'success': True, 'topics': [], 'total_topics': 0, 'processing_time': 0.1}
            mock_emotion_analyze.return_value = {'success': True, 'emotion_analysis': [], 'total_analyzed': 0, 'processing_time': 0.1}
            
            # Execute with minimal parameters
            await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url
            )
            
            # Verify default parameters were used
            mock_topic_extract.assert_called_once_with(self.sample_text, 10)  # Default max_topics

    def test_service_initialization(self):
        """Test that the service initializes all agents correctly"""
        service = ContentPipelineService()
        
        assert service.topic_extractor is not None
        assert service.emotion_analyzer is not None
        assert service.content_generator is not None
        assert hasattr(service.topic_extractor, 'extract_topics')
        assert hasattr(service.emotion_analyzer, 'analyze_emotions')
        assert hasattr(service.content_generator, 'generate_content_for_topic')

    @pytest.mark.asyncio
    async def test_process_content_multiple_platforms(self):
        """Test processing content for multiple platforms"""
        with patch.object(self.service.topic_extractor, 'extract_topics') as mock_topic_extract, \
             patch.object(self.service.emotion_analyzer, 'analyze_emotions') as mock_emotion_analyze, \
             patch.object(self.service.content_generator, 'generate_content_for_topic') as mock_content_gen:
            
            # Mock responses
            mock_topic_extract.return_value = {
                'success': True,
                'topics': [self.mock_topics[0]],  # Just one topic
                'total_topics': 1,
                'processing_time': 0.5
            }
            
            mock_emotion_analyze.return_value = {
                'success': True,
                'emotion_analysis': [self.mock_enhanced_topics[0]],
                'total_analyzed': 1,
                'processing_time': 0.8
            }
            
            # Mock content generation for multiple platforms
            mock_content_gen.side_effect = [
                {**self.mock_generated_content[0], 'platform': 'twitter'},
                {**self.mock_generated_content[0], 'platform': 'linkedin', 'final_post': 'LinkedIn version of the post'}
            ]
            
            # Execute with multiple platforms
            result = await self.service.process_content(
                text=self.sample_text,
                original_url=self.sample_url,
                target_platforms=['twitter', 'linkedin']
            )
            
            # Verify multiple posts generated
            assert result['success'] is True
            assert len(result['generated_posts']) == 2
            assert mock_content_gen.call_count == 2 