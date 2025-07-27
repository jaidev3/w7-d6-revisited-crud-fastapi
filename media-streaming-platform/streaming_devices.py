from abstract_classes import StreamingDevice, MediaContent
from typing import List, Dict, Any, Optional
import random


class SmartTV(StreamingDevice):
    """Smart TV streaming device with large screen and 4K support."""
    
    def __init__(self, device_id: str, device_name: str, screen_size: float, 
                 has_surround_sound: bool = True):
        super().__init__(device_id, device_name, "4K")
        self.screen_size = screen_size  # in inches
        self.has_surround_sound = has_surround_sound
        self.supported_formats = ["MP4", "AVI", "MKV", "HEVC", "HDR10"]
        self.current_quality = "4K"
        self.volume_level = 50
        self.brightness = 75
        
    def connect(self) -> str:
        """Connect the Smart TV to the streaming platform."""
        self.is_connected = True
        return f"🖥️ {self.device_name} ({self.screen_size}\" Smart TV) connected successfully. 4K and surround sound ready!"
    
    def stream_content(self, content: MediaContent) -> str:
        """Stream content on Smart TV with optimized settings."""
        if not self.is_connected:
            return "Device not connected. Please connect first."
        
        self.current_content = content
        # Optimize for TV viewing
        if hasattr(content, 'resolution'):
            optimal_quality = min(content.resolution, self.max_resolution)
        else:
            optimal_quality = "1080p"  # Default for audio content
            
        surround_info = " with surround sound" if self.has_surround_sound else ""
        return f"📺 Streaming on {self.device_name}: {content.play()}\nOptimized for {optimal_quality} viewing{surround_info}"
    
    def adjust_quality(self, quality: str) -> str:
        """Adjust streaming quality for Smart TV."""
        available_qualities = ["720p", "1080p", "4K", "8K"]
        if quality in available_qualities:
            self.current_quality = quality
            return f"Quality adjusted to {quality} on {self.device_name}"
        return f"Quality {quality} not supported. Available: {', '.join(available_qualities)}"
    
    def check_compatibility(self, content: MediaContent) -> bool:
        """Check Smart TV compatibility with content."""
        # Smart TVs can handle most content types
        if hasattr(content, 'resolution'):
            return content.resolution in ["720p", "1080p", "4K", "8K"]
        return True  # Audio content is always compatible
    
    def adjust_display_settings(self, brightness: int, volume: int) -> str:
        """Adjust TV display and audio settings."""
        self.brightness = max(0, min(100, brightness))
        self.volume_level = max(0, min(100, volume))
        return f"Display settings updated: Brightness {self.brightness}%, Volume {self.volume_level}%"
    
    def enable_parental_controls(self, max_rating: str) -> str:
        """Enable parental controls."""
        return f"Parental controls enabled. Maximum rating: {max_rating}"


class Laptop(StreamingDevice):
    """Laptop streaming device with medium screen and headphone support."""
    
    def __init__(self, device_id: str, device_name: str, screen_size: float,
                 has_headphone_jack: bool = True, battery_level: int = 100):
        super().__init__(device_id, device_name, "1080p")
        self.screen_size = screen_size  # in inches
        self.has_headphone_jack = has_headphone_jack
        self.battery_level = battery_level
        self.supported_formats = ["MP4", "AVI", "MKV", "WebM"]
        self.current_quality = "1080p"
        self.is_power_saving = False
        
    def connect(self) -> str:
        """Connect the laptop to the streaming platform."""
        self.is_connected = True
        battery_info = f" (Battery: {self.battery_level}%)" if self.battery_level < 100 else ""
        return f"💻 {self.device_name} ({self.screen_size}\" laptop) connected{battery_info}"
    
    def stream_content(self, content: MediaContent) -> str:
        """Stream content on laptop with power management."""
        if not self.is_connected:
            return "Device not connected. Please connect first."
        
        self.current_content = content
        # Auto-adjust quality based on battery level
        if self.battery_level < 20:
            self.current_quality = "720p"
            self.is_power_saving = True
        
        power_info = " (Power saving mode)" if self.is_power_saving else ""
        return f"💻 Streaming on {self.device_name}: {content.play()}\nQuality: {self.current_quality}{power_info}"
    
    def adjust_quality(self, quality: str) -> str:
        """Adjust streaming quality for laptop."""
        available_qualities = ["480p", "720p", "1080p"]
        if quality in available_qualities:
            self.current_quality = quality
            # Higher quality drains battery faster
            if quality == "1080p" and self.battery_level < 30:
                return f"Warning: {quality} will drain battery quickly. Current battery: {self.battery_level}%"
            return f"Quality adjusted to {quality} on {self.device_name}"
        return f"Quality {quality} not supported. Available: {', '.join(available_qualities)}"
    
    def check_compatibility(self, content: MediaContent) -> bool:
        """Check laptop compatibility with content."""
        # Laptops are versatile but limited by battery and processing power
        if hasattr(content, 'get_file_size'):
            file_size = content.get_file_size()
            if file_size > 5.0:  # GB
                return self.battery_level > 50  # Large files need good battery
        return True
    
    def toggle_power_saving(self) -> str:
        """Toggle power saving mode."""
        self.is_power_saving = not self.is_power_saving
        if self.is_power_saving:
            self.current_quality = "720p"
            return "Power saving mode enabled. Quality reduced to 720p."
        return "Power saving mode disabled. Full quality available."
    
    def update_battery_level(self, level: int) -> str:
        """Update battery level."""
        self.battery_level = max(0, min(100, level))
        if self.battery_level < 10:
            return f"⚠️ Critical battery level: {self.battery_level}%. Please charge device."
        return f"Battery level: {self.battery_level}%"


