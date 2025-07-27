from abstract_classes import SubscriptionTier, MediaContent, ContentRating
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import random


class User:
    """User class managing subscription, watch history, and preferences."""
    
    def __init__(self, user_id: str, username: str, email: str, 
                 age: int, subscription_tier: SubscriptionTier = SubscriptionTier.FREE):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.age = age
        self.subscription_tier = subscription_tier
        self.subscription_start_date = datetime.now()
        self.watch_history: List[Dict[str, Any]] = []
        self.favorites: List[str] = []  # content IDs
        self.watchlist: List[str] = []  # content IDs to watch later
        self.preferences = UserPreferences()
        self.parental_controls = ParentalControls(self.age)
        self.devices: List[str] = []  # device IDs
        self.streaming_time_today = 0  # minutes
        self.total_streaming_time = 0  # minutes
        self.subscription_cost = self._calculate_subscription_cost()
        
    def _calculate_subscription_cost(self) -> float:
        """Calculate monthly subscription cost."""
        costs = {
            SubscriptionTier.FREE: 0.0,
            SubscriptionTier.PREMIUM: 12.99,
            SubscriptionTier.FAMILY: 19.99
        }
        return costs[self.subscription_tier]
    
    def upgrade_subscription(self, new_tier: SubscriptionTier) -> str:
        """Upgrade user subscription."""
        if new_tier == self.subscription_tier:
            return f"Already subscribed to {new_tier.value} tier."
        
        old_tier = self.subscription_tier
        self.subscription_tier = new_tier
        self.subscription_cost = self._calculate_subscription_cost()
        self.subscription_start_date = datetime.now()
        
        return f"Subscription upgraded from {old_tier.value} to {new_tier.value}. New cost: ${self.subscription_cost}/month"
    
    def add_to_watch_history(self, content: MediaContent, watch_duration: int, 
                           device_id: str, quality: str) -> None:
        """Add content to watch history."""
        history_entry = {
            "content_id": content.content_id,
            "title": content.title,
            "watch_date": datetime.now(),
            "watch_duration": watch_duration,  # minutes actually watched
            "total_duration": content.get_duration(),
            "completion_percentage": (watch_duration / content.get_duration()) * 100,
            "device_id": device_id,
            "quality": quality,
            "content_type": type(content).__name__
        }
        self.watch_history.append(history_entry)
        self.streaming_time_today += watch_duration
        self.total_streaming_time += watch_duration
    
    def add_to_favorites(self, content_id: str) -> str:
        """Add content to favorites."""
        if content_id not in self.favorites:
            self.favorites.append(content_id)
            return f"Added to favorites! Total favorites: {len(self.favorites)}"
        return "Already in favorites."
    
    def remove_from_favorites(self, content_id: str) -> str:
        """Remove content from favorites."""
        if content_id in self.favorites:
            self.favorites.remove(content_id)
            return f"Removed from favorites. Total favorites: {len(self.favorites)}"
        return "Not found in favorites."
    
    def add_to_watchlist(self, content_id: str) -> str:
        """Add content to watchlist."""
        if content_id not in self.watchlist:
            self.watchlist.append(content_id)
            return f"Added to watchlist! Items in watchlist: {len(self.watchlist)}"
        return "Already in watchlist."
    
    def remove_from_watchlist(self, content_id: str) -> str:
        """Remove content from watchlist."""
        if content_id in self.watchlist:
            self.watchlist.remove(content_id)
            return f"Removed from watchlist. Items remaining: {len(self.watchlist)}"
        return "Not found in watchlist."
    
    def get_watch_analytics(self) -> Dict[str, Any]:
        """Get detailed watch analytics."""
        if not self.watch_history:
            return {"message": "No watch history available"}
        
        # Calculate analytics
        total_content = len(self.watch_history)
        avg_completion = sum(entry["completion_percentage"] for entry in self.watch_history) / total_content
        
        # Content type breakdown
        content_types = {}
        for entry in self.watch_history:
            content_type = entry["content_type"]
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Device usage
        device_usage = {}
        for entry in self.watch_history:
            device = entry["device_id"]
            device_usage[device] = device_usage.get(device, 0) + entry["watch_duration"]
        
        # Recent activity (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        recent_activity = [entry for entry in self.watch_history 
                          if entry["watch_date"] >= recent_date]
        
        return {
            "total_content_watched": total_content,
            "total_streaming_hours": round(self.total_streaming_time / 60, 1),
            "streaming_hours_today": round(self.streaming_time_today / 60, 1),
            "average_completion_rate": round(avg_completion, 1),
            "content_type_breakdown": content_types,
            "device_usage_minutes": device_usage,
            "recent_activity_count": len(recent_activity),
            "subscription_tier": self.subscription_tier.value,
            "monthly_cost": self.subscription_cost
        }
    
    def get_recommendations_data(self) -> Dict[str, Any]:
        """Get data for recommendation engine."""
        # Analyze watch history for preferences
        genres = []
        directors = []
        artists = []
        
        for entry in self.watch_history:
            if entry["completion_percentage"] > 70:  # Only consider completed content
                # This would be populated with actual content data in real implementation
                pass
        
        return {
            "user_id": self.user_id,
            "age": self.age,
            "subscription_tier": self.subscription_tier.value,
            "favorite_content_ids": self.favorites,
            "watch_history": self.watch_history[-20:],  # Last 20 entries
            "preferences": self.preferences.get_all_preferences(),
            "parental_restrictions": self.parental_controls.get_restrictions()
        }
    
    def can_access_content(self, content: MediaContent) -> tuple[bool, str]:
        """Check if user can access specific content."""
        # Check subscription tier
        if content.is_premium_content() and self.subscription_tier == SubscriptionTier.FREE:
            return False, "Premium subscription required for this content"
        
        # Check parental controls
        if not self.parental_controls.is_content_allowed(content):
            return False, f"Content blocked by parental controls (Rating: {content.rating.value})"
        
        # Check device limit for family plans
        if self.subscription_tier == SubscriptionTier.FAMILY and len(self.devices) > 6:
            return False, "Device limit exceeded for family plan"
        
        return True, "Access granted"
    
    def add_device(self, device_id: str) -> str:
        """Add a device to user's account."""
        if device_id not in self.devices:
            # Check device limits based on subscription
            max_devices = {
                SubscriptionTier.FREE: 1,
                SubscriptionTier.PREMIUM: 3,
                SubscriptionTier.FAMILY: 6
            }
            
            if len(self.devices) >= max_devices[self.subscription_tier]:
                return f"Device limit reached for {self.subscription_tier.value} subscription ({max_devices[self.subscription_tier]} devices max)"
            
            self.devices.append(device_id)
            return f"Device added successfully. Devices: {len(self.devices)}/{max_devices[self.subscription_tier]}"
        return "Device already registered"
    
    def remove_device(self, device_id: str) -> str:
        """Remove a device from user's account."""
        if device_id in self.devices:
            self.devices.remove(device_id)
            return f"Device removed. Active devices: {len(self.devices)}"
        return "Device not found"


