import streamlit as st
import os
from google import genai
from google.genai import types

# --- Configuration ---
st.set_page_config(
    page_title="Community Insight Decision Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Premium Custom CSS ---
st.markdown(
    """
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply custom font */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Custom header design */
    .header-container {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.3);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.025em;
        color: white !important;
    }
    .header-subtitle {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 0.5rem;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Elegant slate-900 */
        border-right: 1px solid #1e293b;
    }
    
    /* Custom chat bubble accents and styling */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Style subheaders */
    h3 {
        font-weight: 600;
        color: #f8fafc;
    }
    
    /* Customize all buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2) !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
        background: linear-gradient(90deg, #5a52e6 0%, #8b4bf0 100%) !important;
    }
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API Key Validation ---
# Fetches securely from environment variables only (no UI input)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ **GEMINI_API_KEY environment variable is missing.** Please set it in your system environment or within your Google Cloud Run service environment configuration.")
    st.info("💡 To run locally, use: `export GEMINI_API_KEY='your-key'` or set it in PowerShell: `$env:GEMINI_API_KEY='your-key'`")
    st.stop()

# Initialize the official GenAI Client
@st.cache_resource
def get_genai_client(api_key: str):
    return genai.Client(api_key=api_key)

try:
    client = get_genai_client(api_key)
except Exception as e:
    st.error(f"Failed to initialize Google GenAI Client: {e}")
    st.stop()

# --- AI System Instruction ---
SYSTEM_INSTRUCTION = (
    "You are an AI Decision Intelligence Assistant for city management. "
    "Analyze the provided community data, identify patterns or anomalies, and suggest "
    "actionable, automated workflows to improve community well-being. "
    "Keep answers concise and strictly related to the provided data."
)

# --- Sidebar (Context & Settings) ---
with st.sidebar:
    st.markdown("### 🏙️ Context & Data")
    st.write("Provide geographic context and community reports for AI analysis.")
    
    district = st.selectbox(
        "Select City District",
        options=["District 1", "District 2", "District 3", "District 4", "District 5", "All Districts"],
        index=0
    )
    
    community_reports = st.text_area(
        "Recent Community Reports",
        height=280,
        placeholder="Paste citizen feedback/reports here (e.g. street light outages, trash collection delays, water pressure issues)..."
    )
    
    st.markdown("---")
    
    # Reset button for state management
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()

# --- Main App Header ---
st.markdown(
    """
    <div class="header-container">
        <h1 class="header-title">🏙️ Community Insight Decision Platform</h1>
        <p class="header-subtitle">Convert citizen feedback into structured, automated decision workflows and urban solutions.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Conversational State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Stateful Chat Session using the official SDK Chats API
if "chat" not in st.session_state:
    try:
        st.session_state.chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3
            )
        )
    except Exception as e:
        st.error(f"Failed to establish AI chat session: {e}")
        st.stop()

# Display current chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Interaction Flow ---
if prompt := st.chat_input("Ask a question about the community data..."):
    # Immediately render and save the user prompt
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Construct context-injected prompt invisibly for RAG integration
    context_injected_prompt = f"""
    Context Data:
    - City District: {district}
    - Recent Community Reports:
    {community_reports if community_reports.strip() else "No reports provided."}
    
    User Query:
    {prompt}
    """
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("Analyzing reports and synthesizing decision pathways..."):
                response = st.session_state.chat.send_message(context_injected_prompt)
            
            # Update UI with generated content
            message_placeholder.markdown(response.text)
            
            # Save assistant response to session history
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"An error occurred while calling the Gemini API: {e}")
