import streamlit as st
import urllib.request
import json
import os

st.set_page_config(page_title="Anshuman's PDF Summarizer", page_icon="📄", layout="centered")
st.title("📄 Anshuman's Simple PDF Summarizer")
st.caption("Created by Anshuman Dash")
st.write("Upload a PDF to get an AI summary instantly.")

# Fetching the Groq Key from Streamlit Secrets
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("🔑 Groq API Key missing! Please configure 'GROQ_API_KEY' in your Streamlit Cloud Secrets dashboard.")
    st.stop()

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Reading the file..."):
        pdf_bytes = uploaded_file.read()
        extracted_text = ""
        for line in pdf_bytes.split(b'\n'):
            if b'BT' in line or b'ET' in line:
                try:
                    extracted_text += line.decode('utf-8', errors='ignore') + "\n"
                except:
                    pass
        
        if len(extracted_text.strip()) < 50:
            extracted_text = pdf_bytes.decode('utf-8', errors='ignore')[:50000]

    with st.spinner("AI is thinking..."):
        try:
            # Point to Groq's free API endpoint
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            # Added "User-Agent" to trick Cloudflare so we don't get blocked with a 403!
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            data = {
                "model": "llama-3.1-8b-instant", # Highly stable free model on Groq
                "messages": [
                    {"role": "system", "content": "You are an expert summarizer. Summarize this text into clear, structured bullet points with bold key headings."},
                    {"role": "user", "content": extracted_text[:40000]}
                ]
            }
            
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                summary = res_data['choices'][0]['message']['content']
                
            st.success("Done!")
            st.write("### Summary:")
            st.markdown(summary)

            st.download_button(
                label="Download Summary as Text File",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
