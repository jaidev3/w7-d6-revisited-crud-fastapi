from abstract_classes import MediaContent, StreamingDevice, SubscriptionTier
from media_content import Movie, TVShow, Podcast, Music
from streaming_devices import SmartTV, Laptop, Mobile, SmartSpeaker
from user import User
from typing import List, Dict, Any, Optional, Type
import random
from datetime import datetime, timedelta


class RecommendationEngine:
    """Advanced recommendation engine based on user preferences and behavior."""
    
    def __init__(self):
        self.content_similarity: Dict[str, List[str]] = {}
        self.user_similarity: Dict[str, List[str]] = {}
        
    def calculate_content_recommendations(self, user: User, 
                                       available_content: List[MediaContent]) -> List[MediaContent]:
        """Calculate personalized content recommendations."""
        recommendations = []
        user_data = user.get_recommendations_data()
        
        # Content-based filtering
        content_based = self._content_based_filtering(user, available_content)
        
        # Collaborative filtering (simplified)
        collaborative = self._collaborative_filtering(user, available_content)
        
        # Trending content
        trending = self._get_trending_content(available_content)
        
        # Combine recommendations with weights
        all_recommendations = {}
        
        # Weight content-based recommendations higher
        for content in content_based[:10]:
            all_recommendations[content.content_id] = all_recommendations.get(content.content_id, 0) + 3
        
        # Add collaborative recommendations
        for content in collaborative[:8]:
            all_recommendations[content.content_id] = all_recommendations.get(content.content_id, 0) + 2
        
        # Add trending content
        for content in trending[:5]:
            all_recommendations[content.content_id] = all_recommendations.get(content.content_id, 0) + 1
        
        # Sort by weighted score and return top recommendations
        sorted_recommendations = sorted(all_recommendations.items(), key=lambda x: x[1], reverse=True)
        
        # Convert back to content objects
        content_dict = {c.content_id: c for c in available_content}
        for content_id, score in sorted_recommendations[:15]:
            if content_id in content_dict:
                recommendations.append(content_dict[content_id])
        
        return recommendations
    
    def _content_based_filtering(self, user: User, content: List[MediaContent]) -> List[MediaContent]:
        """Recommend content based on user's preferences and history."""
        scored_content = []
        user_prefs = user.preferences.get_all_preferences()
        
        for item in content:
            score = 0
            
            # Check if user can access content
            can_access, _ = user.can_access_content(item)
            if not can_access:
                continue
            
            # Genre matching
            if hasattr(item, 'genre') and item.genre in user_prefs['preferred_genres']:
                score += 5
            
            # Check if similar to favorited content
            if item.content_id not in user.favorites:  # Don't recommend already favorited
                # Check average rating
                avg_rating = item.get_average_rating()
                if avg_rating and avg_rating > 4.0:
                    score += 3
                elif avg_rating and avg_rating > 3.5:
                    score += 2
                
                # Boost premium content for premium users
                if item.is_premium_content() and user.subscription_tier != SubscriptionTier.FREE:
                    score += 2
                
                # Content type diversity based on watch history
                content_type = type(item).__name__
                recent_history = user.watch_history[-10:] if len(user.watch_history) > 10 else user.watch_history
                recent_types = [entry['content_type'] for entry in recent_history]
                
                if content_type not in recent_types:
                    score += 1  # Encourage diversity
                
                scored_content.append((item, score))
        
        # Sort by score and return
        scored_content.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored_content]
    
    def _collaborative_filtering(self, user: User, content: List[MediaContent]) -> List[MediaContent]:
        """Simple collaborative filtering based on similar users."""
        # In a real system, this would analyze similar users' preferences
        # For demo purposes, we'll use a simplified approach
        collaborative_recommendations = []
        
        # Find content with high ratings that user hasn't seen
        for item in content:
            if item.content_id not in [entry['content_id'] for entry in user.watch_history]:
                avg_rating = item.get_average_rating()
                if avg_rating and avg_rating > 4.0:
                    collaborative_recommendations.append(item)
        
        return collaborative_recommendations[:10]
    
    def _get_trending_content(self, content: List[MediaContent]) -> List[MediaContent]:
        """Get trending content based on view count and recent ratings."""
        trending = []
        
        for item in content:
            # Simple trending algorithm based on view count and ratings
            trend_score = item.view_count
            avg_rating = item.get_average_rating()
            if avg_rating:
                trend_score *= avg_rating
            
            trending.append((item, trend_score))
        
        # Sort by trend score and return top items
        trending.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in trending[:15]]