class Mobile(StreamingDevice):
    """Mobile device with small screen and battery optimization."""
    
    def __init__(self, device_id: str, device_name: str, screen_size: float,
                 os_type: str, data_plan_limit: float = 10.0):  # GB
        super().__init__(device_id, device_name, "1080p")
        self.screen_size = screen_size  # in inches
        self.os_type = os_type  # iOS, Android, etc.
        self.data_plan_limit = data_plan_limit
        self.data_used = 0.0
        self.supported_formats = ["MP4", "WebM", "HLS"]
        self.current_quality = "720p"  # Default to save data
        self.is_wifi_connected = False
        self.battery_optimization = True
        
    def connect(self) -> str:
        """Connect the mobile device to the streaming platform."""
        self.is_connected = True
        connection_type = "Wi-Fi" if self.is_wifi_connected else "Mobile Data"
        return f"📱 {self.device_name} ({self.screen_size}\" {self.os_type}) connected via {connection_type}"
    
    def stream_content(self, content: MediaContent) -> str:
        """Stream content on mobile with data management."""
        if not self.is_connected:
            return "Device not connected. Please connect first."
        
        self.current_content = content
        
        # Data usage warning
        if not self.is_wifi_connected:
            estimated_usage = content.get_file_size() * 0.1  # Streaming uses less than full file
            if self.data_used + estimated_usage > self.data_plan_limit:
                return f"⚠️ Data limit warning! Estimated usage: {estimated_usage:.2f}GB. Remaining: {self.data_plan_limit - self.data_used:.2f}GB"
        
        # Auto-adjust for mobile viewing
        if self.battery_optimization:
            self.current_quality = "720p"
        
        return f"📱 Streaming on {self.device_name}: {content.play()}\nOptimized for mobile viewing ({self.current_quality})"
    
    def adjust_quality(self, quality: str) -> str:
        """Adjust streaming quality for mobile device."""
        available_qualities = ["480p", "720p", "1080p"]
        if quality in available_qualities:
            self.current_quality = quality
            
            # Data usage warning for higher quality
            if not self.is_wifi_connected and quality in ["1080p"]:
                return f"⚠️ {quality} will use significant mobile data. Consider switching to Wi-Fi."
            return f"Quality adjusted to {quality} on {self.device_name}"
        return f"Quality {quality} not supported. Available: {', '.join(available_qualities)}"
    
    def check_compatibility(self, content: MediaContent) -> bool:
        """Check mobile compatibility with content."""
        # Mobile devices prefer smaller file sizes and shorter content
        if hasattr(content, 'get_duration'):
            duration = content.get_duration()
            if duration > 180:  # 3 hours
                return self.is_wifi_connected  # Long content needs Wi-Fi
        return True
    
    def set_wifi_status(self, wifi_connected: bool) -> str:
        """Set Wi-Fi connection status."""
        self.is_wifi_connected = wifi_connected
        if wifi_connected:
            return "📶 Connected to Wi-Fi. Higher quality streaming available."
        return "📱 Using mobile data. Quality optimized to save data."
    
    def toggle_battery_optimization(self) -> str:
        """Toggle battery optimization mode."""
        self.battery_optimization = not self.battery_optimization
        if self.battery_optimization:
            return "🔋 Battery optimization enabled. Streaming quality optimized for longer battery life."
        return "Battery optimization disabled. Full quality available (higher battery usage)."
    
    def update_data_usage(self, usage: float) -> str:
        """Update data usage."""
        self.data_used += usage
        remaining = self.data_plan_limit - self.data_used
        if remaining < 1.0:
            return f"⚠️ Data usage: {self.data_used:.2f}GB/{self.data_plan_limit}GB. Low data remaining!"
        return f"Data usage: {self.data_used:.2f}GB/{self.data_plan_limit}GB"


