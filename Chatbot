import streamlit as st
from google import genai

st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Gemini Chatbot")

# ---- API key setup ----
# On Streamlit Cloud: add GEMINI_API_KEY in Settings > Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("No Gemini API key found. Add GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL = "gemini-2.5-flash"

# ---- Chat history ----
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model=MODEL)

# ---- Display past messages ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Handle new input ----
prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")
        try:
            response = st.session_state.chat.send_message(prompt)
            reply = response.text
        except Exception as e:
            reply = f"⚠️ Error: {e}"
        placeholder.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
