"""
Chatbot Agent - Handles user interactions and responses
Provides intelligent responses based on processed video data
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import openai
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ChatMessage:
    """Data class for chat messages"""
    id: str
    user_id: str
    content: str
    timestamp: datetime
    message_type: str  # user, assistant, system
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """Data class for chat responses"""
    message: str
    confidence: float
    sources: List[str]
    suggested_questions: List[str]
    metadata: Dict[str, Any]


class ChatbotAgent:
    """
    Chatbot Agent for handling user interactions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Chat history
        self.conversation_history: List[ChatMessage] = []
        
        # TODO: Initialize AI models and APIs
        # self.openai_client = OpenAI(api_key=config.get("openai_api_key"))
        # self.anthropic_client = Anthropic(api_key=config.get("anthropic_api_key"))
    
    async def process_message(self, user_id: str, message: str, context: Optional[dict] = None) -> ChatResponse:
        """
        Process a user message and generate a response
        
        Args:
            user_id: ID of the user
            message: User's message
            context: Additional context (video data, etc.)
            
        Returns:
            ChatResponse with the response
        """
        self.logger.info(f"Processing message from user {user_id}: {message[:50]}...")
        
        # Lấy transcript và phân tích từ context nếu có
        transcript = context.get("transcript", "") if context else ""
        analysis = context.get("analysis", {}) if context else {}

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"Video transcript:\n{transcript}\n\nAnalysis:\n{analysis}\n\nUser question: {message}\n\nAnswer in detail in English:"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in answering questions about video content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        answer = response.choices[0].message.content.strip()

        return ChatResponse(
            message=answer,
            confidence=0.95,
            sources=["openai"],
            suggested_questions=[
                "What are the main topics of the video?",
                "Can you summarize the video content?",
                "What is the overall sentiment of the video?"
            ],
            metadata={"response_type": "openai"}
        )
    
    async def generate_response_with_context(self, message: str, video_data: Dict[str, Any], nlp_data: Dict[str, Any]) -> ChatResponse:
        """
        Generate a response using video and NLP context
        
        Args:
            message: User's message
            video_data: Processed video data
            nlp_data: NLP analysis results
            
        Returns:
            ChatResponse with contextual response
        """
        self.logger.info("Generating contextual response...")
        
        # TODO: Implement contextual response generation
        # This would use the video metadata, transcript, and NLP analysis
        
        return ChatResponse(
            message=f"Based on the video '{video_data.get('title', 'Unknown')}', here's what I found: {nlp_data.get('summary', 'No summary available')}",
            confidence=0.9,
            sources=["video_metadata", "transcript", "nlp_analysis"],
            suggested_questions=[
                "Tell me more about the main topics",
                "What are the key insights?",
                "Can you analyze the sentiment?"
            ],
            metadata={
                "video_title": video_data.get("title"),
                "analysis_type": "contextual"
            }
        )
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get conversation history for a user"""
        user_messages = [msg for msg in self.conversation_history if msg.user_id == user_id]
        return user_messages[-limit:] if limit > 0 else user_messages
    
    async def clear_conversation_history(self, user_id: str):
        """Clear conversation history for a user"""
        self.conversation_history = [msg for msg in self.conversation_history if msg.user_id != user_id]
        self.logger.info(f"Cleared conversation history for user {user_id}")
    
    async def get_suggested_questions(self, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Get suggested questions based on context"""
        # TODO: Implement intelligent question suggestions
        return [
            "What is this video about?",
            "What are the main topics discussed?",
            "Can you summarize the key points?",
            "What is the overall sentiment?",
            "Who is the target audience?"
        ]
    
    async def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent from message"""
        # TODO: Implement intent analysis
        return {
            "intent": "general_question",
            "confidence": 0.8,
            "entities": [],
            "sentiment": "neutral"
        } 