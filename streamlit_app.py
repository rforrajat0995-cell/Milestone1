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
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #00b894;
    }
    /* New Chat button styling */
    div[data-testid="stButton"]:has(button:contains("New Chat")) button {
        width: 100%;
        background-color: #00d4aa;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f;
    }
    /* Expander styling */
    .streamlit-expanderHeader {
        color: #ffffff;
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
    # Header with logo
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #00d4aa; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">MF</div>
        <h2 style="margin: 0; color: #ffffff;">My Chats</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Connection Status
    pipeline, error = get_rag_pipeline()
    if pipeline:
        st.markdown("""
        <div style="background-color: rgba(0, 212, 170, 0.1); border: 1px solid rgba(0, 212, 170, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #00d4aa;"></div>
                <span style="color: #00d4aa; font-weight: 500;">Backend Connected</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mode Status
        st.markdown("""
        <div style="background-color: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
            <div style="font-size: 11px; color: #888; text-transform: uppercase; margin-bottom: 8px;">MODE:</div>
            <div style="background-color: #00d4aa; color: white; padding: 6px 12px; border-radius: 6px; display: inline-block; font-weight: 500; margin-bottom: 8px;">
                ✨ Groq API
            </div>
            <div style="font-size: 12px; color: #888; margin-top: 8px;">
                Embeddings: Local | LLM: Groq
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif error:
        st.markdown("""
        <div style="background-color: rgba(255, 0, 0, 0.1); border: 1px solid rgba(255, 0, 0, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #ff4444;"></div>
                <span style="color: #ff4444; font-weight: 500;">Backend Disconnected</span>
            </div>
            <div style="font-size: 12px; color: #888; margin-top: 8px;">{}</div>
        </div>
        """.format(error[:100]), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #ffc107;"></div>
                <span style="color: #ffc107; font-weight: 500;">Initializing...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chats Section
    st.markdown("### Chats")
    st.markdown("""
    <div style="color: #888; font-size: 12px; margin-bottom: 10px;">
        Current session chat history
    </div>
    """, unsafe_allow_html=True)
    
    # Show chat count
    if st.session_state.messages:
        chat_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.caption(f"📝 {chat_count} conversation{'s' if chat_count != 1 else ''} in this session")
    else:
        st.caption("No conversations yet")
    
    st.markdown("---")
    
    # Info Panel
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
        Ask me anything about Parag Parikh mutual funds. I can help you find information about:
        - **Expense ratios**
        - **Exit loads**
        - **Minimum SIP amounts**
        - **Lock-in periods**
        - **Riskometers**
        - **Benchmarks**
        - **Returns**
        """)
    
    st.markdown("---")
    
    # Disclaimer
    st.markdown("""
    <div style="font-size: 11px; color: #888; line-height: 1.5;">
        <strong>Disclaimer:</strong> This assistant provides factual information only for Parag Parikh Mutual Funds. It does not support other AMCs and does not provide investment advice.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    
    # New Chat Button (prominent, at bottom)
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
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

