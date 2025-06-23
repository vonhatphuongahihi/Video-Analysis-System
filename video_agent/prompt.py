"""
Video Agent Prompts - Prompt templates for video processing tasks
"""

from typing import Dict, Any


class VideoAgentPrompts:
    """
    Prompt templates for Video Agent tasks
    """
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.prompts = self._get_prompts()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for video agent"""
        return """You are a Video Processing Agent specialized in analyzing YouTube videos. 
Your capabilities include:
- Extracting video metadata (title, description, duration, etc.)
- Downloading video content
- Extracting transcripts and captions
- Analyzing video content for insights
- Processing video data for further analysis

Always provide accurate, detailed information and handle errors gracefully."""

    def _get_prompts(self) -> Dict[str, str]:
        """Get all prompt templates"""
        return {
            "video_analysis": """Analyze the following YouTube video:

Video URL: {video_url}
Title: {title}
Description: {description}
Duration: {duration} seconds
Channel: {channel_name}

Please provide:
1. Key topics discussed
2. Main insights
3. Content summary
4. Sentiment analysis
5. Target audience
6. Key takeaways

Transcript: {transcript}""",

            "content_summary": """Create a comprehensive summary of this video content:

Title: {title}
Transcript: {transcript}

Please provide:
- Executive summary (2-3 sentences)
- Key points (bullet points)
- Main arguments or findings
- Conclusion or recommendations""",

            "topic_extraction": """Extract the main topics and themes from this video:

Title: {title}
Transcript: {transcript}

Please identify:
- Primary topic
- Secondary topics
- Key themes
- Related concepts
- Industry/domain classification""",

            "sentiment_analysis": """Analyze the sentiment and tone of this video:

Title: {title}
Transcript: {transcript}

Please evaluate:
- Overall sentiment (positive/negative/neutral)
- Emotional tone
- Confidence level
- Objectivity vs subjectivity
- Engagement level""",

            "metadata_enhancement": """Enhance the video metadata with additional insights:

Original Metadata:
- Title: {title}
- Description: {description}
- Duration: {duration}
- Channel: {channel_name}

Please provide:
- Content category
- Difficulty level
- Prerequisites
- Learning objectives
- Target audience
- Content quality indicators""",

            "error_handling": """An error occurred while processing the video:

Error: {error}
Video URL: {video_url}

Please provide:
- Error analysis
- Possible causes
- Suggested solutions
- Alternative approaches
- Recovery recommendations"""
        }
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Get a formatted prompt
        
        Args:
            prompt_name: Name of the prompt template
            **kwargs: Variables to format the prompt
            
        Returns:
            Formatted prompt string
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"Unknown prompt: {prompt_name}")
        
        template = self.prompts[prompt_name]
        return template.format(**kwargs)
    
    def get_video_analysis_prompt(self, video_data: Dict[str, Any]) -> str:
        """Get formatted video analysis prompt"""
        return self.get_prompt("video_analysis", **video_data)
    
    def get_content_summary_prompt(self, title: str, transcript: str) -> str:
        """Get formatted content summary prompt"""
        return self.get_prompt("content_summary", title=title, transcript=transcript)
    
    def get_topic_extraction_prompt(self, title: str, transcript: str) -> str:
        """Get formatted topic extraction prompt"""
        return self.get_prompt("topic_extraction", title=title, transcript=transcript)
    
    def get_sentiment_analysis_prompt(self, title: str, transcript: str) -> str:
        """Get formatted sentiment analysis prompt"""
        return self.get_prompt("sentiment_analysis", title=title, transcript=transcript)
    
    def get_metadata_enhancement_prompt(self, metadata: Dict[str, Any]) -> str:
        """Get formatted metadata enhancement prompt"""
        return self.get_prompt("metadata_enhancement", **metadata)
    
    def get_error_handling_prompt(self, error: str, video_url: str) -> str:
        """Get formatted error handling prompt"""
        return self.get_prompt("error_handling", error=error, video_url=video_url) 