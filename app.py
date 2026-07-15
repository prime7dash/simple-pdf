import streamlit as st
from groq import Groq

# ---------------- Page Settings ----------------
st.set_page_config(
    page_title="Anshuman AI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Anshuman AI")
st.caption("Developed by Anshuman")

# ---------------- API Key ----------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception as e:
    st.error(f"❌ Secret Error: {e}")
    st.stop()

# ---------------- Groq Client ----------------
try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"❌ Client Error: {e}")
    st.stop()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("🤖 Anshuman AI")
    st.markdown("### 👨‍💻 Developer")
    st.write("**Anshuman**")
    st.markdown("---")
    st.write("Powered by Groq")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------- Chat History ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Chat Input ----------------
prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                )

                reply = response.choices[0].message.content

            except Exception as e:
                reply = f"❌ API Error:\n\n{str(e)}"

            st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
