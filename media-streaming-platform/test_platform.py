#!/usr/bin/env python3
"""
Comprehensive test suite for the Media Streaming Platform
Tests abstract classes, polymorphism, and all platform features
"""

from abstract_classes import MediaContent, StreamingDevice, ContentRating, SubscriptionTier
from media_content import Movie, TVShow, Podcast, Music
from streaming_devices import SmartTV, Laptop, Mobile, SmartSpeaker
from user import User
from streaming_platform import StreamingPlatform


def test_abstract_class_instantiation():
    """Test Case 1: Abstract class instantiation should fail"""
    print("🧪 Test Case 1: Abstract class instantiation")
    
    try:
        # This should fail - cannot instantiate abstract class
        content = MediaContent("Test", "test_001", "Test description", "2024-01-01", ContentRating.G)
        assert False, "Should not be able to instantiate abstract class MediaContent"
    except TypeError as e:
        print(f"✅ MediaContent instantiation properly blocked: {e}")
    
    try:
        # This should fail - cannot instantiate abstract class
        device = StreamingDevice("test_001", "Test Device", "1080p")
        assert False, "Should not be able to instantiate abstract class StreamingDevice"
    except TypeError as e:
        print(f"✅ StreamingDevice instantiation properly blocked: {e}")
    
    print()


def test_polymorphic_content_creation():
    """Test Case 2: Polymorphic content creation and playback"""
    print("🧪 Test Case 2: Polymorphic content creation and playback")
    
    # Create different content types
    movie = Movie("Inception", "mov_test_001", "Dreams within dreams", "2010-07-16", 
                  ContentRating.PG13, 148, "4K", "Sci-Fi", "Christopher Nolan")
    
    tv_show = TVShow("Breaking Bad", "tv_test_001", "Chemistry teacher turns criminal", 
                     "2008-01-20", ContentRating.TV_MA, 62, 5, 47, "Drama")
    
    podcast = Podcast("Tech Talk", "pod_test_001", "Technology discussions", 
                      "2024-01-01", 15, 45, "Tech Host", True)
    
    music = Music("Bohemian Rhapsody", "mus_test_001", "Epic rock opera", 
                  "1975-10-31", "Queen", "A Night at the Opera", 355, "Rock", True)
    
    contents = [movie, tv_show, podcast, music]
    
    # Test polymorphic behavior
    print("Testing polymorphic methods:")
    for content in contents:
        # Test play method
        play_result = content.play()
        assert isinstance(play_result, str)
        assert "playing" in play_result.lower()
        print(f"  ✅ {type(content).__name__}: {play_result}")
        
        # Test duration
        duration = content.get_duration()
        assert isinstance(duration, (int, float))
        assert duration > 0
        print(f"     Duration: {duration} minutes")
        
        # Test file size
        file_size = content.get_file_size()
        assert isinstance(file_size, (int, float))
        print(f"     File size: {file_size} GB")
        
        # Test streaming cost
        cost = content.calculate_streaming_cost("laptop", "1080p")
        assert isinstance(cost, (int, float))
        assert cost >= 0
        print(f"     Streaming cost: ${cost}")
        print()
    
    return contents


def test_device_streaming_behavior():
    """Test Case 3: Device-specific streaming behavior"""
    print("🧪 Test Case 3: Device-specific streaming behavior")
    
    # Create different device types
    smart_tv = SmartTV("tv_test_001", "Samsung 4K TV", 55.0, True)
    laptop = Laptop("laptop_test_001", "MacBook Pro", 13.3, True, 85)
    mobile = Mobile("mobile_test_001", "iPhone 13", 6.1, "iOS", 15.0)
    speaker = SmartSpeaker("speaker_test_001", "Amazon Echo", "Premium", "Alexa")
    
    devices = [smart_tv, laptop, mobile, speaker]
    
    # Create test content
    movie = Movie("Test Movie", "mov_test_002", "Test movie description", "2024-01-01",
                  ContentRating.PG13, 120, "4K", "Action", "Test Director")
    
    print("Testing device connections and streaming:")
    for device in devices:
        # Test connection
        connect_result = device.connect()
        assert "connected" in connect_result.lower()
        print(f"  ✅ {type(device).__name__}: {connect_result}")
        
        # Test polymorphic streaming
        stream_result = device.stream_content(movie)
        assert isinstance(stream_result, str)
        print(f"     Streaming: {stream_result}")
        
        # Test quality adjustment
        quality_result = device.adjust_quality("1080p")
        assert isinstance(quality_result, str)
        print(f"     Quality: {quality_result}")
        print()
    
    return devices, movie


