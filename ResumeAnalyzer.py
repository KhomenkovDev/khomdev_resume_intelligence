import streamlit as st
import fitz  # PyMuPDF
import json
import os
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pathlib import Path

# --- Configuration & Styling ---
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

# Serious Minimalistic Design CSS
st.markdown("""
<style>
    /* Global Font & Spacing Constraints */
    html, body, [class*="css"]  {
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Clean headers */
    h1, h2, h3 {
        font-weight: 600 !important;
        color: #1E1E1E;
    }
    
    /* Dark mode override for text elements if system is dark */
    @media (prefers-color-scheme: dark) {
        h1, h2, h3, p, span {
            color: #E0E0E0 !important;
        }
    }

    /* Minimalist metric cards */
    div[data-testid="metric-container"] {
        background-color: transparent;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: none;
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] {
            border-color: #333333;
        }
    }
    
    /* Hide default streamlit marks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- API Key Management (Live + Local) ---
# Check Streamlit secrets first (for cloud deployment), fallback to .env (for local)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")

GEMINI_API_KEY = get_api_key()

# --- Helper Functions ---
def extract_text_from_pdf(uploaded_file):
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def analyze_with_gemini(resume_text, job_desc, api_key):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    template = """
    You are an expert ATS (Applicant Tracking System) and professional Technical Recruiter. 
    Analyze the provided Resume against the Job Description (JD).
    
    Return ONLY a valid JSON object. Do not include markdown blocks like ```json ... ```, just the raw JSON object.
    Ensure the JSON schema strictly follows the structure below:
    {{
        "match_score": <int between 0 and 100 representing the exact match percentage>,
        "matched_skills": [<array of explicit skills found in both>],
        "missing_skills": [<array of critical skills in JD but missing in Resume>],
        "ats_keywords": [<array of important keywords for this specific role>],
        "candidate_summary": "<A brief, professional 2-3 sentence summary of the candidate's fit>",
        "improvement_tips": [<array of 3-5 highly actionable pieces of advice to improve the resume for this JD>]
    }}

    RESUME:
    {resume_content}

    JD:
    {job_content}
    """

    prompt = PromptTemplate(input_variables=["resume_content", "job_content"], template=template)
    chain = prompt | llm

    try:
        response = chain.invoke({"resume_content": resume_text, "job_content": job_desc})
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        # Handle potential edge cases where LLM includes prefix text
        start_idx = clean_content.find('{')
        end_idx = clean_content.rfind('}') + 1
        return json.loads(clean_content[start_idx:end_idx])
    except json.JSONDecodeError:
        raise Exception("Failed to parse the Gemini response into JSON. The LLM output was formatted incorrectly.")
    except Exception as e:
        raise Exception(f"Analysis Error: {str(e)}")

def create_score_chart(score):
    # Minimalistic donut chart using Altair
    source = pd.DataFrame({
        "Category": ["Match", "Gap"],
        "Value": [score, 100 - score],
        "Color": ["#2E7D32", "#E0E0E0"] if score >= 70 else (["#F57C00", "#E0E0E0"] if score >= 40 else ["#D32F2F", "#E0E0E0"])
    })
    
    chart = alt.Chart(source).mark_arc(innerRadius=50, cornerRadius=2).encode(
        theta=alt.Theta(field="Value", type="quantitative"),
        color=alt.Color(field="Color", type="nominal", scale=None),
        tooltip=["Category", "Value"]
    ).properties(
        width=150,
        height=150
    ).configure_view(strokeWidth=0)
    
    return chart

def generate_markdown_report(result, job_desc):
    report = f"""# Resume Analysis Report

## Score: {result.get('match_score', 0)} / 100

### Candidate Summary
{result.get('candidate_summary', 'N/A')}

---

### Analysis

**✅ Matched Skills**
{', '.join(result.get('matched_skills', [])) if result.get('matched_skills') else 'None found.'}

**❌ Missing Skills**
{', '.join(result.get('missing_skills', [])) if result.get('missing_skills') else 'None found.'}

**🔑 Target ATS Keywords**
{', '.join(result.get('ats_keywords', [])) if result.get('ats_keywords') else 'None identified.'}

---

### Actionable Improvement Tips
"""
    for tip in result.get('improvement_tips', []):
        report += f"- {tip}\\n"
        
    return report

# --- UI Layout ---

# Sidebar
with st.sidebar:
    st.title("AI Resume Analyzer")
    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Paste the target Job Description.
    2. Upload your Resume (PDF format).
    3. Run the analysis.
    """)
    st.markdown("---")
    st.markdown("### Settings")
    ui_api_key = st.text_input("Gemini API Key (Optional)", type="password", help="Overrides system keys. Get yours from Google AI Studio")
    
    st.markdown("---")
    st.caption("Designed with a serious minimalist aesthetic.")

