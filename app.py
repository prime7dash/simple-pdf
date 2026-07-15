import streamlit as st
import urllib.request
import json
import os
import pypdf

st.set_page_config(page_title="Anshuman's PDF Chatbot", page_icon="💬", layout="centered")
st.title("💬 Anshuman's PDF Chatbot")
st.caption("Created by Anshuman Dash")
st.write("Upload a PDF and ask the AI anything about it!")

# Fetching the Gemini Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🔑 Gemini API Key missing! Please configure 'GEMINI_API_KEY' in your Streamlit Cloud Secrets dashboard.")
    st.stop()

# Initialize chat history in session state so it remembers your conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

# If a new file is uploaded, extract its text
if uploaded_file is not None:
    with st.spinner("Reading and processing PDF..."):
        try:
            reader = pypdf.PdfReader(uploaded_file)
            text_content = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
            
            st.session_state.pdf_text = text_content
            st.success("PDF processed successfully! You can now start chatting below.")
        except Exception as e:
            st.error(f"Could not read this PDF: {e}")
            st.stop()

# Only show the chat interface if a PDF has been successfully processed
if st.session_state.pdf_text:
    st.write("---")
    st.write("### Chat History")
    
    # Display previous chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user chat input
    if user_query := st.chat_input("Ask a question about your PDF..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        # Generate response from Gemini
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                    headers = {"Content-Type": "application/json"}
                    
                    # Construct prompt with chat history context and the PDF document text
                    context_prompt = (
                        f"You are a helpful AI assistant. You are analyzing the following PDF document:\n"
                        f"--- START OF DOCUMENT ---\n{st.session_state.pdf_text[:60000]}\n--- END OF DOCUMENT ---\n\n"
                        f"Answer the user's question accurately based strictly on the document text provided above.\n"
                        f"User Question: {user_query}"
                    )
                    
                    data = {
                        "contents": [{
                            "parts": [{"text": context_prompt}]
                        }]
                    }
                    
                    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
                    with urllib.request.urlopen(req) as response:
                        res_data = json.loads(response.read().decode('utf-8'))
                        ai_response = res_data['candidates'][0]['content']['parts'][0]['text']
                    
                    message_placeholder.markdown(ai_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