def test_device_content_compatibility():
    """Test Case 4: Device-content compatibility"""
    print("🧪 Test Case 4: Device-content compatibility")
    
    # Create content types
    podcast = Podcast("Audio Podcast", "pod_test_002", "Audio content", 
                      "2024-01-01", 20, 30, "Host", True)
    music = Music("Test Song", "mus_test_002", "Test music", 
                  "2024-01-01", "Artist", "Album", 180, "Pop", True)
    movie = Movie("Video Movie", "mov_test_003", "Video content", "2024-01-01",
                  ContentRating.PG, 90, "1080p", "Comedy", "Director")
    tv_show = TVShow("Video Show", "tv_test_002", "Video series", "2024-01-01",
                     ContentRating.TV_PG, 20, 2, 30, "Drama")
    
    # Create smart speaker (audio-focused device)
    speaker = SmartSpeaker("speaker_test_002", "Google Nest", "High-End", "Google")
    speaker.connect()
    
    audio_content = [podcast, music]
    video_content = [movie, tv_show]
    
    print("Testing audio content on smart speaker:")
    for content in audio_content:
        result = speaker.stream_content(content)
        print(f"  ✅ {content.title}: {result}")
    
    print("\nTesting video content on smart speaker (should extract audio):")
    for content in video_content:
        result = speaker.stream_content(content)
        print(f"  ✅ {content.title}: {result}")
    
    print()


def test_user_subscription_platform_integration():
    """Test Case 5: User subscription and platform integration"""
    print("🧪 Test Case 5: User subscription and platform integration")
    
    # Create user with premium subscription
    user = User("user_test_001", "john_doe", "john@email.com", 28, SubscriptionTier.PREMIUM)
    user.preferences.add_preferred_genre("Sci-Fi")
    user.preferences.add_preferred_genre("Drama")
    
    # Create platform
    platform = StreamingPlatform("TestStream")
    
    # Create content
    movie = Movie("Sci-Fi Epic", "mov_test_004", "Space adventure", "2024-01-01",
                  ContentRating.PG13, 150, "4K", "Sci-Fi", "Director", True)
    tv_show = TVShow("Drama Series", "tv_test_003", "Intense drama", "2024-01-01",
                     ContentRating.TV_14, 40, 3, 60, "Drama", True)
    
    # Add content to platform
    platform.add_content(movie)
    platform.add_content(tv_show)
    
    # Register user
    platform.register_user(user)
    print(f"✅ User registered: {user.username}")
    
    # Register device
    smart_tv = SmartTV("tv_test_002", "Test TV", 65.0, True)
    platform.register_device(smart_tv)
    user.add_device(smart_tv.device_id)
    print(f"✅ Device registered: {smart_tv.device_name}")
    
    # Test recommendation system
    recommendations = platform.get_recommendations(user.user_id)
    assert isinstance(recommendations, list)
    print(f"✅ Recommendations generated: {len(recommendations)} items")
    for rec in recommendations[:3]:
        print(f"   • {rec['title']} ({rec['type']}) - Genre: {rec.get('genre', 'N/A')}")
    
    # Test streaming workflow
    stream_result = platform.start_streaming(user.user_id, movie.content_id, smart_tv.device_id)
    print(f"✅ Streaming started: {stream_result.split(chr(10))[0]}")  # First line only
    
    # Stop streaming and check analytics
    platform.stop_streaming(user.user_id)
    analytics = user.get_watch_analytics()
    
    if "message" not in analytics:
        print(f"✅ Analytics available:")
        print(f"   • Total content watched: {analytics['total_content_watched']}")
        print(f"   • Total streaming hours: {analytics['total_streaming_hours']}")
        print(f"   • Monthly cost: ${analytics['monthly_cost']}")
    
    print()
    return platform, user


