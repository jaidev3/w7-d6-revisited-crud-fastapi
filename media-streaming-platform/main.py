#!/usr/bin/env python3
"""
Media Streaming Platform with Abstraction & Polymorphism
========================================================

This demonstration showcases a comprehensive media streaming platform that handles 
different types of media content (Movies, TV Shows, Podcasts, Music) using abstract 
base classes and polymorphism. The system manages user subscriptions, content 
recommendations, and playback functionality across various devices.

Key Features Demonstrated:
- Abstract base classes (MediaContent, StreamingDevice)
- Polymorphism in content playback and device streaming
- User subscription management with tiered access
- Advanced recommendation engine
- Parental controls and content filtering
- Device-specific quality optimization
- Watch time analytics and reporting
"""

from abstract_classes import ContentRating, SubscriptionTier
from media_content import Movie, TVShow, Podcast, Music
from streaming_devices import SmartTV, Laptop, Mobile, SmartSpeaker
from user import User
from streaming_platform import StreamingPlatform
import time
import random


def create_sample_content():
    """Create sample content for the platform."""
    content = []
    
    # Movies
    movies = [
        Movie("The Matrix", "mov_001", "A hacker discovers reality is a simulation", 
              "1999-03-31", ContentRating.R, 136, "4K", "Sci-Fi", "The Wachowskis", True),
        Movie("Finding Nemo", "mov_002", "A clownfish searches for his son", 
              "2003-05-30", ContentRating.G, 100, "1080p", "Animation", "Andrew Stanton"),
        Movie("Inception", "mov_003", "Dreams within dreams heist thriller", 
              "2010-07-16", ContentRating.PG13, 148, "4K", "Thriller", "Christopher Nolan", True),
        Movie("The Lion King", "mov_004", "Young lion prince's journey to reclaim his kingdom", 
              "1994-06-24", ContentRating.G, 88, "1080p", "Animation", "Roger Allers")
    ]
    
    # TV Shows
    tv_shows = [
        TVShow("Stranger Things", "tv_001", "Kids encounter supernatural forces", 
               "2016-07-15", ContentRating.TV_14, 42, 4, 50, "Sci-Fi", True),
        TVShow("The Office", "tv_002", "Mockumentary of office workers", 
               "2005-03-24", ContentRating.TV_PG, 201, 9, 22, "Comedy"),
        TVShow("Breaking Bad", "tv_003", "High school teacher turns to cooking meth", 
               "2008-01-20", ContentRating.TV_MA, 62, 5, 47, "Drama", True),
        TVShow("Friends", "tv_004", "Six friends living in New York", 
               "1994-09-22", ContentRating.TV_PG, 236, 10, 22, "Comedy")
    ]
    
    # Podcasts
    podcasts = [
        Podcast("Tech Talk Daily", "pod_001", "Latest technology news and trends", 
                "2024-01-15", 145, 35, "Sarah Tech", True),
        Podcast("History Mysteries", "pod_002", "Unsolved mysteries from history", 
                "2024-01-10", 78, 45, "Dr. Historical", False),
        Podcast("Startup Stories", "pod_003", "Entrepreneurs share their journey", 
                "2024-01-12", 92, 55, "Business Guru", True, True),
        Podcast("Science Simplified", "pod_004", "Complex science made easy", 
                "2024-01-08", 156, 40, "Prof. Science")
    ]
    
    # Music
    music = [
        Music("Bohemian Rhapsody", "mus_001", "Epic rock opera masterpiece", 
              "1975-10-31", "Queen", "A Night at the Opera", 355, "Rock", True, True),
        Music("Billie Jean", "mus_002", "Iconic pop hit", 
              "1983-01-02", "Michael Jackson", "Thriller", 294, "Pop", True),
        Music("Imagine", "mus_003", "Inspirational peace anthem", 
              "1971-09-09", "John Lennon", "Imagine", 183, "Rock", True),
        Music("Shape of You", "mus_004", "Modern pop hit", 
              "2017-01-06", "Ed Sheeran", "÷", 233, "Pop", False)
    ]
    
    content.extend(movies)
    content.extend(tv_shows)
    content.extend(podcasts)
    content.extend(music)
    
    # Add some ratings to content
    for item in content:
        for _ in range(random.randint(10, 50)):
            item.add_rating(random.uniform(3.0, 5.0))
        item.view_count = random.randint(100, 10000)
    
    return content


