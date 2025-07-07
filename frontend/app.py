import streamlit as st
import requests
import json
import os

st.set_page_config(
    page_title="HR SmartHire AI Agents",
    page_icon="📄",
    layout="centered"
)

st.title("📄 HR SmartHire AI Agents")
st.markdown("Upload a resume PDF and provide a job description to get an ATS score, resume summary, and an automated email decision.")


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000") 


uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_description = st.text_area("Job Description", height=200, placeholder="Paste the full job description here...")


if st.button("Process Application"):
    if uploaded_file is None:
        st.error("Please upload a resume PDF.")
    elif not job_description.strip():
        st.error("Please provide a job description.")
    else:
        with st.spinner("Processing resume... This may take a moment (extracting text, scoring, summarizing, and deciding)..."):
            try:
                files = {"resume_file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"job_description": job_description}

                response = requests.post(f"{BACKEND_URL}/process_resume/", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Processing Complete!")

                    st.subheader("Application Results:")
                    
                    ats_score = result.get('ats_score', 'N/A')
                    st.metric(label="ATS Score (0-100)", value=f"{ats_score:.2f}" if isinstance(ats_score, float) else ats_score)

                    st.write(f"**Applicant Email:** {result.get('email', 'Not found')}")

                    st.subheader("Resume Summary:")
                    summary = result.get('resume_summary')
                    if summary:
                        st.markdown(summary)
                    else:
                        st.write("No summary available.")

                    st.subheader("Automated Decision:")
                    decision_status = ""
                    if result.get('email_sent'):
                        decision_status = "Accepted (Email Sent)" if result.get('ats_score', 0) >= 75 else "Rejected (Email Sent)"
                        st.success(decision_status)
                    elif result.get('ats_score', 0) >= 60 and result.get('ats_score', 0) < 75 :
                        decision_status = "Human Review Recommended"
                        st.warning(decision_status)
                        st.info("This candidate's score falls in a range that suggests manual review is beneficial.")
                    elif result.get('ats_score', 0) < 60:
                        decision_status = "Rejected (No Email Sent due to issue)" if result.get('email_error') else "Rejected (Email decision)"
                        st.error(decision_status)
                    else:
                        decision_status = "Unknown Decision"
                        st.info(decision_status)


                    if result.get('extraction_error') or result.get('scoring_error') or result.get('email_error'):
                        st.error("Errors occurred during processing:")
                        if result.get('extraction_error'):
                            st.write(f"- **PDF Extraction Error:** {result.get('error_message', 'Unknown')}")
                        if result.get('scoring_error'):
                            st.write(f"- **ATS Scoring Error:** {result.get('error_message', 'Unknown')}")
                        if result.get('email_error'):
                            st.write(f"- **Email Sending Error:** {result.get('error_message', 'Unknown')}")
                        elif result.get('error_message') and not (result.get('extraction_error') or result.get('scoring_error') or result.get('email_error')):
                             st.write(f"- **General Processing Error:** {result.get('error_message')}")
                        st.info("Check backend logs for more details.")

                    st.subheader("Full Processing Details (for debugging):")
                    st.json(result)

                else:
                    st.error(f"Error from backend: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Could not connect to backend at {BACKEND_URL}. Please ensure the FastAPI backend is running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.sidebar.header("About")
st.sidebar.info(
    "This application uses LangGraph for orchestrating the HR workflow, "
    "FastAPI for the backend API, and Streamlit for the interactive UI. "
    "It leverages LLMs for resume summarization and SentenceTransformers for ATS scoring."
)
st.sidebar.markdown("---")
st.sidebar.markdown("Developed by Your Name/Organization")