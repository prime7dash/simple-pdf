import streamlit as st
import pypdf
from openai import OpenAI

st.set_page_config(page_title="PDF Summarizer", page_icon="📄", layout="centered")
st.title("📄 Simple PDF Summarizer")
st.write("Upload a PDF to get an AI summary instantly.")

api_key = st.sidebar.text_input("Enter OpenAI Key", type="password")

if not api_key:
    st.info("Please enter your OpenAI API key in the left sidebar to start.")
    st.stop()

client = OpenAI(api_key=api_key)
uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Reading the file..."):
        pdf_reader = pypdf.PdfReader(uploaded_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

    if not extracted_text.strip():
        st.error("Could not read any text from this PDF.")
        st.stop()

    with st.spinner("AI is thinking..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert summarizer. Summarize this text into clear, structured bullet points with bold key headings."},
                    {"role": "user", "content": extracted_text}
                ]
            )
            summary = response.choices.message.content
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
