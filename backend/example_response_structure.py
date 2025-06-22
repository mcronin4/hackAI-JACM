#!/usr/bin/env python3
"""
Example of the NEW platform-separated response structure for frontend
"""

# Example successful response with both Twitter and LinkedIn posts
successful_response = {
    "success": True,
    
    # 🆕 NEW: Posts organized by platform for easy frontend handling
    "platform_posts": {
        "twitter": [
            {
                "post_content": "Building strong relationships isn't just networking events. It's genuine curiosity & helping others. When you shift from 'what can I get' to 'how can I help,' magic happens. What's one small action that built your strongest connection? https://example.com/networking",
                "topic_id": 1,
                "topic_name": "Building authentic professional relationships through genuine curiosity",
                "primary_emotion": "encourage_dreams",
                "content_strategy": "single_tweet",
                "processing_time": 3.2
            },
            {
                "post_content": "People say networking is about who you know. Wrong. It's about who knows YOU care about their success. Small gestures—remembering details, sharing opportunities—create lasting bonds. How do you show you genuinely care? https://example.com/networking",
                "topic_id": 2, 
                "topic_name": "Creating lasting professional connections through genuine care",
                "primary_emotion": "encourage_dreams",
                "content_strategy": "single_tweet",
                "processing_time": 2.8
            }
        ],
        "linkedin": [
            {
                "post_content": "Building truly strong professional relationships transcends the transactional nature of networking events. It's about cultivating genuine curiosity about others' journeys and their unique challenges.\n\nThe shift from 'what can I gain' to 'how can I genuinely contribute' is profoundly noticed. People instinctively recognize this authentic approach.\n\nSmall, consistent actions—like recalling past conversation details, proactively sharing relevant opportunities, or offering support during difficult periods—forge lasting connections. These aren't just fleeting interactions; they are investments in a supportive ecosystem.\n\nHow are you nurturing your professional relationships today? https://example.com/networking",
                "topic_id": 1,
                "topic_name": "Building authentic professional relationships through genuine curiosity", 
                "primary_emotion": "encourage_dreams",
                "content_strategy": "professional_post",
                "processing_time": 4.1
            },
            {
                "post_content": "The most successful professionals understand a fundamental truth: networking isn't about collecting contacts—it's about building genuine connections where mutual success is the foundation.\n\nWhen we demonstrate authentic interest in others' achievements and challenges, we create an environment where meaningful collaboration naturally emerges. This approach transforms superficial professional interactions into lasting partnerships.\n\nConsider the small gestures that have the greatest impact: remembering important details from previous conversations, thoughtfully sharing relevant opportunities, or simply offering support during challenging times.\n\nWhat intentional action will you take today to deepen a professional relationship? https://example.com/networking",
                "topic_id": 2,
                "topic_name": "Creating lasting professional connections through genuine care",
                "primary_emotion": "encourage_dreams", 
                "content_strategy": "professional_post",
                "processing_time": 4.7
            }
        ]
    },
    
    # 🔄 LEGACY: Flat list for backwards compatibility (if needed)
    "generated_posts": [
        "Building strong relationships isn't just networking events...",  # Twitter post 1
        "People say networking is about who you know...",               # Twitter post 2  
        "Building truly strong professional relationships...",          # LinkedIn post 1
        "The most successful professionals understand..."               # LinkedIn post 2
    ],
    
    "total_topics": 2,
    "successful_generations": 4,  # 2 topics × 2 platforms = 4 posts
    "processing_time": 15.3,
    "pipeline_details": {
        "topic_extraction_time": 2.1,
        "emotion_analysis_time": 1.8,
        "platforms_processed": ["twitter", "linkedin"]
    }
}

# Example error response
error_response = {
    "success": False,
    "error": "Topic extraction failed: ...",
    "platform_posts": {},  # Empty structure
    "generated_posts": [],  # Empty for backwards compatibility
    "total_topics": 0,
    "successful_generations": 0,
    "processing_time": 2.1
}

def frontend_usage_example():
    """How the frontend would use the new structure"""
    response = successful_response  # This is what your API returns
    
    if response["success"]:
        platform_posts = response["platform_posts"]
        
        # Easy access to Twitter posts
        twitter_posts = platform_posts.get("twitter", [])
        print(f"Twitter: {len(twitter_posts)} posts")
        for post in twitter_posts:
            print(f"  - {post['post_content'][:50]}...")
            print(f"    Strategy: {post['content_strategy']}")
            print(f"    Length: {len(post['post_content'])} chars")
        
        # Easy access to LinkedIn posts  
        linkedin_posts = platform_posts.get("linkedin", [])
        print(f"\nLinkedIn: {len(linkedin_posts)} posts")
        for post in linkedin_posts:
            print(f"  - {post['post_content'][:50]}...")
            print(f"    Strategy: {post['content_strategy']}")
            print(f"    Length: {len(post['post_content'])} chars")
            
        # Frontend can easily display them separately or together
        total_posts = len(twitter_posts) + len(linkedin_posts)
        print(f"\nTotal: {total_posts} posts across {len(platform_posts)} platforms")

if __name__ == "__main__":
    print("🎯 Frontend Usage Example:")
    print("=" * 50)
    frontend_usage_example() 