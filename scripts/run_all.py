#!/usr/bin/env python3
"""
ADK System Runner - Main script to run the entire ADK system
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from host_agent.main import HostAgent
from video_agent import VideoAgent, VideoAgentExecutor


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/adk_system.log')
        ]
    )


async def run_video_agent_test():
    """Run video agent test"""
    print("Testing Video Agent...")
    
    agent = VideoAgent()
    executor = VideoAgentExecutor(agent)
    
    # Test video URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        await executor.start()
        
        # Test single video processing
        result = await agent.process_video(test_url)
        print(f"Video processed: {result.metadata.title}")
        
        # Test batch processing
        task_id = await executor.process_video(test_url)
        print(f"Task submitted: {task_id}")
        
        await executor.stop()
        
    except Exception as e:
        print(f"Video agent test failed: {e}")
        await executor.stop()


async def run_host_agent_test():
    """Run host agent test"""
    print("Testing Host Agent...")
    
    host_agent = HostAgent()
    
    try:
        await host_agent.start()
        
        # Test video workflow
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        workflow = await host_agent.process_video_workflow(test_url)
        print(f"Workflow completed: {workflow['id']}")
        
        # Get system status
        status = await host_agent.get_system_status()
        print(f"System status: {status}")
        
        await host_agent.stop()
        
    except Exception as e:
        print(f"Host agent test failed: {e}")
        await host_agent.stop()


async def run_full_system():
    """Run the full ADK system"""
    print("Starting Full ADK System...")
    
    host_agent = HostAgent()
    
    try:
        await host_agent.start()
        print("✅ Host Agent started successfully")
        
        # Keep the system running
        print("🔄 System is running. Press Ctrl+C to stop...")
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        await host_agent.stop()
        print("✅ System stopped")


def run_ui():
    """Run the Streamlit UI"""
    print("Starting Streamlit UI...")
    
    import subprocess
    import os
    
    ui_path = Path(__file__).parent.parent / "ui" / "app.py"
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(ui_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start UI: {e}")
    except KeyboardInterrupt:
        print("\n🛑 UI stopped")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ADK System Runner")
    parser.add_argument(
        "--mode",
        choices=["test", "video", "host", "full", "ui"],
        default="test",
        help="Run mode: test (all tests), video (video agent only), host (host agent only), full (full system), ui (streamlit interface)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    print(f"🎬 ADK System Runner - Mode: {args.mode}")
    print("=" * 50)
    
    try:
        if args.mode == "test":
            # Run all tests
            asyncio.run(run_video_agent_test())
            print()
            asyncio.run(run_host_agent_test())
            
        elif args.mode == "video":
            # Run video agent test only
            asyncio.run(run_video_agent_test())
            
        elif args.mode == "host":
            # Run host agent test only
            asyncio.run(run_host_agent_test())
            
        elif args.mode == "full":
            # Run full system
            asyncio.run(run_full_system())
            
        elif args.mode == "ui":
            # Run UI
            run_ui()
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 