class UserPreferences:
    """User preferences for content and streaming."""
    
    def __init__(self):
        self.preferred_genres: Set[str] = set()
        self.preferred_languages: Set[str] = {"English"}
        self.preferred_quality = "auto"
        self.autoplay_next = True
        self.subtitle_enabled = False
        self.subtitle_language = "English"
        self.volume_level = 75
        self.skip_intro = False
        self.mature_content_filter = True
        self.notification_preferences = {
            "new_releases": True,
            "recommendations": True,
            "subscription_updates": True
        }
    
    def add_preferred_genre(self, genre: str) -> str:
        """Add a preferred genre."""
        self.preferred_genres.add(genre)
        return f"Added {genre} to preferred genres. Total: {len(self.preferred_genres)}"
    
    def remove_preferred_genre(self, genre: str) -> str:
        """Remove a preferred genre."""
        if genre in self.preferred_genres:
            self.preferred_genres.remove(genre)
            return f"Removed {genre} from preferred genres"
        return "Genre not found in preferences"
    
    def set_quality_preference(self, quality: str) -> str:
        """Set preferred streaming quality."""
        valid_qualities = ["auto", "480p", "720p", "1080p", "4K"]
        if quality in valid_qualities:
            self.preferred_quality = quality
            return f"Quality preference set to {quality}"
        return f"Invalid quality. Choose from: {', '.join(valid_qualities)}"
    
    def toggle_autoplay(self) -> str:
        """Toggle autoplay next episode/content."""
        self.autoplay_next = not self.autoplay_next
        return f"Autoplay {'enabled' if self.autoplay_next else 'disabled'}"
    
    def configure_subtitles(self, enabled: bool, language: str = "English") -> str:
        """Configure subtitle preferences."""
        self.subtitle_enabled = enabled
        self.subtitle_language = language
        status = "enabled" if enabled else "disabled"
        return f"Subtitles {status}" + (f" in {language}" if enabled else "")
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences."""
        return {
            "preferred_genres": list(self.preferred_genres),
            "preferred_languages": list(self.preferred_languages),
            "preferred_quality": self.preferred_quality,
            "autoplay_next": self.autoplay_next,
            "subtitle_enabled": self.subtitle_enabled,
            "subtitle_language": self.subtitle_language,
            "volume_level": self.volume_level,
            "skip_intro": self.skip_intro,
            "mature_content_filter": self.mature_content_filter,
            "notifications": self.notification_preferences
        }


class ParentalControls:
    """Parental controls for content filtering."""
    
    def __init__(self, user_age: int):
        self.user_age = user_age
        self.enabled = user_age < 18
        self.max_rating = self._get_default_max_rating()
        self.blocked_genres: Set[str] = set()
        self.time_restrictions = {
            "enabled": False,
            "start_time": "22:00",
            "end_time": "06:00"
        }
        self.daily_time_limit = 0  # minutes, 0 = no limit
        
    def _get_default_max_rating(self) -> ContentRating:
        """Get default maximum rating based on age."""
        if self.user_age < 6:
            return ContentRating.G
        elif self.user_age < 10:
            return ContentRating.PG
        elif self.user_age < 13:
            return ContentRating.PG13
        elif self.user_age < 17:
            return ContentRating.R
        else:
            return ContentRating.NC17
    
    def set_max_rating(self, rating: ContentRating) -> str:
        """Set maximum allowed content rating."""
        self.max_rating = rating
        return f"Maximum content rating set to {rating.value}"
    
    def block_genre(self, genre: str) -> str:
        """Block a specific genre."""
        self.blocked_genres.add(genre)
        return f"Blocked genre: {genre}. Total blocked genres: {len(self.blocked_genres)}"
    
    def unblock_genre(self, genre: str) -> str:
        """Unblock a specific genre."""
        if genre in self.blocked_genres:
            self.blocked_genres.remove(genre)
            return f"Unblocked genre: {genre}"
        return "Genre not found in blocked list"
    
    def set_time_restrictions(self, enabled: bool, start_time: str = "22:00", 
                            end_time: str = "06:00") -> str:
        """Set time-based viewing restrictions."""
        self.time_restrictions = {
            "enabled": enabled,
            "start_time": start_time,
            "end_time": end_time
        }
        if enabled:
            return f"Time restrictions enabled: {start_time} - {end_time}"
        return "Time restrictions disabled"
    
    def set_daily_time_limit(self, minutes: int) -> str:
        """Set daily viewing time limit."""
        self.daily_time_limit = minutes
        if minutes > 0:
            hours = minutes // 60
            mins = minutes % 60
            return f"Daily time limit set to {hours}h {mins}m"
        return "Daily time limit removed"
    
    def is_content_allowed(self, content: MediaContent) -> bool:
        """Check if content is allowed under current parental controls."""
        if not self.enabled:
            return True
        
        # Check rating
        rating_values = {
            ContentRating.G: 0, ContentRating.PG: 1, ContentRating.PG13: 2,
            ContentRating.R: 3, ContentRating.NC17: 4,
            ContentRating.TV_Y: 0, ContentRating.TV_G: 1, ContentRating.TV_PG: 2,
            ContentRating.TV_14: 3, ContentRating.TV_MA: 4
        }
        
        content_rating_value = rating_values.get(content.rating, 5)
        max_rating_value = rating_values.get(self.max_rating, 0)
        
        if content_rating_value > max_rating_value:
            return False
        
        # Check blocked genres
        if hasattr(content, 'genre') and content.genre in self.blocked_genres:
            return False
        
        return True
    
    def is_viewing_time_allowed(self) -> tuple[bool, str]:
        """Check if current time allows viewing."""
        if not self.time_restrictions["enabled"]:
            return True, "No time restrictions"
        
        current_time = datetime.now().strftime("%H:%M")
        start_time = self.time_restrictions["start_time"]
        end_time = self.time_restrictions["end_time"]
        
        # Handle overnight restrictions (e.g., 22:00 - 06:00)
        if start_time > end_time:
            if current_time >= start_time or current_time <= end_time:
                return False, f"Viewing restricted between {start_time} and {end_time}"
        else:
            if start_time <= current_time <= end_time:
                return False, f"Viewing restricted between {start_time} and {end_time}"
        
        return True, "Viewing time allowed"
    
    def get_restrictions(self) -> Dict[str, Any]:
        """Get all current parental control settings."""
        return {
            "enabled": self.enabled,
            "user_age": self.user_age,
            "max_rating": self.max_rating.value if self.max_rating else None,
            "blocked_genres": list(self.blocked_genres),
            "time_restrictions": self.time_restrictions,
            "daily_time_limit_minutes": self.daily_time_limit
        } 