def create_sample_devices():
    """Create sample streaming devices."""
    devices = [
        SmartTV("tv_001", "Living Room Samsung TV", 65.0, True),
        SmartTV("tv_002", "Bedroom LG TV", 43.0, False),
        Laptop("laptop_001", "MacBook Pro", 13.3, True, 85),
        Laptop("laptop_002", "Dell XPS", 15.6, True, 45),
        Mobile("mobile_001", "iPhone 15 Pro", 6.1, "iOS", 15.0),
        Mobile("mobile_002", "Samsung Galaxy S24", 6.2, "Android", 20.0),
        SmartSpeaker("speaker_001", "Amazon Echo", "Premium", "Alexa"),
        SmartSpeaker("speaker_002", "Google Nest", "High-End", "Google")
    ]
    return devices


def create_sample_users():
    """Create sample users with different profiles."""
    users = [
        User("user_001", "alice_johnson", "alice@email.com", 28, SubscriptionTier.PREMIUM),
        User("user_002", "bob_smith", "bob@email.com", 35, SubscriptionTier.FAMILY),
        User("user_003", "charlie_brown", "charlie@email.com", 16, SubscriptionTier.FREE),
        User("user_004", "diana_prince", "diana@email.com", 42, SubscriptionTier.PREMIUM),
        User("user_005", "young_user", "parent@email.com", 8, SubscriptionTier.FREE)
    ]
    
    # Configure user preferences
    users[0].preferences.add_preferred_genre("Sci-Fi")
    users[0].preferences.add_preferred_genre("Thriller")
    users[0].preferences.set_quality_preference("4K")
    
    users[1].preferences.add_preferred_genre("Comedy")
    users[1].preferences.add_preferred_genre("Animation")
    users[1].preferences.configure_subtitles(True, "English")
    
    users[2].preferences.add_preferred_genre("Comedy")
    users[2].parental_controls.set_time_restrictions(True, "22:00", "06:00")
    
    users[3].preferences.add_preferred_genre("Drama")
    users[3].preferences.add_preferred_genre("History")
    
    # Young user with strict parental controls
    users[4].parental_controls.set_max_rating(ContentRating.G)
    users[4].parental_controls.block_genre("Horror")
    users[4].parental_controls.set_daily_time_limit(120)  # 2 hours
    
    return users


def demonstrate_polymorphism(platform):
    """Demonstrate polymorphism with different content types and devices."""
    print("\n" + "="*60)
    print("🎭 POLYMORPHISM DEMONSTRATION")
    print("="*60)
    
    # Get some content and devices
    movie = platform.get_content_by_id("mov_001")
    tv_show = platform.get_content_by_id("tv_001")
    podcast = platform.get_content_by_id("pod_001")
    music = platform.get_content_by_id("mus_001")
    
    smart_tv = platform.get_device_by_id("tv_001")
    laptop = platform.get_device_by_id("laptop_001")
    mobile = platform.get_device_by_id("mobile_001")
    speaker = platform.get_device_by_id("speaker_001")
    
    print("\n📱 Device Connection (Polymorphic behavior):")
    devices = [smart_tv, laptop, mobile, speaker]
    for device in devices:
        print(f"  • {device.connect()}")
    
    print("\n🎬 Content Playback (Polymorphic behavior):")
    content_items = [movie, tv_show, podcast, music]
    for content in content_items:
        print(f"  • {content.play()}")
    
    print("\n📺 Device-Specific Streaming (Polymorphic behavior):")
    # Different devices handle the same content differently
    print(f"Smart TV: {smart_tv.stream_content(movie)}")
    print(f"Laptop: {laptop.stream_content(tv_show)}")
    print(f"Mobile: {mobile.stream_content(podcast)}")
    print(f"Speaker: {speaker.stream_content(music)}")
    
    print("\n⚙️ Quality Adjustment (Polymorphic behavior):")
    print(f"Smart TV: {smart_tv.adjust_quality('4K')}")
    print(f"Laptop: {laptop.adjust_quality('1080p')}")
    print(f"Mobile: {mobile.adjust_quality('720p')}")
    print(f"Speaker: {speaker.adjust_quality('lossless')}")


