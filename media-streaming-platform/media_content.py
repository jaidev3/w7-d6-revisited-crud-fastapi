from abstract_classes import MediaContent, ContentRating
from typing import List, Optional, Dict, Any
import random


class Movie(MediaContent):
    """Concrete class for movie content."""
    
    def __init__(self, title: str, content_id: str, description: str, 
                 release_date: str, rating: ContentRating, duration_minutes: int,
                 resolution: str, genre: str, director: str, is_premium: bool = False):
        super().__init__(title, content_id, description, release_date, rating, is_premium)
        self.duration_minutes = duration_minutes
        self.resolution = resolution
        self.genre = genre
        self.director = director
        self.cast: List[str] = []
        self.subtitles_available: List[str] = ["English"]
        
    def play(self) -> str:
        """Start playing the movie."""
        self.increment_view_count()
        return f"🎬 Now playing: {self.title} ({self.duration_minutes} min) - Directed by {self.director}"
    
    def get_duration(self) -> int:
        """Get movie duration in minutes."""
        return self.duration_minutes
    
    def get_file_size(self) -> float:
        """Calculate file size based on duration and resolution."""
        base_size_per_minute = {
            "720p": 0.02,  # GB per minute
            "1080p": 0.05,
            "4K": 0.15,
            "8K": 0.4
        }
        return round(self.duration_minutes * base_size_per_minute.get(self.resolution, 0.05), 2)
    
    def calculate_streaming_cost(self, device_type: str, quality: str) -> float:
        """Calculate streaming cost based on device and quality."""
        base_cost = 0.05  # Base cost per minute
        quality_multiplier = {"720p": 1.0, "1080p": 1.5, "4K": 2.5, "8K": 4.0}
        device_multiplier = {"mobile": 0.8, "laptop": 1.0, "smart_tv": 1.2, "smart_speaker": 0.5}
        
        return round(base_cost * self.duration_minutes * 
                    quality_multiplier.get(quality, 1.0) * 
                    device_multiplier.get(device_type, 1.0), 2)
    
    def add_cast_member(self, actor: str) -> None:
        """Add an actor to the cast."""
        if actor not in self.cast:
            self.cast.append(actor)
    
    def add_subtitle_language(self, language: str) -> None:
        """Add subtitle language support."""
        if language not in self.subtitles_available:
            self.subtitles_available.append(language)


class TVShow(MediaContent):
    """Concrete class for TV show content."""
    
    def __init__(self, title: str, content_id: str, description: str, 
                 release_date: str, rating: ContentRating, total_episodes: int,
                 total_seasons: int, episode_duration: int, genre: str,
                 is_premium: bool = False):
        super().__init__(title, content_id, description, release_date, rating, is_premium)
        self.total_episodes = total_episodes
        self.total_seasons = total_seasons
        self.episode_duration = episode_duration
        self.genre = genre
        self.current_season = 1
        self.current_episode = 1
        self.episodes_watched = 0
        self.is_series_complete = False
        
    def play(self) -> str:
        """Start playing the current episode."""
        self.increment_view_count()
        episode_info = f"S{self.current_season:02d}E{self.current_episode:02d}"
        return f"📺 Now playing: {self.title} - {episode_info} ({self.episode_duration} min)"
    
    def get_duration(self) -> int:
        """Get total series duration in minutes."""
        return self.total_episodes * self.episode_duration
    
    def get_file_size(self) -> float:
        """Calculate total file size for all episodes."""
        size_per_episode = self.episode_duration * 0.03  # GB per episode
        return round(self.total_episodes * size_per_episode, 2)
    
    def calculate_streaming_cost(self, device_type: str, quality: str) -> float:
        """Calculate streaming cost for current episode."""
        base_cost = 0.03  # Base cost per minute for TV
        quality_multiplier = {"720p": 1.0, "1080p": 1.5, "4K": 2.0}
        device_multiplier = {"mobile": 0.8, "laptop": 1.0, "smart_tv": 1.2, "smart_speaker": 0.5}
        
        return round(base_cost * self.episode_duration * 
                    quality_multiplier.get(quality, 1.0) * 
                    device_multiplier.get(device_type, 1.0), 2)
    
    def next_episode(self) -> str:
        """Move to the next episode."""
        if self.current_episode < self.episodes_per_season():
            self.current_episode += 1
        elif self.current_season < self.total_seasons:
            self.current_season += 1
            self.current_episode = 1
        else:
            return "Series completed! No more episodes available."
        
        self.episodes_watched += 1
        return f"Moving to S{self.current_season:02d}E{self.current_episode:02d}"
    
    def episodes_per_season(self) -> int:
        """Calculate average episodes per season."""
        return self.total_episodes // self.total_seasons
    
    def get_progress_percentage(self) -> float:
        """Get viewing progress as percentage."""
        return round((self.episodes_watched / self.total_episodes) * 100, 1)


