"""
Host Agent - Main orchestrator for the ADK application
Coordinates all other agents and manages the overall workflow
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from video_agent import VideoAgent, VideoAgentExecutor
# TODO: Import other agents when they're created
# from nlp_agent import NLPAgent
# from chatbot_agent import ChatbotAgent


class HostAgent:
    """
    Host Agent - Main orchestrator
    Manages the workflow between different specialized agents
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.video_agent = VideoAgent()
        self.video_executor = VideoAgentExecutor(self.video_agent)
        
        # TODO: Initialize other agents
        # self.nlp_agent = NLPAgent()
        # self.chatbot_agent = ChatbotAgent()
        
        # Workflow state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    async def start(self):
        """Start the host agent and all sub-agents"""
        self.logger.info("Starting Host Agent...")
        
        # Start video executor
        await self.video_executor.start()
        
        # TODO: Start other agents
        # await self.nlp_agent.start()
        # await self.chatbot_agent.start()
        
        self.logger.info("Host Agent started successfully")
    
    async def stop(self):
        """Stop the host agent and all sub-agents"""
        self.logger.info("Stopping Host Agent...")
        
        # Stop video executor
        await self.video_executor.stop()
        
        # TODO: Stop other agents
        # await self.nlp_agent.stop()
        # await self.chatbot_agent.stop()
        
        self.logger.info("Host Agent stopped")
    
    async def process_video_workflow(self, video_url: str) -> Dict[str, Any]:
        """
        Complete workflow for processing a video
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Complete workflow results
        """
        workflow_id = f"workflow_{len(self.active_workflows) + 1}"
        self.logger.info(f"Starting video workflow {workflow_id} for: {video_url}")
        
        workflow = {
            "id": workflow_id,
            "video_url": video_url,
            "status": "processing",
            "steps": [],
            "results": {}
        }
        
        self.active_workflows[workflow_id] = workflow
        
        try:
            # Step 1: Process video
            self.logger.info(f"Step 1: Processing video...")
            video_result = await self.video_agent.process_video(video_url)
            workflow["steps"].append({
                "name": "video_processing",
                "status": "completed",
                "result": video_result
            })
            workflow["results"]["video"] = video_result
            
            # Step 2: Analyze content (placeholder for NLP agent)
            self.logger.info(f"Step 2: Analyzing content...")
            content_analysis = await self.video_agent.analyze_video_content(video_url)
            workflow["steps"].append({
                "name": "content_analysis", 
                "status": "completed",
                "result": content_analysis
            })
            workflow["results"]["analysis"] = content_analysis
            
            # TODO: Step 3: NLP processing
            # self.logger.info(f"Step 3: NLP processing...")
            # nlp_result = await self.nlp_agent.process_text(video_result.transcript)
            # workflow["steps"].append({
            #     "name": "nlp_processing",
            #     "status": "completed", 
            #     "result": nlp_result
            # })
            # workflow["results"]["nlp"] = nlp_result
            
            # TODO: Step 4: Prepare chatbot responses
            # self.logger.info(f"Step 4: Preparing chatbot responses...")
            # chat_prep = await self.chatbot_agent.prepare_responses(workflow["results"])
            # workflow["steps"].append({
            #     "name": "chatbot_preparation",
            #     "status": "completed",
            #     "result": chat_prep
            # })
            # workflow["results"]["chatbot"] = chat_prep
            
            workflow["status"] = "completed"
            self.logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            raise
        
        return workflow
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow"""
        return self.active_workflows.get(workflow_id)
    
    async def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        return list(self.active_workflows.values())
    
    async def batch_process_videos(self, video_urls: List[str]) -> List[str]:
        """
        Process multiple videos in batch
        
        Args:
            video_urls: List of YouTube video URLs
            
        Returns:
            List of workflow IDs
        """
        workflow_ids = []
        
        for url in video_urls:
            try:
                workflow = await self.process_video_workflow(url)
                workflow_ids.append(workflow["id"])
            except Exception as e:
                self.logger.error(f"Failed to process video {url}: {e}")
        
        return workflow_ids
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "host_agent": "running",
            "video_agent": "running",
            "video_executor": {
                "queue_size": self.video_executor.get_queue_size(),
                "active_tasks": self.video_executor.get_active_tasks_count()
            },
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len([w for w in self.active_workflows.values() if w["status"] == "completed"]),
            "failed_workflows": len([w for w in self.active_workflows.values() if w["status"] == "failed"])
        }


async def main():
    """Main function to run the host agent"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and start host agent
    host_agent = HostAgent()
    
    try:
        await host_agent.start()
        
        # Example usage
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"Processing video: {test_url}")
        
        workflow = await host_agent.process_video_workflow(test_url)
        print(f"Workflow completed: {workflow['id']}")
        
        # Get system status
        status = await host_agent.get_system_status()
        print(f"System status: {status}")
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await host_agent.stop()


if __name__ == "__main__":
    asyncio.run(main()) 