class SmartSpeaker(StreamingDevice):
    """Smart speaker device for audio-only content with voice control."""
    
    def __init__(self, device_id: str, device_name: str, speaker_quality: str,
                 voice_assistant: str = "Generic"):
        super().__init__(device_id, device_name, "Audio Only")
        self.speaker_quality = speaker_quality  # Basic, Premium, High-End
        self.voice_assistant = voice_assistant
        self.supported_formats = ["MP3", "AAC", "FLAC", "OGG"]
        self.current_quality = "high"
        self.volume_level = 50
        self.voice_control_enabled = True
        
    def connect(self) -> str:
        """Connect the smart speaker to the streaming platform."""
        self.is_connected = True
        return f"🔊 {self.device_name} ({self.speaker_quality} {self.voice_assistant} speaker) connected and ready for voice commands"
    
    def stream_content(self, content: MediaContent) -> str:
        """Stream audio content on smart speaker."""
        if not self.is_connected:
            return "Device not connected. Please connect first."
        
        self.current_content = content
        voice_info = f" Say 'Hey {self.voice_assistant}, pause' to control." if self.voice_control_enabled else ""
        
        # Smart speakers only handle audio content well
        if hasattr(content, 'artist') or hasattr(content, 'host'):
            return f"🔊 Playing on {self.device_name}: {content.play()}{voice_info}"
        else:
            # For video content, extract audio
            return f"🔊 Playing audio from {self.device_name}: {content.title} (audio only){voice_info}"
    
    def adjust_quality(self, quality: str) -> str:
        """Adjust audio quality for smart speaker."""
        available_qualities = ["standard", "high", "lossless"]
        if quality in available_qualities:
            self.current_quality = quality
            quality_info = {
                "standard": "Good quality, lower bandwidth",
                "high": "High quality audio",
                "lossless": "Premium lossless audio"
            }
            return f"Audio quality set to {quality}: {quality_info[quality]}"
        return f"Quality {quality} not supported. Available: {', '.join(available_qualities)}"
    
    def check_compatibility(self, content: MediaContent) -> bool:
        """Check smart speaker compatibility with content."""
        # Smart speakers work best with audio content
        if hasattr(content, 'artist') or hasattr(content, 'host'):
            return True  # Music or podcast
        return True  # Can extract audio from video content
    
    def voice_command(self, command: str) -> str:
        """Process voice commands."""
        if not self.voice_control_enabled:
            return "Voice control is disabled."
        
        command = command.lower()
        if "play" in command:
            if self.current_content:
                return f"▶️ Resuming: {self.current_content.title}"
            return "No content loaded. Please select content first."
        elif "pause" in command:
            return "⏸️ Playback paused"
        elif "volume up" in command:
            self.volume_level = min(100, self.volume_level + 10)
            return f"🔊 Volume increased to {self.volume_level}%"
        elif "volume down" in command:
            self.volume_level = max(0, self.volume_level - 10)
            return f"🔉 Volume decreased to {self.volume_level}%"
        elif "next" in command:
            return "⏭️ Playing next track"
        elif "previous" in command:
            return "⏮️ Playing previous track"
        else:
            return f"Command '{command}' not recognized. Try 'play', 'pause', 'volume up/down', 'next', or 'previous'."
    
    def toggle_voice_control(self) -> str:
        """Toggle voice control feature."""
        self.voice_control_enabled = not self.voice_control_enabled
        if self.voice_control_enabled:
            return f"🎤 Voice control enabled. Say 'Hey {self.voice_assistant}' to give commands."
        return "🔇 Voice control disabled. Use manual controls only."
    
    def get_audio_info(self) -> Dict[str, Any]:
        """Get detailed audio information."""
        return {
            "speaker_quality": self.speaker_quality,
            "voice_assistant": self.voice_assistant,
            "audio_quality": self.current_quality,
            "volume_level": self.volume_level,
            "voice_control": self.voice_control_enabled,
            "supported_formats": self.supported_formats
        } 