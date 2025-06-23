"""
Video Agent Executor - Manages execution of video processing tasks
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .agent import VideoAgent, VideoProcessingResult


@dataclass
class ProcessingTask:
    """Data class for processing tasks"""
    task_id: str
    video_url: str
    status: str  # pending, processing, completed, failed
    created_at: float
    completed_at: Optional[float] = None
    result: Optional[VideoProcessingResult] = None
    error: Optional[str] = None


class VideoAgentExecutor:
    """
    Executor for Video Agent tasks
    Handles task queuing, execution, and result management
    """
    
    def __init__(self, agent: VideoAgent, max_concurrent_tasks: int = 3):
        self.agent = agent
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logging.getLogger(__name__)
        
        # Task management
        self.tasks: Dict[str, ProcessingTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Background task
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the executor background processor"""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_queue())
        self.logger.info("Video Agent Executor started")
    
    async def stop(self):
        """Stop the executor background processor"""
        if not self._running:
            return
        
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Video Agent Executor stopped")
    
    async def process_video(self, video_url: str) -> str:
        """
        Submit a video for processing
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Task ID for tracking
        """
        import uuid
        
        task_id = str(uuid.uuid4())
        task = ProcessingTask(
            task_id=task_id,
            video_url=video_url,
            status="pending",
            created_at=time.time()
        )
        
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        
        self.logger.info(f"Submitted video processing task {task_id} for {video_url}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[ProcessingTask]:
        """Get the status of a processing task"""
        return self.tasks.get(task_id)
    
    async def get_all_tasks(self) -> List[ProcessingTask]:
        """Get all processing tasks"""
        return list(self.tasks.values())
    
    async def _process_queue(self):
        """Background task to process the queue"""
        while self._running:
            try:
                # Wait for a task
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Process the task
                asyncio.create_task(self._process_single_task(task))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in queue processor: {e}")
    
    async def _process_single_task(self, task: ProcessingTask):
        """Process a single video processing task"""
        async with self.semaphore:
            try:
                # Update status
                task.status = "processing"
                self.logger.info(f"Processing task {task.task_id}")
                
                # Process the video
                result = await self.agent.process_video(task.video_url)
                
                # Update task with result
                task.status = "completed"
                task.completed_at = time.time()
                task.result = result
                
                self.logger.info(f"Completed task {task.task_id}")
                
            except Exception as e:
                # Update task with error
                task.status = "failed"
                task.completed_at = time.time()
                task.error = str(e)
                
                self.logger.error(f"Failed task {task.task_id}: {e}")
    
    async def process_video_sync(self, video_url: str) -> VideoProcessingResult:
        """
        Process a video synchronously (blocking)
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            VideoProcessingResult
        """
        self.logger.info(f"Processing video synchronously: {video_url}")
        return await self.agent.process_video(video_url)
    
    async def batch_process_videos(self, video_urls: List[str]) -> List[str]:
        """
        Submit multiple videos for batch processing
        
        Args:
            video_urls: List of YouTube video URLs
            
        Returns:
            List of task IDs
        """
        task_ids = []
        for url in video_urls:
            task_id = await self.process_video(url)
            task_ids.append(task_id)
        
        self.logger.info(f"Submitted {len(video_urls)} videos for batch processing")
        return task_ids
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.task_queue.qsize()
    
    def get_active_tasks_count(self) -> int:
        """Get number of currently active tasks"""
        return sum(1 for task in self.tasks.values() if task.status == "processing") 