#!/usr/bin/env python3
"""
Video Agent - Main entry point
Handles YouTube video processing, download, and transcript extraction
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from video_agent.agent import VideoAgent
from video_agent.agent_executor import VideoAgentExecutor


async def main():
    """Main function to run the video agent"""
    print("🎥 Starting Video Agent...")
    
    # Initialize the video agent
    agent = VideoAgent()
    executor = VideoAgentExecutor(agent)
    
    # Example usage
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    
    try:
        result = await executor.process_video(video_url)
        print(f"✅ Video processing completed: {result}")
    except Exception as e:
        print(f"❌ Error processing video: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 