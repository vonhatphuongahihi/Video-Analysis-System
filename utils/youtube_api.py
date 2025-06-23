"""
YouTube API Utilities
Helper functions for YouTube API integration
"""

import logging
from typing import Dict, Any, Optional, List
import re
from urllib.parse import urlparse, parse_qs


class YouTubeAPIHelper:
    """
    Helper class for YouTube API operations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # TODO: Initialize YouTube API client
        # self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if invalid
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            r'youtu\.be\/([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def validate_youtube_url(self, url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid YouTube URL
        """
        video_id = self.extract_video_id(url)
        return video_id is not None and len(video_id) == 11
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get video information from YouTube API
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video information dictionary
        """
        # TODO: Implement actual YouTube API call
        # For now, return mock data
        self.logger.info(f"Getting video info for: {video_id}")
        
        return {
            "video_id": video_id,
            "title": f"Sample Video {video_id}",
            "description": "This is a sample video description",
            "duration": "PT5M30S",  
            "view_count": 1000,
            "like_count": 100,
            "upload_date": "2024-01-01",
            "channel_name": "Sample Channel",
            "channel_id": "UC_sample",
            "tags": ["sample", "video", "test"],
            "category_id": "22",  
            "default_language": "en"
        }
    
    def get_video_transcript(self, video_id: str, language: str = "en") -> str:
        """
        Get video transcript/captions
        
        Args:
            video_id: YouTube video ID
            language: Language code (default: en)
            
        Returns:
            Transcript text
        """
        # TODO: Implement transcript extraction
        # This would use youtube_transcript_api or similar
        self.logger.info(f"Getting transcript for: {video_id} in {language}")
        
        return f"This is a sample transcript for video {video_id}. " \
               f"It contains the spoken content from the video in {language} language."
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of video information
        """
        # TODO: Implement YouTube search API
        self.logger.info(f"Searching for: {query}")
        
        # Mock search results
        return [
            {
                "video_id": f"search_result_{i}",
                "title": f"Search Result {i} for {query}",
                "description": f"Description for search result {i}",
                "channel_name": f"Channel {i}",
                "upload_date": "2024-01-01",
                "view_count": 1000 + i * 100
            }
            for i in range(1, min(max_results + 1, 6))
        ]
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get channel information
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel information
        """
        # TODO: Implement channel info API
        self.logger.info(f"Getting channel info for: {channel_id}")
        
        return {
            "channel_id": channel_id,
            "title": f"Channel {channel_id}",
            "description": "Sample channel description",
            "subscriber_count": 10000,
            "video_count": 100,
            "view_count": 1000000,
            "created_date": "2020-01-01",
            "country": "US"
        }
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get videos from a playlist
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos
            
        Returns:
            List of video information
        """
        # TODO: Implement playlist API
        self.logger.info(f"Getting playlist videos for: {playlist_id}")
        
        return [
            {
                "video_id": f"playlist_video_{i}",
                "title": f"Playlist Video {i}",
                "description": f"Description for playlist video {i}",
                "position": i,
                "channel_name": "Playlist Channel"
            }
            for i in range(1, min(max_results + 1, 11))
        ]


def extract_video_id_simple(url: str) -> Optional[str]:
    """
    Simple function to extract video ID from YouTube URL
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None
    """
    helper = YouTubeAPIHelper()
    return helper.extract_video_id(url)


def validate_youtube_url_simple(url: str) -> bool:
    """
    Simple function to validate YouTube URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid
    """
    helper = YouTubeAPIHelper()
    return helper.validate_youtube_url(url) 