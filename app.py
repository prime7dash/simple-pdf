import streamlit as st
import urllib.request
import json
import os
import pypdf  # Clean text extraction

st.set_page_config(page_title="Anshuman's PDF Summarizer", page_icon="📄", layout="centered")
st.title("📄 Anshuman's Simple PDF Summarizer")
st.caption("Created by Anshuman Dash")
st.write("Upload a PDF to get an AI summary instantly.")

# Fetching the Gemini Key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🔑 Gemini API Key missing! Please configure 'GEMINI_API_KEY' in your Streamlit Cloud Secrets dashboard.")
    st.stop()

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Reading and extracting text from PDF..."):
        try:
            reader = pypdf.PdfReader(uploaded_file)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        except Exception as e:
            st.error(f"Could not read this PDF: {e}")
            st.stop()
        
        if len(extracted_text.strip()) < 20:
            st.error("⚠️ This PDF seems to be an image or scanned document. The text extractor couldn't read it. Please try a text-based PDF.")
            st.stop()

    with st.spinner("Gemini is analyzing and summarizing..."):
        try:
            # Google AI Studio Gemini API Endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Formatted exactly how Gemini expects its payload
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"You are an expert summarizer. Analyze the provided text and write a highly accurate, structured summary. Use bold headings and clean bullet points to organize the key takeaways.\n\nText to summarize:\n{extracted_text[:60000]}"
                    }]
                }]
            }
            
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                # Extracting the output text from Gemini's response structure
                summary = res_data['candidates'][0]['content']['parts'][0]['text']
                
            st.success("Summary Generated Successfully!")
            st.write("### Summary:")
            st.markdown(summary)

            st.download_button(
                label="Download Summary as Text File",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"An error occurred during summarization: {e}")
