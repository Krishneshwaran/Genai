import streamlit as st
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to generate answer using Gemini API
def generate_gemini_answer(pdf_text, question):
    prompt = f"""
    You are an expert in summarizing and answering questions from provided documents.
    Below is a text extracted from a PDF. Use the text to answer the question provided.

    PDF Text:
    {pdf_text}

    Question: {question}
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Streamlit app
st.title("Ask Questions from PDF")

# Upload PDF
uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf is not None:
    # Extract text from the PDF
    with st.spinner("Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_pdf)

    # Display PDF content (optional, can be removed if the content is large)
    st.subheader("Extracted Text from PDF:")
    st.write(pdf_text[:1500] + "..." if len(pdf_text) > 1500 else pdf_text)  # Limiting the display to the first 1500 characters

    # Ask a question
    question = st.text_input("Ask a question based on the PDF:")

    # Generate the answer when a question is provided
    if question:
        with st.spinner("Generating answer..."):
            answer = generate_gemini_answer(pdf_text, question)
        
        st.subheader("Answer:")
        st.write(answer)
