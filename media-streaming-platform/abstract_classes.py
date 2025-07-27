from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
import statistics


class ContentRating(Enum):
    G = "G"
    PG = "PG"
    PG13 = "PG-13"
    R = "R"
    NC17 = "NC-17"
    TV_Y = "TV-Y"
    TV_G = "TV-G"
    TV_PG = "TV-PG"
    TV_14 = "TV-14"
    TV_MA = "TV-MA"


class SubscriptionTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    FAMILY = "family"


class MediaContent(ABC):
    """Abstract base class for all media content types."""
    
    def __init__(self, title: str, content_id: str, description: str, 
                 release_date: str, rating: ContentRating, is_premium: bool = False):
        self.title = title
        self.content_id = content_id
        self.description = description
        self.release_date = release_date
        self.rating = rating
        self.is_premium = is_premium
        self.user_ratings: List[float] = []
        self.view_count = 0
        self.tags: List[str] = []
    
    @abstractmethod
    def play(self) -> str:
        """Start playing the content."""
        pass
    
    @abstractmethod
    def get_duration(self) -> int:
        """Get content duration in minutes."""
        pass
    
    @abstractmethod
    def get_file_size(self) -> float:
        """Get file size in GB."""
        pass
    
    @abstractmethod
    def calculate_streaming_cost(self, device_type: str, quality: str) -> float:
        """Calculate streaming cost based on device and quality."""
        pass
    
    def add_rating(self, rating: float) -> None:
        """Add a user rating (1-5 stars)."""
        if 1 <= rating <= 5:
            self.user_ratings.append(rating)
        else:
            raise ValueError("Rating must be between 1 and 5")
    
    def get_average_rating(self) -> Optional[float]:
        """Get average user rating."""
        if not self.user_ratings:
            return None
        return round(statistics.mean(self.user_ratings), 2)
    
    def is_premium_content(self) -> bool:
        """Check if content requires premium subscription."""
        return self.is_premium
    
    def increment_view_count(self) -> None:
        """Increment view count."""
        self.view_count += 1
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the content."""
        if tag not in self.tags:
            self.tags.append(tag)


class StreamingDevice(ABC):
    """Abstract base class for different streaming devices."""
    
    def __init__(self, device_id: str, device_name: str, max_resolution: str):
        self.device_id = device_id
        self.device_name = device_name
        self.max_resolution = max_resolution
        self.is_connected = False
        self.current_content: Optional[MediaContent] = None
        self.supported_formats: List[str] = []
        self.current_quality = "auto"
    
    @abstractmethod
    def connect(self) -> str:
        """Connect the device to the streaming platform."""
        pass
    
    @abstractmethod
    def stream_content(self, content: MediaContent) -> str:
        """Stream content on this device."""
        pass
    
    @abstractmethod
    def adjust_quality(self, quality: str) -> str:
        """Adjust streaming quality."""
        pass
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "max_resolution": self.max_resolution,
            "is_connected": self.is_connected,
            "supported_formats": self.supported_formats,
            "current_quality": self.current_quality
        }
    
    def check_compatibility(self, content: MediaContent) -> bool:
        """Check if device is compatible with content."""
        # Basic compatibility check - can be overridden in subclasses
        return True
    
    def disconnect(self) -> str:
        """Disconnect the device."""
        self.is_connected = False
        self.current_content = None
        return f"{self.device_name} disconnected successfully" 