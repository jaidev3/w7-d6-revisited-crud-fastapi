# 🎬 Media Streaming Platform with Abstraction & Polymorphism

A comprehensive media streaming platform that demonstrates object-oriented programming principles through abstract base classes and polymorphism. The system handles different types of media content (Movies, TV Shows, Podcasts, Music) and manages streaming across various devices with advanced features like user subscriptions, content recommendations, and parental controls.

## 🏗️ Architecture Overview

The platform is built using key OOP principles:

- **Abstract Base Classes**: Define common interfaces for content and devices
- **Polymorphism**: Enables different content types and devices to behave appropriately while sharing common interfaces
- **Encapsulation**: Each class manages its own state and behavior
- **Inheritance**: Concrete classes extend abstract base classes with specific implementations

## 📋 Core Components

### Abstract Base Classes

#### `MediaContent(ABC)`
Base class for all media types with abstract methods:
- `play()`: Start playing the content
- `get_duration()`: Get content duration in minutes
- `get_file_size()`: Get file size in GB
- `calculate_streaming_cost()`: Calculate streaming cost based on device and quality

Concrete methods:
- `add_rating()`: Add user rating (1-5 stars)
- `get_average_rating()`: Get average user rating
- `is_premium_content()`: Check if content requires premium subscription

#### `StreamingDevice(ABC)`
Base class for streaming devices with abstract methods:
- `connect()`: Connect device to streaming platform
- `stream_content()`: Stream content on this device
- `adjust_quality()`: Adjust streaming quality

Concrete methods:
- `get_device_info()`: Get device information
- `check_compatibility()`: Check content compatibility

### Concrete Classes

#### Media Content Types
- **Movie**: Duration, resolution, genre, director, cast
- **TVShow**: Episodes, seasons, current episode tracking
- **Podcast**: Episode number, transcript availability, guests
- **Music**: Artist, album, lyrics, playlist integration

#### Streaming Devices
- **SmartTV**: Large screen, 4K support, surround sound, parental controls
- **Laptop**: Medium screen, headphone support, power management
- **Mobile**: Small screen, battery optimization, data usage tracking
- **SmartSpeaker**: Audio-only, voice control, high-quality audio

### Supporting Classes

#### `User`
- Subscription management (Free, Premium, Family tiers)
- Watch history and analytics
- Favorites and watchlist
- User preferences
- Device management

#### `UserPreferences`
- Preferred genres and languages
- Quality preferences
- Subtitle settings
- Autoplay and notification preferences

#### `ParentalControls`
- Age-appropriate content filtering
- Time-based viewing restrictions
- Daily time limits
- Genre blocking

#### `StreamingPlatform`
- Content library management
- Device registration
- User authentication
- Recommendation engine
- Analytics and reporting

## 🎯 Key Features

### 1. **Polymorphic Content Playback**
Different content types implement the `play()` method differently:
```python
# Movies show duration and director
movie.play()  # "🎬 Now playing: The Matrix (136 min) - Directed by The Wachowskis"

# Music shows artist and duration
music.play()  # "🎵 Now playing: Bohemian Rhapsody by Queen (5:55) 🎵"

# TV Shows show season and episode
tv_show.play()  # "📺 Now playing: Stranger Things - S01E01 (50 min)"
```

### 2. **Device-Specific Streaming**
Different devices handle content streaming based on their capabilities:
```python
# Smart TV optimizes for large screen viewing
smart_tv.stream_content(movie)  # Optimizes for 4K with surround sound

# Mobile optimizes for data usage and battery
mobile.stream_content(movie)  # Reduces quality, warns about data usage

# Smart Speaker extracts audio for audio-only playback
speaker.stream_content(movie)  # Plays audio track with voice controls
```

### 3. **Advanced Recommendation Engine**
- **Content-based filtering**: Based on user preferences and history
- **Collaborative filtering**: Based on similar users' preferences
- **Trending content**: Popular content with high ratings
- **Personalized scoring**: Combines multiple factors for recommendations

### 4. **Subscription Tier Management**
- **Free**: Limited content, 1 device, ads
- **Premium**: Full content library, 3 devices, HD quality
- **Family**: Premium features + 6 devices, multiple profiles

### 5. **Comprehensive Analytics**
- User watch time and completion rates
- Content popularity metrics
- Device usage patterns
- Platform-wide statistics

### 6. **Parental Controls**
- Age-appropriate content filtering
- Time-based viewing restrictions
- Daily time limits
- Genre and content blocking

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- No external dependencies required (uses standard library only)

### Installation
1. Clone or download the project
2. Navigate to the media-streaming-platform directory
3. Run the demonstration:

```bash
python main.py
```

