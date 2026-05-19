import streamlit as st
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="YouTube AI Chat", layout="centered")

# -------------------------
# CUSTOM CSS (MODERN CHAT UI)
# -------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

/* Title */
.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: 700;
    background: linear-gradient(90deg,#60a5fa,#a78bfa,#34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Chat bubbles */
.user-msg {
    background: #2563eb;
    padding: 12px;
    border-radius: 15px;
    margin: 8px 0;
    text-align: right;
    color: white;
}

.bot-msg {
    background: #1f2937;
    padding: 12px;
    border-radius: 15px;
    margin: 8px 0;
    color: #e5e7eb;
}

/* Card */
.card {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Input box style */
.stTextInput > div > div > input {
    background-color: #0b1220;
    color: white;
    border-radius: 10px;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg,#3b82f6,#8b5cf6);
    color: white;
    border-radius: 10px;
    border: none;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
if "video_id" not in st.session_state:
    st.session_state.video_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = None

if "last_question" not in st.session_state:
    st.session_state.last_question = None


# -------------------------
# HEADER
# -------------------------
st.markdown("<div class='main-title'>🎬 AI YouTube Chat</div>", unsafe_allow_html=True)
st.caption("Chat with any YouTube video using AI")

# -------------------------
# STEP 1 - VIDEO INPUT
# -------------------------
st.markdown("### 📌 Add YouTube Video")

youtube_url = st.text_input("Paste YouTube URL")

if st.button("🚀 Process Video"):
    if youtube_url:

        with st.spinner("🧠 AI is watching the video..."):
            time.sleep(1)

            res = requests.post(
                f"{BASE_URL}/process-video",
                json={"youtube_url": youtube_url}
            )

        if res.status_code == 200:
            st.session_state.video_id = res.json()["video_id"]
            st.success("Video processed successfully!")
        else:
            st.error("Failed to process video")


# -------------------------
# STEP 2 - SUMMARY (CARD STYLE)
# -------------------------
if st.session_state.video_id and not st.session_state.summary:

    with st.spinner("🧾 Generating smart summary..."):
        res = requests.post(
            f"{BASE_URL}/summary",
            json={"video_id": st.session_state.video_id}
        )

    if res.status_code == 200:
        st.session_state.summary = res.json()["response"]


if st.session_state.summary:
    with st.expander("📌 View Video Summary", expanded=True):
        st.markdown(f"<div class='card'>{st.session_state.summary}</div>", unsafe_allow_html=True)


# -------------------------
# STEP 3 - CHAT AREA
# -------------------------
if st.session_state.summary:

    st.markdown("### 💬 Chat with Video AI")

    chat_container = st.container()

    with chat_container:

        for msg in st.session_state.messages:

            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-msg'>🤖 {msg['content']}</div>", unsafe_allow_html=True)


    # input box
    user_input = st.text_input("Ask anything about the video...", key="input")

    col1, col2 = st.columns([1, 1])

    ask_clicked = col1.button("Send 💬")
    regen_clicked = col2.button("🔄 Regenerate")

    # -------------------------
    # ASK
    # -------------------------
    if ask_clicked and user_input:

        st.session_state.last_question = user_input
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("🤖 Thinking..."):
            res = requests.post(
                f"{BASE_URL}/ask",
                json={
                    "video_id": st.session_state.video_id,
                    "question": user_input
                }
            )

        if res.status_code == 200:
            answer = res.json()["response"]
            st.session_state.messages.append({"role": "assistant", "content": answer})

        st.rerun()

    # -------------------------
    # REGENERATE
    # -------------------------
    if regen_clicked and st.session_state.last_question:

        with st.spinner("♻️ Regenerating answer..."):
            res = requests.post(
                f"{BASE_URL}/ask",
                json={
                    "video_id": st.session_state.video_id,
                    "question": st.session_state.last_question
                }
            )

        if res.status_code == 200:
            new_answer = res.json()["response"]

            for i in range(len(st.session_state.messages)-1, -1, -1):
                if st.session_state.messages[i]["role"] == "assistant":
                    st.session_state.messages[i]["content"] = new_answer
                    break

        st.rerun()