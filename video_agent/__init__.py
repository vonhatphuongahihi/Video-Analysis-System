"""
Video Agent Package
YouTube video processing and analysis agent
"""

from .agent import VideoAgent, VideoMetadata, VideoProcessingResult
from .agent_executor import VideoAgentExecutor, ProcessingTask
from .prompt import VideoAgentPrompts

__version__ = "0.1.0"
__author__ = "ADK Team"

__all__ = [
    "VideoAgent",
    "VideoMetadata", 
    "VideoProcessingResult",
    "VideoAgentExecutor",
    "ProcessingTask",
    "VideoAgentPrompts"
] 