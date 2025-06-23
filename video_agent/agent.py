"""
Video Agent - Core agent for YouTube video processing
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from googleapiclient.discovery import build
import os
import isodate
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import openai
import yt_dlp

from .prompt import VideoAgentPrompts

load_dotenv()

@dataclass
class VideoMetadata:
    """Data class for video metadata"""
    title: str
    description: str
    duration: int
    view_count: int
    upload_date: str
    channel_name: str
    video_id: str


@dataclass
class VideoProcessingResult:
    """Data class for video processing results"""
    video_url: str
    metadata: VideoMetadata
    transcript: str
    video_file_path: Optional[str] = None
    processing_time: float = 0.0


class VideoAgent:
    """
    Video Agent responsible for:
    - Downloading YouTube videos
    - Extracting transcripts
    - Extracting metadata
    - Processing video content
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.prompts = VideoAgentPrompts()
        
        # Initialize processing directories
        self.output_dir = Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_video(self, video_url: str) -> VideoProcessingResult:
        """
        Main method to process a YouTube video
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            VideoProcessingResult with all processed data
        """
        self.logger.info(f"Starting video processing for: {video_url}")
        
        try:
            # Extract video ID
            video_id = self._extract_video_id(video_url)
            
            # Get video metadata
            metadata = await self._get_video_metadata(video_id)
            
            # Extract transcript
            transcript = await self._extract_transcript(video_id)
            
            # Create result
            result = VideoProcessingResult(
                video_url=video_url,
                metadata=metadata,
                transcript=transcript
            )
            
            self.logger.info(f"Video processing completed for: {video_url}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing video {video_url}: {e}")
            raise
    
    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from YouTube URL"""
        # Simple extraction - can be enhanced with regex
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError(f"Invalid YouTube URL: {video_url}")
    
    async def _get_video_metadata(self, video_id: str) -> VideoMetadata:
        """Get video metadata from YouTube API"""
        self.logger.info(f"Getting metadata for video: {video_id}")

        # Get API key from environment variable
        api_key = os.getenv("YOUTUBE_API_KEY")
        youtube = build("youtube", "v3", developerKey=api_key)

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            raise ValueError(f"No video found for ID: {video_id}")

        info = items[0]
        snippet = info["snippet"]
        stats = info["statistics"]
        content = info["contentDetails"]

        # Convert ISO 8601 duration to seconds (can use isodate.parse_duration)
        duration = int(isodate.parse_duration(content["duration"]).total_seconds())

        return VideoMetadata(
            title=snippet["title"],
            description=snippet.get("description", ""),
            duration=duration,
            view_count=int(stats.get("viewCount", 0)),
            upload_date=snippet.get("publishedAt", "")[:10],
            channel_name=snippet.get("channelTitle", ""),
            video_id=video_id
        )
    
    async def _extract_transcript(self, video_id: str) -> str:
        """Extract transcript from YouTube video"""
        self.logger.info(f"Extracting transcript for video: {video_id}")
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['vi', 'en'])
            transcript = " ".join([item['text'] for item in transcript_list])
            return transcript
        except Exception as e:
            self.logger.warning(f"Transcript not available: {e}")
            return ""
    
    async def analyze_video_content(self, video_url: str) -> dict:
        # Process video to get transcript
        result = await self.process_video(video_url)
        transcript = result.transcript

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 1. Summarize content
        summary_prompt = f"Summarize the following video content in English:\n\n{transcript}"
        summary_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a video summarization expert."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=300
        )
        summary = summary_response.choices[0].message.content.strip()

        # 2. Extract topics
        topic_prompt = f"List the main topics of the following video (as a list, in English):\n\n{transcript}"
        topic_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a video topic analysis expert."},
                {"role": "user", "content": topic_prompt}
            ],
            max_tokens=100
        )
        topics = topic_response.choices[0].message.content.strip().split('\n')

        # 3. Sentiment analysis
        sentiment_prompt = f"Analyze the overall sentiment of the following video (positive, negative, neutral):\n\n{transcript}"
        sentiment_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a sentiment analysis expert. Always answer with only one of these words: positive, negative, or neutral, in English."},
                {"role": "user", "content": sentiment_prompt}
            ],
            max_tokens=10
        )
        sentiment_raw = sentiment_response.choices[0].message.content.strip().lower()
        # Normalize sentiment to English
        if "positive" in sentiment_raw:
            sentiment = "positive"
        elif "negative" in sentiment_raw:
            sentiment = "negative"
        elif "neutral" in sentiment_raw:
            sentiment = "neutral"
        else:
            sentiment = "neutral"

        return {
            "video_url": video_url,
            "title": result.metadata.title,
            "duration_minutes": result.metadata.duration // 60,
            "transcript_length": len(transcript),
            "key_topics": topics,
            "sentiment": sentiment,
            "summary": summary
        } 