import uuid
import asyncio
import streamlit as st
from audio_recorder_streamlit import audio_recorder

from agent import DatasmithAgent
from voice_chat import VoiceChat
from config import get_settings


if "agent" not in st.session_state:
    st.session_state.agent = DatasmithAgent()
    st.session_state.settings = get_settings()
    try:
        st.session_state.voice = VoiceChat()
        st.session_state.voice_enabled = True
    except:
        st.session_state.voice_enabled = False


st.set_page_config(page_title="Datasmith AI", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .stApp { max-width: 900px; margin: 0 auto; }
    .header-text {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.3rem;
    }
    .stats-bar {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-around;
        font-size: 0.85rem;
    }
    .stat-item { text-align: center; }
    .stat-value { font-weight: 700; color: #667eea; font-size: 1.1rem; }
    .stat-label { color: #888; font-size: 0.75rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None


def format_stats(stats: dict) -> str:
    return f"📊 {stats.get('total_tokens', 0):,} tok | ⚡ {stats.get('tokens_per_sec', 0):.0f} tok/s | ⏱️ {stats.get('total_time_sec', 0):.1f}s | 💰 ${stats.get('estimated_cost_usd', 0):.4f}"


async def transcribe_audio(audio_bytes: bytes) -> str:
    if st.session_state.voice_enabled:
        try:
            return await st.session_state.voice.transcribe(audio_bytes)
        except Exception as e:
            return f"[Transcription error: {e}]"
    return "[Voice not available]"


def main():
    init_session()
    
    st.markdown('<div class="header-container"><div class="header-text">🤖 Datasmith AI</div></div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Summarize • Explain • Analyze • Chat</p>", unsafe_allow_html=True)
    
    stats = st.session_state.agent.get_stats()
    st.markdown(f'''
        <div class="stats-bar">
            <div class="stat-item"><div class="stat-value">{stats['total_tokens']:,}</div><div class="stat-label">Tokens</div></div>
            <div class="stat-item"><div class="stat-value">{stats['tokens_per_sec']:.0f}</div><div class="stat-label">Tok/sec</div></div>
            <div class="stat-item"><div class="stat-value">{stats['total_time_sec']:.1f}s</div><div class="stat-label">Time</div></div>
            <div class="stat-item"><div class="stat-value">${stats['estimated_cost_usd']:.4f}</div><div class="stat-label">Cost</div></div>
        </div>
    ''', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Options")
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.processed_files = set()
            st.session_state.agent.reset_stats()
            st.rerun()
        st.divider()
        st.markdown("**📎 Supports:** PDF, Images, Audio, YouTube URLs\n\n**💡 Try:** 'Summarize this', 'Explain the code'")
        if st.session_state.voice_enabled:
            st.success("🎤 Voice enabled")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
                if msg.get("filename"): st.caption(f"📎 {msg['filename']}")
                if msg.get("is_voice"): st.caption("🎤 Voice")
        else:
            with st.chat_message("assistant", avatar="❓" if msg.get("is_clarify") else "🤖"):
                st.markdown(msg["content"])
                if msg.get("stats"): st.caption(format_stats(msg["stats"]))

    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.chat_input("Type a message or paste a YouTube URL...")
    with col2:
        audio_bytes = audio_recorder(text="", recording_color="#667eea", neutral_color="#e0e0e0", icon_size="2x", pause_threshold=2.0) if st.session_state.voice_enabled else None
    with col3:
        if st.button("📎", help="Attach file"):
            st.session_state.show_upload = True

    if st.session_state.get("show_upload", False):
        with st.expander("📎 Upload File", expanded=True):
            uploaded_file = st.file_uploader("Choose file", type=["pdf", "png", "jpg", "jpeg", "mp3", "wav", "txt"], label_visibility="collapsed")
            c1, c2 = st.columns(2)
            with c1:
                if uploaded_file and st.button("📤 Send", type="primary", use_container_width=True):
                    fk = f"{uploaded_file.name}_{uploaded_file.size}"
                    if fk not in st.session_state.processed_files:
                        st.session_state.pending_file = {"content": uploaded_file.getvalue(), "name": uploaded_file.name}
                        st.session_state.processed_files.add(fk)
                        st.session_state.show_upload = False
                        st.rerun()
            with c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_upload = False
                    st.rerun()

    should_process, file_content, filename, is_voice = False, None, None, False

    if st.session_state.get("pending_file"):
        file_content = st.session_state.pending_file["content"]
        filename = st.session_state.pending_file["name"]
        st.session_state.pending_file = None
        should_process = True

    if audio_bytes and audio_bytes != st.session_state.last_audio:
        st.session_state.last_audio = audio_bytes
        with st.spinner("🎤 Transcribing..."):
            user_input = asyncio.run(transcribe_audio(audio_bytes))
            is_voice = True
            should_process = True

    if user_input and not is_voice:
        should_process = True

    if should_process and (user_input or file_content):
        display_text = user_input or f"📄 {filename}"
        st.session_state.messages.append({"role": "user", "content": display_text, "filename": filename, "is_voice": is_voice})
        
        with st.chat_message("user"):
            st.markdown(display_text)
            if filename: st.caption(f"📎 {filename}")
            if is_voice: st.caption("🎤 Voice")
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                result = asyncio.run(st.session_state.agent.process(session_id=st.session_state.session_id, message=user_input, file_content=file_content, filename=filename))
            st.markdown(result["response"])
            st.caption(format_stats(result.get("stats", {})))
        
        st.session_state.messages.append({"role": "assistant", "content": result["response"], "is_clarify": result["requires_clarification"], "stats": result.get("stats", {})})
        st.rerun()


if __name__ == "__main__":
    main()