def demonstrate_streaming_workflow(platform):
    """Demonstrate complete streaming workflow."""
    print("\n" + "="*60)
    print("🎥 COMPLETE STREAMING WORKFLOW")
    print("="*60)
    
    user_id = "user_001"
    user = platform.authenticate_user(user_id)
    
    print(f"\n👤 User: {user.username} ({user.subscription_tier.value} subscription)")
    
    # Add devices to user account
    print(f"📱 Adding devices: {user.add_device('tv_001')}")
    print(f"📱 Adding devices: {user.add_device('laptop_001')}")
    
    # Start streaming
    print(f"\n▶️ Starting stream: {platform.start_streaming(user_id, 'mov_001', 'tv_001')}")
    
    # Simulate some viewing time
    print("\n⏱️ Simulating 5 minutes of viewing...")
    time.sleep(2)  # Simulate time passing
    
    # Check active stream
    dashboard = platform.get_user_dashboard(user_id)
    if dashboard["active_stream"]:
        stream_info = dashboard["active_stream"]
        print(f"📊 Active Stream: {stream_info['content_title']} on {stream_info['device_name']}")
        print(f"   Quality: {stream_info['quality']}, Cost: ${stream_info['streaming_cost']}")
    
    # Adjust quality during streaming
    print(f"\n🔧 Quality adjustment: {platform.quality_optimization(user_id, '1080p')}")
    
    # Stop streaming
    print(f"\n⏹️ Stopping stream: {platform.stop_streaming(user_id)}")
    
    # Add to favorites
    print(f"❤️ Adding to favorites: {user.add_to_favorites('mov_001')}")
    
    # Add to watchlist
    print(f"📝 Adding to watchlist: {user.add_to_watchlist('tv_001')}")


