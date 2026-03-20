import streamlit as st
import fitz  # PyMuPDF
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pathlib import Path


# Load variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def extract_text_from_pdf(uploaded_file):
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def analyze_with_gemini(resume_text, job_desc):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0
    )

    template = """
    You are an AI Resume Analyzer. Compare the Resume against the Job Description (JD).
    Return ONLY a valid JSON object with these keys: 
    "match_score", "matched_skills", "missing_skills", and "summary".

    RESUME:
    {resume_content}

    JD:
    {job_content}
    """

    prompt = PromptTemplate(input_variables=["resume_content", "job_content"], template=template)
    chain = prompt | llm

    response = chain.invoke({"resume_content": resume_text, "job_content": job_desc})

    # Clean string if Gemini adds markdown backticks
    clean_content = response.content.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_content)


# --- Streamlit UI ---
st.set_page_config(page_title="Gemini Resume AI", layout="wide")
st.title("♊ Gemini-Powered Resume Analyzer")

# UI Layout
col1, col2 = st.columns(2)
with col1:
    job_desc = st.text_area("Job Requirements", height=250, placeholder="Paste JD here...")
with col2:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if st.button("Analyze Resume"):
    if not GEMINI_API_KEY:
        st.error("API Key not found in .env file!")
    elif not job_desc or not uploaded_file:
        st.warning("Please provide both the Job Description and a Resume PDF.")
    else:
        with st.spinner("Gemini is analyzing..."):
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
                result = analyze_with_gemini(resume_text, job_desc)

                # Results Section
                st.divider()
                st.metric("Match Score", f"{result['match_score']}%")
                st.progress(result['match_score'] / 100)

                c1, c2 = st.columns(2)
                with c1:
                    st.success("### ✅ Matched Skills")
                    st.write(", ".join(result['matched_skills']))
                with c2:
                    st.error("### ❌ Missing Skills")
                    st.write(", ".join(result['missing_skills']))

                st.info(f"**💡 Recruiter Feedback:** {result['summary']}")

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
