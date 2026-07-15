import streamlit as st
from groq import Groq

st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")

st.title("🤖 AI Chatbot (Groq Debug)")

try:
    api_key = st.secrets["GROQ_API_KEY"]
    st.success("✅ API key found")
except Exception as e:
    st.error(f"❌ Secret Error: {e}")
    st.stop()

try:
    client = Groq(api_key=api_key)
    st.success("✅ Groq client created")
except Exception as e:
    st.error(f"❌ Client Error: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"❌ API Error:\n\n{str(e)}"

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
