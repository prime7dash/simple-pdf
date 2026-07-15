import time
import tempfile
import os

import streamlit as st
from google import genai

st.set_page_config(page_title="PDF Summarizer", page_icon="📄", layout="centered")
st.title("📄 PDF Summarizer")
st.caption("Upload a PDF and get an AI-generated summary powered by Gemini.")

# ---- API key setup ----
# On Streamlit Cloud: add GEMINI_API_KEY in Settings > Secrets
# Locally: create .streamlit/secrets.toml with GEMINI_API_KEY = "your-key"
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("No Gemini API key found. Add GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL = "gemini-2.5-flash"

# ---- Sidebar options ----
st.sidebar.header("Options")
summary_style = st.sidebar.selectbox(
    "Summary style",
    ["Concise (bullet points)", "Detailed (paragraphs)", "Executive summary"],
)
custom_instructions = st.sidebar.text_area(
    "Extra instructions (optional)",
    placeholder="e.g. Focus on financial figures, ignore appendix...",
)

style_prompts = {
    "Concise (bullet points)": "Summarize the document as clear, concise bullet points covering the key ideas.",
    "Detailed (paragraphs)": "Write a detailed summary in well-organized paragraphs covering the main sections.",
    "Executive summary": "Write a short executive summary (under 200 words) highlighting only the most important takeaways.",
}

# ---- File upload ----
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    st.info(f"**{uploaded_file.name}** ready ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("Summarize", type="primary"):
        with st.spinner("Uploading PDF and generating summary..."):
            tmp_path = None
            try:
                # Save to a temp file since the Gemini SDK uploads by file path
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                # Upload the PDF to Gemini's file storage
                gemini_file = client.files.upload(file=tmp_path)

                # Wait until the file finishes processing
                while gemini_file.state == "PROCESSING":
                    time.sleep(1)
                    gemini_file = client.files.get(name=gemini_file.name)

                if gemini_file.state == "FAILED":
                    st.error("PDF processing failed. Try a different file.")
                    st.stop()

                prompt = style_prompts[summary_style]
                if custom_instructions.strip():
                    prompt += f"\n\nAdditional instructions: {custom_instructions.strip()}"

                response = client.models.generate_content(
                    model=MODEL,
                    contents=[gemini_file, prompt],
                )

                st.subheader("Summary")
                st.markdown(response.text)

                st.download_button(
                    "Download summary as .txt",
                    data=response.text,
                    file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_summary.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
else:
    st.info("Upload a PDF file to get started.")