class StreamingPlatform:
    """Main streaming platform orchestrator using polymorphism."""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.content_library: List[MediaContent] = []
        self.registered_devices: List[StreamingDevice] = []
        self.users: Dict[str, User] = {}
        self.active_streams: Dict[str, Dict[str, Any]] = {}  # user_id -> stream info
        self.recommendation_engine = RecommendationEngine()
        self.platform_analytics = {
            "total_streams": 0,
            "total_users": 0,
            "premium_users": 0,
            "total_content": 0
        }
        
    def add_content(self, content: MediaContent) -> str:
        """Add content to the platform library."""
        self.content_library.append(content)
        self.platform_analytics["total_content"] += 1
        return f"Added '{content.title}' to {self.platform_name} library"
    
    def register_device(self, device: StreamingDevice) -> str:
        """Register a streaming device."""
        self.registered_devices.append(device)
        return f"Device '{device.device_name}' registered successfully"
    
    def register_user(self, user: User) -> str:
        """Register a new user."""
        self.users[user.user_id] = user
        self.platform_analytics["total_users"] += 1
        if user.subscription_tier != SubscriptionTier.FREE:
            self.platform_analytics["premium_users"] += 1
        return f"User '{user.username}' registered successfully"
    
    def authenticate_user(self, user_id: str) -> Optional[User]:
        """Authenticate and return user."""
        return self.users.get(user_id)
    
    def get_device_by_id(self, device_id: str) -> Optional[StreamingDevice]:
        """Get device by ID."""
        for device in self.registered_devices:
            if device.device_id == device_id:
                return device
        return None
    
    def get_content_by_id(self, content_id: str) -> Optional[MediaContent]:
        """Get content by ID."""
        for content in self.content_library:
            if content.content_id == content_id:
                return content
        return None
    
    def start_streaming(self, user_id: str, content_id: str, device_id: str) -> str:
        """Start streaming content using polymorphism."""
        # Get user, content, and device
        user = self.authenticate_user(user_id)
        if not user:
            return "User not found or not authenticated"
        
        content = self.get_content_by_id(content_id)
        if not content:
            return "Content not found"
        
        device = self.get_device_by_id(device_id)
        if not device:
            return "Device not found"
        
        # Check user access permissions
        can_access, access_message = user.can_access_content(content)
        if not can_access:
            return f"Access denied: {access_message}"
        
        # Check parental controls time restrictions
        time_allowed, time_message = user.parental_controls.is_viewing_time_allowed()
        if not time_allowed:
            return f"Viewing restricted: {time_message}"
        
        # Check device compatibility
        if not device.check_compatibility(content):
            return f"Content not compatible with {device.device_name}"
        
        # Connect device if not connected
        if not device.is_connected:
            device.connect()
        
        # Start streaming (polymorphic behavior)
        stream_result = device.stream_content(content)
        
        # Calculate streaming cost
        device_type = type(device).__name__.lower().replace('smart', 'smart_')
        streaming_cost = content.calculate_streaming_cost(device_type, device.current_quality)
        
        # Record active stream
        self.active_streams[user_id] = {
            "content": content,
            "device": device,
            "start_time": datetime.now(),
            "streaming_cost": streaming_cost,
            "quality": device.current_quality
        }
        
        # Update analytics
        self.platform_analytics["total_streams"] += 1
        
        return f"✅ Streaming started!\n{stream_result}\nStreaming cost: ${streaming_cost}"
    
    def stop_streaming(self, user_id: str) -> str:
        """Stop streaming and update user history."""
        if user_id not in self.active_streams:
            return "No active stream found for user"
        
        stream_info = self.active_streams[user_id]
        content = stream_info["content"]
        device = stream_info["device"]
        start_time = stream_info["start_time"]
        
        # Calculate watch duration
        end_time = datetime.now()
        watch_duration = int((end_time - start_time).total_seconds() / 60)  # minutes
        
        # Add to user's watch history
        user = self.users[user_id]
        user.add_to_watch_history(content, watch_duration, device.device_id, device.current_quality)
        
        # Clear active stream
        del self.active_streams[user_id]
        
        return f"⏹️ Streaming stopped. Watched for {watch_duration} minutes."
    
    def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user."""
        user = self.authenticate_user(user_id)
        if not user:
            return []
        
        recommendations = self.recommendation_engine.calculate_content_recommendations(
            user, self.content_library
        )
        
        # Format recommendations
        formatted_recommendations = []
        for content in recommendations:
            rec_info = {
                "content_id": content.content_id,
                "title": content.title,
                "type": type(content).__name__,
                "description": content.description,
                "rating": content.get_average_rating(),
                "is_premium": content.is_premium_content(),
                "duration": content.get_duration()
            }
            
            # Add type-specific info
            if hasattr(content, 'genre'):
                rec_info["genre"] = content.genre
            if hasattr(content, 'artist'):
                rec_info["artist"] = content.artist
            if hasattr(content, 'director'):
                rec_info["director"] = content.director
            
            formatted_recommendations.append(rec_info)
        
        return formatted_recommendations
    
    def search_content(self, query: str, content_type: str = None, 
                      genre: str = None) -> List[Dict[str, Any]]:
        """Search content with filters."""
        results = []
        query_lower = query.lower()
        
        for content in self.content_library:
            # Text search in title and description
            if (query_lower in content.title.lower() or 
                query_lower in content.description.lower()):
                
                # Apply filters
                if content_type and type(content).__name__ != content_type:
                    continue
                
                if genre and hasattr(content, 'genre') and content.genre != genre:
                    continue
                
                result_info = {
                    "content_id": content.content_id,
                    "title": content.title,
                    "type": type(content).__name__,
                    "description": content.description,
                    "rating": content.get_average_rating(),
                    "view_count": content.view_count,
                    "is_premium": content.is_premium_content()
                }
                
                results.append(result_info)
        
        # Sort by relevance (view count and rating)
        results.sort(key=lambda x: (x["view_count"], x["rating"] or 0), reverse=True)
        return results
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Get platform-wide analytics."""
        # Calculate additional analytics
        premium_percentage = 0
        if self.platform_analytics["total_users"] > 0:
            premium_percentage = (self.platform_analytics["premium_users"] / 
                                self.platform_analytics["total_users"]) * 100
        
        # Content type breakdown
        content_types = {}
        for content in self.content_library:
            content_type = type(content).__name__
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Active streams
        active_stream_count = len(self.active_streams)
        
        # Device type breakdown
        device_types = {}
        for device in self.registered_devices:
            device_type = type(device).__name__
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return {
            "platform_name": self.platform_name,
            "total_users": self.platform_analytics["total_users"],
            "premium_users": self.platform_analytics["premium_users"],
            "premium_percentage": round(premium_percentage, 1),
            "total_content": self.platform_analytics["total_content"],
            "total_streams": self.platform_analytics["total_streams"],
            "active_streams": active_stream_count,
            "content_type_breakdown": content_types,
            "device_type_breakdown": device_types,
            "registered_devices": len(self.registered_devices)
        }
    
    def quality_optimization(self, user_id: str, target_quality: str) -> str:
        """Optimize streaming quality for user's current session."""
        if user_id not in self.active_streams:
            return "No active stream to optimize"
        
        stream_info = self.active_streams[user_id]
        device = stream_info["device"]
        content = stream_info["content"]
        
        # Use polymorphic method to adjust quality
        result = device.adjust_quality(target_quality)
        
        # Update streaming cost
        device_type = type(device).__name__.lower().replace('smart', 'smart_')
        new_cost = content.calculate_streaming_cost(device_type, device.current_quality)
        stream_info["streaming_cost"] = new_cost
        stream_info["quality"] = device.current_quality
        
        return f"{result}\nUpdated streaming cost: ${new_cost}"
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard."""
        user = self.authenticate_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get recommendations
        recommendations = self.get_recommendations(user_id)[:5]
        
        # Get analytics
        analytics = user.get_watch_analytics()
        
        # Active stream info
        active_stream = None
        if user_id in self.active_streams:
            stream_info = self.active_streams[user_id]
            active_stream = {
                "content_title": stream_info["content"].title,
                "device_name": stream_info["device"].device_name,
                "quality": stream_info["quality"],
                "streaming_cost": stream_info["streaming_cost"],
                "duration": str(datetime.now() - stream_info["start_time"]).split('.')[0]
            }
        
        return {
            "user_info": {
                "username": user.username,
                "subscription_tier": user.subscription_tier.value,
                "monthly_cost": user.subscription_cost,
                "devices_registered": len(user.devices)
            },
            "analytics": analytics,
            "recommendations": recommendations,
            "active_stream": active_stream,
            "favorites_count": len(user.favorites),
            "watchlist_count": len(user.watchlist)
        } 