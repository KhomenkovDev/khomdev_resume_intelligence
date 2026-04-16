# KhomDev Resume Intelligence

<div align="center">
  <img src="icon.png" width="150" alt="KhomDev Resume Intelligence Icon" />
</div>
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=google&logoColor=white)

An enterprise-grade, minimalist web application that leverages Google's **Gemini 2.5 Flash** model to analyze and score candidate resumes against specific job descriptions. 

This tool is designed for both job seekers looking to optimize their resumes for Applicant Tracking Systems (ATS), and recruiters needing a quick, unbiased summary of candidate fit.

## ✨ Features

- **High-Accuracy Matching**: Calculates a precise match score (0-100%) based on semantic skill alignment.
- **ATS Keyword Extraction**: Identifies exact keywords from the Job Description that need to be naturally incorporated into the resume.
- **Actionable Insights**: Generates 3-5 concrete, actionable tips mathematically tailored to improve the resume for the specific role.
- **Serious Minimalist Design**: A clean, distraction-free UI built with custom CSS and Streamlit.
- **Robust Parsing**: Extracts text cleanly from standard PDF documents using PyMuPDF.
- **Downloadable Reports**: One-click download of the markdown analysis report for record-keeping.

## 🚀 Live Demo

*(Placeholder: Link to your deployed Streamlit Community Cloud app here)*

## 🛠️ Technology Stack

- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **LLM Engine**: Google [Gemini-2.5-Flash](https://deepmind.google/technologies/gemini/) via integration with LangChain.
- **PDF Processing**: [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) (`fitz`)
- **Data Visualization**: [Altair](https://altair-viz.github.io/) / Pandas

## 💻 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KhomenkovDev/khomdev_resume_intelligence.git
   cd AIResumeanalyzer
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your Google Gemini API Key:
   ```env
   GEMINI_API_KEY="your_actual_api_key_here"
   ```
   *Note: If deploying on Streamlit Cloud, add this key to your Streamlit App Secrets instead of committing a `.env` file.*

5. **Run the application:**
   ```bash
   streamlit run ResumeAnalyzer.py
   ```

## 📸 Screenshots

![Screenshot 1](screenshots/Screenshot%202026-04-16%20at%2020.37.55.png)
![Screenshot 2](screenshots/Screenshot%202026-04-16%20at%2020.38.26.png)

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License
This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
