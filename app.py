import streamlit as st
import urllib.request
import json
import base64

st.set_page_config(page_title="Anshuman's Gemini PDF AI", page_icon="💬", layout="centered")
st.title("💬 Anshuman's PDF Chat & Summary AI")
st.caption("Created by Anshuman Dash")
st.write("Upload a PDF to get an instant summary and start chatting. **No installation required!**")

# Fetching the Gemini Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🔑 Gemini API Key missing! Please configure 'GEMINI_API_KEY' in your Streamlit Cloud Secrets dashboard.")
    st.stop()

# Initialize session states to remember summary and chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "current_file" not in st.session_state:
    st.session_state.current_file = None

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

# If a different PDF is uploaded, reset the state
if uploaded_file is not None:
    if st.session_state.current_file != uploaded_file.name:
        st.session_state.current_file = uploaded_file.name
        st.session_state.summary = ""
        st.session_state.chat_history = []

    # Read PDF bytes and convert to base64 encoding natively
    file_bytes = uploaded_file.read()
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    
    # Step 1: Generate Summary automatically if it doesn't exist
    if not st.session_state.summary:
        with st.spinner("Gemini is reading your PDF and writing a summary..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                
                data = {
                    "contents": [{
                        "parts": [
                            {"text": "Analyze this entire PDF document and generate a highly accurate, beautiful, and structured summary. Use bold headings and clean bullet points to organize the key takeaways."},
                            {
                                "inlineData": {
                                    "mimeType": "application/pdf",
                                    "data": base64_pdf
                                }
                            }
                        ]
                    }]
                }
                
                req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    st.session_state.summary = res_data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                st.error(f"Error generating summary: {e}")
                st.stop()

    # Step 2: Render Summary and Chat Window
    if st.session_state.summary:
        st.success("PDF analyzed successfully!")
        with st.expander("📄 View PDF Summary", expanded=True):
            st.markdown(st.session_state.summary)
            
        st.write("---")
        st.write("### 💬 Ask Questions About the PDF")
        
        # Display chat history on screen
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Accept user question input
        if user_query := st.chat_input("Ask something about the PDF..."):
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    try:
                        # Build context including past conversation history
                        history_context = ""
                        for chat in st.session_state.chat_history[:-1]:
                            history_context += f"{chat['role'].capitalize()}: {chat['content']}\n"
                        
                        prompt = (
                            f"You are a helpful AI assistant. Answer the user's question accurately based on the attached PDF document.\n"
                            f"Here is the conversation history so far:\n{history_context}\n"
                            f"User's new question: {user_query}"
                        )
                        
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                        headers = {"Content-Type": "application/json"}
                        
                        data = {
                            "contents": [{
                                "parts": [
                                    {"text": prompt},
                                    {
                                        "inlineData": {
                                            "mimeType": "application/pdf",
                                            "data": base64_pdf
                                        }
                                    }
                                ]
                            }]
                        }
                        
                        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
                        with urllib.request.urlopen(req) as response:
                            res_data = json.loads(response.read().decode('utf-8'))
                            ai_response = res_data['candidates'][0]['content']['parts'][0]['text']
                            
                        message_placeholder.markdown(ai_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    except Exception as e:
                        st.error(f"Error generating answer: {e}")