# Main Body
st.title("Resume Fit Analysis")
st.markdown("Evaluate candidate profiles against job requirements using advanced Language Models.")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### Job Description")
    job_desc = st.text_area("Paste the job requirements here", height=250, label_visibility="collapsed", placeholder="E.g., We are looking for a Software Engineer with 3+ years of Python experience...")

with col2:
    st.markdown("#### Candidate Resume")
    uploaded_file = st.file_uploader("Upload PDF document", type=["pdf"], label_visibility="collapsed")


# Execution
active_api_key = ui_api_key if ui_api_key else GEMINI_API_KEY

analyze_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

if analyze_clicked:
    if not active_api_key:
        st.error("Authentication Error: Gemini API Key is missing. Please provide it in the sidebar or via secrets/.env.")
    elif not job_desc or not uploaded_file:
        st.warning("Input Error: Please provide both a Job Description and a Resume PDF.")
    else:
        with st.spinner("Executing analysis..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text:
                st.error("Failed to extract text from the provided PDF.")
            else:
                try:
                    result = analyze_with_gemini(resume_text, job_desc, active_api_key)
                    
                    st.markdown("---")
                    st.markdown("### Analysis Results")
                    
                    # Score Card
                    score_col, summary_col = st.columns([1, 3])
                    
                    with score_col:
                        score = result.get('match_score', 0)
                        st.metric("Overall Match", f"{score}%")
                        st.altair_chart(create_score_chart(score), use_container_width=True)
                        
                    with summary_col:
                        st.markdown("#### Executive Summary")
                        st.write(result.get('candidate_summary', 'No summary provided.'))
                        
                        # Download Button
                        report_md = generate_markdown_report(result, job_desc)
                        st.download_button(
                            label="Download Report (Markdown)",
                            data=report_md,
                            file_name="resume_analysis_report.md",
                            mime="text/markdown"
                        )
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Detailed Metrics Tabs
                    tab1, tab2, tab3 = st.tabs(["Skills Match", "ATS Optimization", "Improvement Tips"])
                    
                    with tab1:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("##### Present in Resume")
                            for skill in result.get('matched_skills', []):
                                st.markdown(f"- ✅ {skill}")
                        with c2:
                            st.markdown("##### Missing from Resume")
                            for skill in result.get('missing_skills', []):
                                st.markdown(f"- ❌ {skill}")
                                
                    with tab2:
                        st.markdown("##### Recommended Keywords")
                        st.write("Ensure these keywords appear naturally in your resume to pass automated screens:")
                        keywords = result.get('ats_keywords', [])
                        tags_html = ""
                        for kw in keywords:
                            tags_html += f'<span style="display:inline-block; padding: 4px 8px; margin: 4px; background-color: rgba(200, 200, 200, 0.2); border-radius: 4px; border: 1px solid rgba(150, 150, 150, 0.3); font-size: 0.9em;">{kw}</span>'
                        st.markdown(tags_html, unsafe_allow_html=True)
                    
                    with tab3:
                        st.markdown("##### Actionable Recommendations")
                        for tip in result.get('improvement_tips', []):
                            st.info(tip, icon="💡")
                            
                except Exception as e:
                    st.error(f"Execution Failed: {str(e)}")
