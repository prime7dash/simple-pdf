import streamlit as st
import urllib.request
import json

st.set_page_config(page_title="PDF Summarizer", page_icon="📄", layout="centered")
st.title("📄 Simple PDF Summarizer")
st.write("Upload a PDF to get an AI summary instantly.")

api_key = st.sidebar.text_input("Enter OpenAI Key", type="password")

if not api_key:
    st.info("Please enter your OpenAI API key in the left sidebar to start.")
    st.stop()

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Reading the file..."):
        # Read the raw file bytes
        pdf_bytes = uploaded_file.read()
        
        # Pull text using basic string decoding (skips external library errors)
        extracted_text = ""
        for line in pdf_bytes.split(b'\n'):
            if b'BT' in line or b'ET' in line: # Basic PDF text stream filtering
                try:
                    extracted_text += line.decode('utf-8', errors='ignore') + "\n"
                except:
                    pass
        
        # Fallback to general file text if parsing fails
        if len(extracted_text.strip()) < 50:
            extracted_text = pdf_bytes.decode('utf-8', errors='ignore')[:50000]

    with st.spinner("AI is thinking..."):
        try:
            # Native API request using built-in urllib (No openai library required)
            url = "https://openai.com"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
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