### Running the Demo
The `main.py` file provides a comprehensive demonstration of all features:

```bash
python main.py
```

This will showcase:
- Polymorphism in action
- Complete streaming workflow
- Recommendation engine
- Parental controls
- Search and filtering
- Analytics and reporting

## 📁 Project Structure

```
media-streaming-platform/
├── abstract_classes.py      # Abstract base classes and enums
├── media_content.py         # Concrete media content classes
├── streaming_devices.py     # Concrete streaming device classes
├── user.py                  # User, preferences, and parental controls
├── streaming_platform.py    # Main platform orchestrator
├── main.py                  # Comprehensive demonstration
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## 🎭 Polymorphism Examples

### Content Polymorphism
```python
# All content types share the same interface but behave differently
content_list = [movie, tv_show, podcast, music]

for content in content_list:
    print(content.play())           # Polymorphic method call
    print(f"Duration: {content.get_duration()} minutes")
    print(f"Size: {content.get_file_size()} GB")
    print(f"Cost: ${content.calculate_streaming_cost('laptop', '1080p')}")
```

### Device Polymorphism
```python
# All devices can stream content but with device-specific optimizations
devices = [smart_tv, laptop, mobile, speaker]

for device in devices:
    print(device.connect())                    # Polymorphic connection
    print(device.stream_content(content))      # Device-specific streaming
    print(device.adjust_quality("1080p"))      # Device-specific quality adjustment
```

## 🔧 Extensibility

The platform is designed for easy extension:

### Adding New Content Types
```python
class Audiobook(MediaContent):
    def __init__(self, title, content_id, narrator, chapters, ...):
        super().__init__(...)
        self.narrator = narrator
        self.chapters = chapters
    
    def play(self):
        return f"🎧 Now playing audiobook: {self.title} narrated by {self.narrator}"
    
    # Implement other abstract methods...
```

### Adding New Device Types
```python
class VRHeadset(StreamingDevice):
    def __init__(self, device_id, device_name, fov, ...):
        super().__init__(device_id, device_name, "4K")
        self.field_of_view = fov
    
    def connect(self):
        return f"🥽 {self.device_name} VR headset connected for immersive viewing"
    
    def stream_content(self, content):
        # VR-specific streaming logic
        return f"🥽 Streaming {content.title} in immersive VR mode"
    
    # Implement other abstract methods...
```

## 📊 Sample Output

When you run the demonstration, you'll see output like:

```
🎬============================================================🎬
     MEDIA STREAMING PLATFORM DEMONSTRATION
        with Abstraction & Polymorphism
🎬============================================================🎬

🔧 Setting up platform...
✅ Platform setup complete!
   📚 Added 16 content items
   📱 Registered 8 devices
   👥 Registered 5 users

============================================================
🎭 POLYMORPHISM DEMONSTRATION
============================================================

📱 Device Connection (Polymorphic behavior):
  • 🖥️ Living Room Samsung TV (65.0" Smart TV) connected successfully. 4K and surround sound ready!
  • 💻 MacBook Pro (13.3" laptop) connected (Battery: 85%)
  • 📱 iPhone 15 Pro (6.1" iOS) connected via Mobile Data
  • 🔊 Amazon Echo (Premium Alexa speaker) connected and ready for voice commands

🎬 Content Playback (Polymorphic behavior):
  • 🎬 Now playing: The Matrix (136 min) - Directed by The Wachowskis
  • 📺 Now playing: Stranger Things - S01E01 (50 min)
  • 🎙️ Now playing: Tech Talk Daily - Episode 145 (35 min) (Transcript available)
  • 🎵 Now playing: Bohemian Rhapsody by Queen (5:55) 🎵
```

## 🎓 Educational Value

This project demonstrates key computer science concepts:

1. **Abstract Base Classes**: Defining contracts that subclasses must implement
2. **Polymorphism**: Same interface, different implementations
3. **Inheritance**: Code reuse and specialization
4. **Encapsulation**: Data hiding and method organization
5. **Composition**: Building complex objects from simpler ones
6. **Design Patterns**: Strategy pattern in device streaming, Observer pattern in analytics

## 🤝 Contributing

Feel free to extend this project by:
- Adding new content types (Audiobooks, Live Streams, etc.)
- Creating new device types (VR Headsets, Gaming Consoles, etc.)
- Implementing new recommendation algorithms
- Adding more sophisticated analytics
- Creating a web interface
- Adding database persistence

## 📝 License

This project is created for educational purposes and is available under the MIT License.

---

**Note**: This is a demonstration project showcasing object-oriented programming principles. In a production environment, you would need additional considerations like database integration, security, API design, scalability, and real streaming protocols. 