class Podcast(MediaContent):
    """Concrete class for podcast content."""
    
    def __init__(self, title: str, content_id: str, description: str, 
                 release_date: str, episode_number: int, duration_minutes: int,
                 host: str, transcript_available: bool = False, is_premium: bool = False):
        super().__init__(title, content_id, description, release_date, ContentRating.G, is_premium)
        self.episode_number = episode_number
        self.duration_minutes = duration_minutes
        self.host = host
        self.transcript_available = transcript_available
        self.guests: List[str] = []
        self.topics: List[str] = []
        
    def play(self) -> str:
        """Start playing the podcast."""
        self.increment_view_count()
        transcript_info = " (Transcript available)" if self.transcript_available else ""
        return f"🎙️ Now playing: {self.title} - Episode {self.episode_number} ({self.duration_minutes} min){transcript_info}"
    
    def get_duration(self) -> int:
        """Get podcast duration in minutes."""
        return self.duration_minutes
    
    def get_file_size(self) -> float:
        """Calculate file size for audio content."""
        # Audio files are much smaller than video
        size_per_minute = 0.001  # GB per minute for audio
        transcript_size = 0.01 if self.transcript_available else 0
        return round(self.duration_minutes * size_per_minute + transcript_size, 3)
    
    def calculate_streaming_cost(self, device_type: str, quality: str) -> float:
        """Calculate streaming cost for podcast."""
        base_cost = 0.01  # Lower cost for audio content
        device_multiplier = {"mobile": 0.9, "laptop": 1.0, "smart_tv": 0.7, "smart_speaker": 1.2}
        
        return round(base_cost * self.duration_minutes * 
                    device_multiplier.get(device_type, 1.0), 2)
    
    def add_guest(self, guest: str) -> None:
        """Add a guest to the podcast."""
        if guest not in self.guests:
            self.guests.append(guest)
    
    def add_topic(self, topic: str) -> None:
        """Add a topic discussed in the podcast."""
        if topic not in self.topics:
            self.topics.append(topic)
    
    def get_transcript(self) -> str:
        """Get transcript if available."""
        if self.transcript_available:
            return f"Transcript for {self.title} - Episode {self.episode_number} is available."
        return "Transcript not available for this episode."


class Music(MediaContent):
    """Concrete class for music content."""
    
    def __init__(self, title: str, content_id: str, description: str, 
                 release_date: str, artist: str, album: str, duration_seconds: int,
                 genre: str, lyrics_available: bool = False, is_premium: bool = False):
        super().__init__(title, content_id, description, release_date, ContentRating.G, is_premium)
        self.artist = artist
        self.album = album
        self.duration_seconds = duration_seconds
        self.genre = genre
        self.lyrics_available = lyrics_available
        self.featured_artists: List[str] = []
        self.play_count = 0
        
    def play(self) -> str:
        """Start playing the music."""
        self.increment_view_count()
        self.play_count += 1
        duration_str = f"{self.duration_seconds // 60}:{self.duration_seconds % 60:02d}"
        lyrics_info = " 🎵" if self.lyrics_available else ""
        return f"🎵 Now playing: {self.title} by {self.artist} ({duration_str}){lyrics_info}"
    
    def get_duration(self) -> int:
        """Get music duration in minutes."""
        return self.duration_seconds // 60
    
    def get_file_size(self) -> float:
        """Calculate file size for music."""
        # High quality audio file size
        size_per_second = 0.0002  # GB per second for high-quality audio
        return round(self.duration_seconds * size_per_second, 3)
    
    def calculate_streaming_cost(self, device_type: str, quality: str) -> float:
        """Calculate streaming cost for music."""
        base_cost = 0.005  # Very low cost for music streaming
        quality_multiplier = {"low": 0.5, "standard": 1.0, "high": 1.5, "lossless": 2.0}
        device_multiplier = {"mobile": 1.0, "laptop": 1.0, "smart_tv": 0.8, "smart_speaker": 1.3}
        
        duration_minutes = self.duration_seconds / 60
        return round(base_cost * duration_minutes * 
                    quality_multiplier.get(quality, 1.0) * 
                    device_multiplier.get(device_type, 1.0), 3)
    
    def add_featured_artist(self, artist: str) -> None:
        """Add a featured artist."""
        if artist not in self.featured_artists:
            self.featured_artists.append(artist)
    
    def get_lyrics(self) -> str:
        """Get lyrics if available."""
        if self.lyrics_available:
            return f"♪ Lyrics for '{self.title}' by {self.artist} are available."
        return "Lyrics not available for this song."
    
    def create_playlist_info(self) -> Dict[str, Any]:
        """Get info for playlist creation."""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration_seconds,
            "genre": self.genre,
            "play_count": self.play_count
        } 