def demonstrate_recommendation_engine(platform):
    """Demonstrate the recommendation engine."""
    print("\n" + "="*60)
    print("🤖 RECOMMENDATION ENGINE")
    print("="*60)
    
    user_id = "user_001"
    user = platform.authenticate_user(user_id)
    
    # Simulate some viewing history
    user.add_to_watch_history(platform.get_content_by_id("mov_001"), 120, "tv_001", "4K")
    user.add_to_watch_history(platform.get_content_by_id("mov_003"), 148, "laptop_001", "1080p")
    user.add_to_favorites("mov_001")
    user.add_to_favorites("mov_003")
    
    print(f"\n👤 Getting recommendations for {user.username}:")
    print(f"   Preferred genres: {list(user.preferences.preferred_genres)}")
    print(f"   Subscription tier: {user.subscription_tier.value}")
    
    recommendations = platform.get_recommendations(user_id)
    
    print(f"\n🎯 Top 5 Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        rating_str = f"⭐ {rec['rating']}" if rec['rating'] else "⭐ No rating"
        premium_str = "💎 Premium" if rec['is_premium'] else "🆓 Free"
        print(f"  {i}. {rec['title']} ({rec['type']})")
        print(f"     {rec['description'][:50]}...")
        print(f"     {rating_str} | {premium_str} | {rec['duration']} min")
        if 'genre' in rec:
            print(f"     Genre: {rec['genre']}")
        print()


def demonstrate_parental_controls(platform):
    """Demonstrate parental controls functionality."""
    print("\n" + "="*60)
    print("👨‍👩‍👧‍👦 PARENTAL CONTROLS")
    print("="*60)
    
    young_user = platform.authenticate_user("user_005")
    adult_content = platform.get_content_by_id("mov_001")  # R-rated movie
    family_content = platform.get_content_by_id("mov_002")  # G-rated movie
    
    print(f"\n👶 Young User: {young_user.username} (Age: {young_user.age})")
    print(f"   Parental controls enabled: {young_user.parental_controls.enabled}")
    print(f"   Max rating allowed: {young_user.parental_controls.max_rating.value}")
    
    # Test content access
    can_access_adult, message_adult = young_user.can_access_content(adult_content)
    can_access_family, message_family = young_user.can_access_content(family_content)
    
    print(f"\n🔒 Content Access Test:")
    print(f"   '{adult_content.title}' ({adult_content.rating.value}): {'✅ Allowed' if can_access_adult else '❌ Blocked'}")
    if not can_access_adult:
        print(f"       Reason: {message_adult}")
    
    print(f"   '{family_content.title}' ({family_content.rating.value}): {'✅ Allowed' if can_access_family else '❌ Blocked'}")
    if not can_access_family:
        print(f"       Reason: {message_family}")
    
    # Test time restrictions
    time_allowed, time_message = young_user.parental_controls.is_viewing_time_allowed()
    print(f"\n⏰ Time Restrictions: {'✅ Viewing allowed' if time_allowed else '❌ Viewing restricted'}")
    print(f"   {time_message}")
    
    # Show daily time limit
    daily_limit = young_user.parental_controls.daily_time_limit
    if daily_limit > 0:
        hours = daily_limit // 60
        minutes = daily_limit % 60
        print(f"📱 Daily Time Limit: {hours}h {minutes}m")


def demonstrate_analytics(platform):
    """Demonstrate analytics and reporting features."""
    print("\n" + "="*60)
    print("📊 ANALYTICS & REPORTING")
    print("="*60)
    
    # Platform-wide analytics
    platform_stats = platform.get_platform_analytics()
    print(f"\n🏢 Platform Analytics for '{platform_stats['platform_name']}':")
    print(f"   👥 Total Users: {platform_stats['total_users']}")
    print(f"   💎 Premium Users: {platform_stats['premium_users']} ({platform_stats['premium_percentage']}%)")
    print(f"   🎬 Total Content: {platform_stats['total_content']}")
    print(f"   📺 Total Streams: {platform_stats['total_streams']}")
    print(f"   🔴 Active Streams: {platform_stats['active_streams']}")
    print(f"   📱 Registered Devices: {platform_stats['registered_devices']}")
    
    print(f"\n📈 Content Type Breakdown:")
    for content_type, count in platform_stats['content_type_breakdown'].items():
        print(f"   • {content_type}: {count}")
    
    print(f"\n📱 Device Type Breakdown:")
    for device_type, count in platform_stats['device_type_breakdown'].items():
        print(f"   • {device_type}: {count}")
    
    # User-specific analytics
    user = platform.authenticate_user("user_001")
    user_stats = user.get_watch_analytics()
    
    print(f"\n👤 User Analytics for '{user.username}':")
    if "message" not in user_stats:
        print(f"   🎬 Content Watched: {user_stats['total_content_watched']}")
        print(f"   ⏱️ Total Hours: {user_stats['total_streaming_hours']}")
        print(f"   📅 Hours Today: {user_stats['streaming_hours_today']}")
        print(f"   ✅ Avg Completion: {user_stats['average_completion_rate']}%")
        print(f"   💰 Monthly Cost: ${user_stats['monthly_cost']}")
        
        if user_stats['content_type_breakdown']:
            print(f"\n   Content Type Preferences:")
            for content_type, count in user_stats['content_type_breakdown'].items():
                print(f"     • {content_type}: {count}")


def demonstrate_search_functionality(platform):
    """Demonstrate content search and filtering."""
    print("\n" + "="*60)
    print("🔍 SEARCH & FILTERING")
    print("="*60)
    
    # General search
    print("\n🔍 Searching for 'science':")
    search_results = platform.search_content("science")
    for result in search_results[:3]:
        print(f"   • {result['title']} ({result['type']})")
        print(f"     {result['description'][:50]}...")
        rating_str = f"⭐ {result['rating']}" if result['rating'] else "⭐ No rating"
        print(f"     {rating_str} | Views: {result['view_count']}")
    
    # Filtered search
    print("\n🎬 Searching for movies with 'the':")
    movie_results = platform.search_content("the", content_type="Movie")
    for result in movie_results:
        print(f"   • {result['title']} - Views: {result['view_count']}")
    
    # Genre-based search
    print("\n🎭 Searching for comedy content:")
    comedy_results = platform.search_content("", genre="Comedy")
    for result in comedy_results:
        print(f"   • {result['title']} ({result['type']})")


def main():
    """Main demonstration function."""
    print("🎬" + "="*58 + "🎬")
    print("     MEDIA STREAMING PLATFORM DEMONSTRATION")
    print("        with Abstraction & Polymorphism")
    print("🎬" + "="*58 + "🎬")
    
    # Initialize the platform
    platform = StreamingPlatform("StreamFlix Pro")
    
    # Setup sample data
    print("\n🔧 Setting up platform...")
    
    # Add content
    content_items = create_sample_content()
    for content in content_items:
        platform.add_content(content)
    
    # Register devices
    devices = create_sample_devices()
    for device in devices:
        platform.register_device(device)
    
    # Register users
    users = create_sample_users()
    for user in users:
        platform.register_user(user)
    
    print(f"✅ Platform setup complete!")
    print(f"   📚 Added {len(content_items)} content items")
    print(f"   📱 Registered {len(devices)} devices")
    print(f"   👥 Registered {len(users)} users")
    
    # Run demonstrations
    demonstrate_polymorphism(platform)
    demonstrate_streaming_workflow(platform)
    demonstrate_recommendation_engine(platform)
    demonstrate_parental_controls(platform)
    demonstrate_search_functionality(platform)
    demonstrate_analytics(platform)
    
    print("\n" + "="*60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("✅ Abstract base classes (MediaContent, StreamingDevice)")
    print("✅ Polymorphism in content playback and device streaming")
    print("✅ User subscription management with tiered access")
    print("✅ Advanced recommendation engine")
    print("✅ Parental controls and content filtering")
    print("✅ Device-specific quality optimization")
    print("✅ Watch time analytics and reporting")
    print("✅ Search and filtering functionality")
    print("\n🏗️ Architecture Benefits:")
    print("• Easy to add new content types (extend MediaContent)")
    print("• Easy to add new devices (extend StreamingDevice)")
    print("• Consistent interface across all content and devices")
    print("• Scalable and maintainable codebase")
    print("• Rich feature set with real-world applicability")


if __name__ == "__main__":
    main() 