"""
Streamlit app for Mutual Fund FAQ Assistant using RAG
"""

import streamlit as st
import os
import sys
from typing import Dict, List, Optional
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Parag Parikh Mutual Funds Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d4aa;
        text-align: center;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .message-user {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #00d4aa;
    }
    .message-assistant {
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #888;
    }
    .source-link {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.85rem;
    }
    .stButton>button {
        background-color: #00d4aa;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00b894;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "initialization_error" not in st.session_state:
    st.session_state.initialization_error = None
if "initialization_attempted" not in st.session_state:
    st.session_state.initialization_attempted = False

@st.cache_resource
def initialize_rag_pipeline():
    """Initialize RAG pipeline (cached)"""
    try:
        from rag_pipeline import RAGPipeline
        
        # Check for API key in Streamlit secrets or environment
        api_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, 'secrets') else None
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return None, "GROQ_API_KEY not found. Please set it in Streamlit secrets or environment variables."
        
        pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
        
        # Check if vector DB needs to be built
        try:
            # Try to load existing vector DB
            from data_storage import DataStorage
            storage = DataStorage()
            data = storage.load_data()
            
            if data and data.get("funds"):
                # Check if vector DB exists and has data
                import os.path as path
                from config_rag import VECTOR_DB_PATH
                
                vector_db_file = os.path.join(VECTOR_DB_PATH, "mutual_funds.json")
                if not path.exists(vector_db_file) or os.path.getsize(vector_db_file) == 0:
                    logger.info("Vector DB missing or empty, building index...")
                    pipeline.build_index()
                    logger.info("Vector index built successfully")
        except Exception as e:
            logger.warning(f"Could not check/build vector DB: {e}")
        
        return pipeline, None
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}", exc_info=True)
        return None, str(e)

def get_rag_pipeline():
    """Get or initialize RAG pipeline"""
    if not st.session_state.initialization_attempted:
        st.session_state.initialization_attempted = True
        with st.spinner("Initializing RAG pipeline (this may take a moment on first load)..."):
            pipeline, error = initialize_rag_pipeline()
            st.session_state.rag_pipeline = pipeline
            st.session_state.initialization_error = error
    
    return st.session_state.rag_pipeline, st.session_state.initialization_error

def process_query(query: str) -> Dict:
    """Process a query using RAG pipeline"""
    pipeline, error = get_rag_pipeline()
    
    if error:
        return {
            "success": False,
            "answer": f"Error: {error}",
            "source_urls": []
        }
    
    if not pipeline:
        return {
            "success": False,
            "answer": "RAG pipeline not initialized. Please check your GROQ_API_KEY environment variable.",
            "source_urls": []
        }
    
    try:
        response = pipeline.answer_query(query)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return {
            "success": False,
            "answer": f"Error processing query: {str(e)}",
            "source_urls": []
        }

# Main UI
st.markdown('<div class="main-header">📊 Parag Parikh Mutual Funds Assistant</div>', unsafe_allow_html=True)

# Info box
st.markdown("""
<div class="info-box">
    <strong>📌 Important:</strong> This assistant is specifically designed for <strong>Parag Parikh Mutual Funds only</strong>. 
    It does not support queries about funds from other Asset Management Companies (AMCs).
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    Ask me anything about Parag Parikh mutual funds. I can help you find information about:
    - Expense ratios
    - Exit loads
    - Minimum SIP amounts
    - Lock-in periods
    - Riskometers
    - Benchmarks
    - Returns
    """)
    
    # Check pipeline status
    pipeline, error = get_rag_pipeline()
    if pipeline:
        st.success("✅ RAG Pipeline Ready")
    elif error:
        st.error(f"❌ Error: {error}")
    else:
        st.info("⏳ Initializing...")
    
    st.markdown("---")
    st.markdown("**Disclaimer:** This assistant provides factual information only for Parag Parikh Mutual Funds. It does not support other AMCs and does not provide investment advice.")
    
    # Clear chat button in sidebar
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat interface
st.header("💬 Chat")

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    source_urls = message.get("source_urls", [])
    
    if role == "user":
        st.markdown(f'<div class="message-user"><strong>You:</strong><br>{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="message-assistant"><strong>Assistant:</strong><br>{content}</div>', unsafe_allow_html=True)
        
        if source_urls:
            url = source_urls[0]
            if url and url.startswith("http"):
                st.markdown(f"""
                <div class="source-link">
                    <strong>Source:</strong> <a href="{url}" target="_blank">{url if len(url) < 80 else url[:77] + "..."}</a>
                    <br><small>Note: Source URLs are from when data was scraped. If this link doesn't work, please search for the fund on <a href="https://groww.in/mutual-funds" target="_blank">Groww</a>.</small>
                </div>
                """, unsafe_allow_html=True)

# Chat input
query = st.chat_input("Ask a question about Parag Parikh mutual funds...")

if query:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Process query
    with st.spinner("Thinking..."):
        response = process_query(query)
    
    # Add assistant response
    answer = response.get("answer", "Sorry, I couldn't process your query.")
    source_urls = response.get("source_urls", [])
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "source_urls": source_urls
    })
    
    # Rerun to update UI
    st.rerun()