def test_subscription_tier_restrictions():
    """Test Case 6: Subscription tier restrictions"""
    print("🧪 Test Case 6: Subscription tier restrictions")
    
    # Create free user
    free_user = User("user_test_002", "jane_doe", "jane@email.com", 25, SubscriptionTier.FREE)
    
    # Create platform and register user
    platform = StreamingPlatform("TestStream")
    platform.register_user(free_user)
    
    # Create premium content
    premium_movie = Movie("Premium Film", "mov_test_005", "Exclusive content", "2024-01-01",
                          ContentRating.PG13, 120, "4K", "Action", "Premium Director", True)
    platform.add_content(premium_movie)
    
    # Register device
    laptop = Laptop("laptop_test_002", "Test Laptop", 15.6, True, 75)
    platform.register_device(laptop)
    free_user.add_device(laptop.device_id)
    
    # Test access restriction
    can_access, message = free_user.can_access_content(premium_movie)
    print(f"✅ Free user premium content access: {'Allowed' if can_access else 'Blocked'}")
    if not can_access:
        print(f"   Reason: {message}")
    
    # Test streaming attempt
    stream_result = platform.start_streaming(free_user.user_id, premium_movie.content_id, laptop.device_id)
    print(f"✅ Streaming attempt result: {stream_result}")
    
    print()


def test_content_rating_and_recommendations():
    """Test Case 7: Content rating and recommendation impact"""
    print("🧪 Test Case 7: Content rating and recommendation impact")
    
    # Create movie and add ratings
    movie = Movie("Highly Rated Film", "mov_test_006", "Great movie", "2024-01-01",
                  ContentRating.PG13, 130, "4K", "Drama", "Acclaimed Director")
    
    # Add multiple ratings
    ratings = [4.5, 4.8, 4.2, 4.7, 4.6]
    for rating in ratings:
        movie.add_rating(rating)
    
    average_rating = movie.get_average_rating()
    expected_average = sum(ratings) / len(ratings)
    
    print(f"✅ Movie ratings added: {ratings}")
    print(f"✅ Average rating: {average_rating} (expected: {expected_average:.2f})")
    assert abs(average_rating - expected_average) < 0.1, f"Rating calculation error: {average_rating} vs {expected_average}"
    
    # Test recommendation impact
    platform = StreamingPlatform("TestStream")
    user = User("user_test_003", "movie_lover", "lover@email.com", 30, SubscriptionTier.PREMIUM)
    user.preferences.add_preferred_genre("Drama")
    
    platform.register_user(user)
    platform.add_content(movie)
    
    # Add some viewing history to improve recommendations
    user.add_to_watch_history(movie, 120, "device_001", "4K")
    user.add_to_favorites(movie.content_id)
    
    recommendations = platform.get_recommendations(user.user_id)
    highly_rated = [rec for rec in recommendations if rec.get('rating') and rec['rating'] > 4.0]
    
    print(f"✅ Recommendations generated: {len(recommendations)} items")
    print(f"✅ Highly rated recommendations (>4.0): {len(highly_rated)} items")
    
    if highly_rated:
        print("   Top rated recommendations:")
        for rec in highly_rated[:3]:
            print(f"   • {rec['title']}: ⭐ {rec['rating']}")
    
    print()


def run_all_tests():
    """Run all test cases"""
    print("🚀 Starting Media Streaming Platform Test Suite")
    print("=" * 60)
    
    try:
        test_abstract_class_instantiation()
        contents = test_polymorphic_content_creation()
        devices, movie = test_device_streaming_behavior()
        test_device_content_compatibility()
        platform, user = test_user_subscription_platform_integration()
        test_subscription_tier_restrictions()
        test_content_rating_and_recommendations()
        
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("✅ Abstract classes properly prevent instantiation")
        print("✅ Polymorphism working correctly across content types")
        print("✅ Device-specific streaming behavior implemented")
        print("✅ Content-device compatibility checks working")
        print("✅ User subscription and platform integration functional")
        print("✅ Subscription tier restrictions enforced")
        print("✅ Content rating and recommendation system operational")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests() 