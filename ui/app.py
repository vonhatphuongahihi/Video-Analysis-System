"""
ADK Video Analysis UI - Streamlit Application
Main user interface for the ADK system
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
import logging
import openai
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from host_agent.main import HostAgent
from video_agent import VideoAgent
from chatbot_agent.chat_handler import ChatbotAgent


def setup_logging():
    """Setup logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def init_session_state():
    """Initialize session state variables"""
    if 'host_agent' not in st.session_state:
        st.session_state.host_agent = None
    if 'video_urls' not in st.session_state:
        st.session_state.video_urls = []
    if 'workflows' not in st.session_state:
        st.session_state.workflows = []
    if 'current_workflow' not in st.session_state:
        st.session_state.current_workflow = None


async def init_host_agent():
    """Initialize the host agent"""
    if st.session_state.host_agent is None:
        st.session_state.host_agent = HostAgent()
        await st.session_state.host_agent.start()


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="ADK Video Analysis System",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    setup_logging()
    init_session_state()
    
    # Header
    st.title("🎬 Video Analysis System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Initialize host agent
        if st.button("🚀 Initialize System"):
            with st.spinner("Initializing host agent..."):
                asyncio.run(init_host_agent())
            st.success("System initialized!")
        
        if st.session_state.host_agent:
            st.success("✅ Host Agent: Running")
            
            # System status
            if st.button("📊 Check Status"):
                with st.spinner("Checking system status..."):
                    status = asyncio.run(st.session_state.host_agent.get_system_status())
                    st.json(status)
        else:
            st.error("❌ Host Agent: Not initialized")
        
        st.markdown("---")
        
        # Navigation
        st.header("📋 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["🏠 Home", "📹 Video Processing", "💬 Chat Interface", "📊 Analytics"]
        )
    
    # Main content based on selected page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📹 Video Processing":
        show_video_processing_page()
    elif page == "💬 Chat Interface":
        show_chat_interface_page()
    elif page == "📊 Analytics":
        show_analytics_page()


def show_home_page():
    """Display the home page"""
    st.header("Welcome to ADK Video Analysis System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 What can this system do?")
        st.markdown("""
        - **📹 Process YouTube videos** - Extract metadata and transcript 
        - **🧠 Analyze content** - Extract insights and summaries
        - **💬 Chat with AI** - Ask questions about video content
        - **📊 Generate reports** - Get detailed analytics
        """)
    
    with col2:
        st.subheader("🚀 Quick Start")
        st.markdown("""
        1. Go to **Video Processing** page
        2. Enter a YouTube URL
        3. Click **Process Video**
        4. Chat with the AI about the content
        """)
    
    st.markdown("---")
    
    # Recent workflows
    if st.session_state.workflows:
        st.subheader("📋 Recent Workflows")
        for workflow in st.session_state.workflows[-5:]:
            with st.expander(f"Workflow {workflow['id']} - {workflow['status']}"):
                st.write(f"**Video:** {workflow['video_url']}")
                st.write(f"**Status:** {workflow['status']}")


def show_video_processing_page():
    """Display the video processing page"""
    st.header("📹 Video Processing")
    
    # Video URL input
    video_url = st.text_input(
        "Enter YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎬 Process Single Video", type="primary"):
            if video_url:
                process_single_video(video_url)
            else:
                st.error("Please enter a video URL")
    
    with col2:
        if st.button("📋 Batch Processing"):
            st.info("Batch processing feature coming soon!")
    
    # Batch processing
    st.subheader("📋 Batch Processing")
    batch_urls = st.text_area(
        "Enter multiple URLs (one per line):",
        placeholder="https://youtube.com/watch?v=...\nhttps://youtube.com/watch?v=..."
    )
    
    if st.button("🚀 Process Batch"):
        if batch_urls:
            urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
            process_batch_videos(urls)
        else:
            st.error("Please enter video URLs")
    
    # Display results
    if st.session_state.workflows:
        st.subheader("📊 Processing Results")
        for workflow in st.session_state.workflows:
            display_workflow_result(workflow)


def process_single_video(video_url):
    """Process a single video"""
    if not st.session_state.host_agent:
        st.error("Please initialize the system first!")
        return
    
    with st.spinner(f"Processing video: {video_url}"):
        try:
            workflow = asyncio.run(st.session_state.host_agent.process_video_workflow(video_url))
            st.session_state.workflows.append(workflow)
            st.session_state.current_workflow = workflow
            st.success(f"✅ Video processed successfully! Workflow ID: {workflow['id']}")
        except Exception as e:
            st.error(f"❌ Error processing video: {e}")


def process_batch_videos(video_urls):
    """Process multiple videos"""
    if not st.session_state.host_agent:
        st.error("Please initialize the system first!")
        return
    
    with st.spinner(f"Processing {len(video_urls)} videos..."):
        try:
            workflow_ids = asyncio.run(st.session_state.host_agent.batch_process_videos(video_urls))
            st.success(f"✅ Submitted {len(workflow_ids)} videos for processing")
            st.write(f"Workflow IDs: {workflow_ids}")
        except Exception as e:
            st.error(f"❌ Error in batch processing: {e}")


def display_workflow_result(workflow):
    """Display workflow results"""
    with st.expander(f"Workflow {workflow['id']} - {workflow['status']}"):
        st.write(f"**Video URL:** {workflow['video_url']}")
        st.write(f"**Status:** {workflow['status']}")
        
        if workflow['status'] == 'completed':
            results = workflow.get('results', {})
            
            if 'video' in results:
                video_data = results['video']
                st.subheader("📹 Video Information")
                st.write(f"**Title:** {video_data.metadata.title}")
                st.write(f"**Duration:** {video_data.metadata.duration} seconds")
                st.write(f"**Channel:** {video_data.metadata.channel_name}")
                st.write(f"**Transcript Length:** {len(video_data.transcript)} characters")
            
            if 'analysis' in results:
                analysis = results['analysis']
                st.subheader("📊 Analysis Results")
                st.write(f"**Key Topics:** {', '.join(analysis.get('key_topics', []))}")
                st.write(f"**Sentiment:** {analysis.get('sentiment', 'Unknown')}")
                st.write(f"**Summary:** {analysis.get('summary', 'No summary available')}")


def show_chat_interface_page():
    """Display the chat interface page"""
    st.header("💬 Chat Interface")
    
    if not st.session_state.current_workflow:
        st.warning("Please process a video first to enable chat!")
        return
    
    # Chat interface
    st.subheader("Ask questions about the video:")
    
    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(f"👤 **You:** {message['content']}")
        else:
            st.write(f"🤖 **AI:** {message['content']}")
    
    # Chat input
    user_input = st.text_input("Your question:", key="chat_input")
    
    if st.button("💬 Send"):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Gọi ChatbotAgent thực sự
            chatbot = ChatbotAgent()
            # Lấy context từ workflow hiện tại
            context = {
                "transcript": st.session_state.current_workflow["results"]["video"].transcript,
                "analysis": st.session_state.current_workflow["results"]["analysis"]
            }
            # Gọi hàm async trong sync context
            response = asyncio.run(chatbot.process_message("user", user_input, context))
            ai_response = response.message

            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()


def show_analytics_page():
    """Display the analytics page"""
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.host_agent:
        st.warning("Please initialize the system first!")
        return
    
    # System metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Workflows", len(st.session_state.workflows))
    
    with col2:
        completed = len([w for w in st.session_state.workflows if w['status'] == 'completed'])
        st.metric("Completed", completed)
    
    with col3:
        failed = len([w for w in st.session_state.workflows if w['status'] == 'failed'])
        st.metric("Failed", failed)
    
    # Workflow status chart
    if st.session_state.workflows:
        st.subheader("📈 Workflow Status Distribution")
        
        status_counts = {}
        for workflow in st.session_state.workflows:
            status = workflow['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.bar_chart(status_counts)



if __name__ == "__main__":
    main() 