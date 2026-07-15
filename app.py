import streamlit as st
from groq import Groq

st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")

st.title("🤖 AI Chatbot (Groq)")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.7,
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"❌ Error: {e}"

   
