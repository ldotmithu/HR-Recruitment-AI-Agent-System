from langgraph.graph import StateGraph,END
from langgraph.prebuilt import ToolNode
from typing import TypedDict,Optional

from core.state import HRApplicationState
from core.tools import (
    extract_text_from_pdf,
    llm_ats_score,
    send_acceptance_email,
    send_rejection_email
)
from core.llm_chains import resume_summarizer

def extract_resume_node(state:HRApplicationState):
    """Extracts text and email from the PDF resume."""
    pdf_path =state["pdf_path"]
    extract_data = extract_text_from_pdf.invoke({"pdf_path":pdf_path})
    return {extract_data}

def ats_score_node(state:HRApplicationState):
    """ Computes the ATS compatibility score."""
    if state.get("extraction_error"):
        return {"scoring_error": True, "error_message": "Skipped ATS scoring due to extraction error."}
    
    resume_text = state.get("resume_text","")
    job_text = state.get("job_text","")
    
    if not resume_text and job_text:
        error_msg = "'resume_text' or 'job_text' is missing for ATS scoring."
        return {"ats_score": 0.0, "scoring_error": True, "error_message": error_msg}
    
    score_data = llm_ats_score.invoke({
        "resume_text":resume_text,
        "job_text":job_text
        })
    return {score_data}

def summarize_resume_node(state: HRApplicationState):
    """Summarizes the resume using an LLM."""
    if state.get("extraction_error") or state.get("scoring_error"):
        return {"resume_summary": None, "error_message": state.get("error_message")}
    
    if not resume_summarizer:
        error_msg = "LLM summarizer is not initialized. Skipping summarization."
        return {"resume_summary": None, "error_message": error_msg}


    resume_text = state.get("resume_text", "")
    job_text = state.get("job_text", "")

    if not resume_text or not job_text:
        error_msg = "'resume_text' or 'job_text' missing for summarization."
        return {"resume_summary": None, "error_message": error_msg}

    try:
        summary = resume_summarizer.invoke({
            "resume_text": resume_text,
            "job_text": job_text
        })
        return {"resume_summary": summary}
    except Exception as e:
        error_msg = f"Error summarizing resume: {e}"
        return {"resume_summary": None, "error_message": error_msg}
    
def send_rejection_node(state: HRApplicationState):
    """Sends a rejection email."""
    if state.get("email_error"): 
         print("Skipping rejection email due to prior email configuration error.")
         return {} 
    
    email = state.get("email")
    if not email:
        error_msg = "Skipping rejection email: No email address found."
        return {"email_error": True, "error_message": error_msg}

    email_sent_data = send_rejection_email.invoke({"email": email})
    return {email_sent_data}

def send_acceptance_node(state: HRApplicationState):
    """Sends an acceptance email."""
    print(f"--- Node: send_acceptance ---")

    if state.get("email_error"): 
         print("Skipping acceptance email due to prior email configuration error.")
         return {}
         
    email = state.get("email")
    if not email:
        error_msg = "Skipping acceptance email: No email address found."
        return {"email_error": True, "error_message": error_msg}

    email_sent_data = send_acceptance_email.invoke({"email": email})
    return {email_sent_data}

def human_review_node(state: HRApplicationState):
    """Logs details for human review."""
    print(f"--- Node: human_review ---")
    print("\n--- CANDIDATE FOR HUMAN REVIEW ---")
    print(f"Email: {state.get('email', 'N/A')}")
    print(f"ATS Score: {state.get('ats_score', 'N/A')}")
    print(f"Resume Summary:\n{state.get('resume_summary', 'No summary available.')}\n")
    print("----------------------------------")
    return {}

def handle_error_node(state: HRApplicationState):
    """Centralized error handling node."""
    print(f"--- Node: handle_error ---")
    print(f"\n--- WORKFLOW ERROR ENCOUNTERED ---")
    if state.get("extraction_error"):
        print(f"Extraction Error: {state.get('error_message', 'Unknown extraction error')}")
    if state.get("scoring_error"):
        print(f"Scoring Error: {state.get('error_message', 'Unknown scoring error')}")
    if state.get("email_error"):
        print(f"Email Error: {state.get('error_message', 'Unknown email error')}")
    print("Application processing terminated due to errors.")
    print("----------------------------------")
    return {}


workflow = StateGraph(HRApplicationState)

workflow.add_node("extract_resume", extract_resume_node)
workflow.add_node("ats_scorer", ats_score_node)
workflow.add_node("summarize_resume", summarize_resume_node)
workflow.add_node("send_rejection", send_rejection_node)
workflow.add_node("send_acceptance", send_acceptance_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("handle_error", handle_error_node)    

workflow.set_entry_point("extract_resume")

def check_extraction_status(state: HRApplicationState) -> str:
    if state.get("extraction_error"):
        return "handle_error" 
    return "ats_scorer"
workflow.add_conditional_edges(
    "extract_resume",
    check_extraction_status,
    {
        "handle_error": "handle_error",
        "ats_scorer": "ats_scorer",
    }
)

def check_scoring_status(state: HRApplicationState) -> str:
    if state.get("scoring_error"):
        return "handle_error" 
    return "summarize_resume" 

workflow.add_conditional_edges(
    "ats_scorer",
    check_scoring_status,
    {
        "handle_error": "handle_error",
        "summarize_resume": "summarize_resume",
    }
)

def decide_next(state: HRApplicationState) -> str:
    print(f"--- Node: decide_next (ATS Score: {state.get('ats_score', 'N/A')}) ---")
    if state.get("extraction_error") or state.get("scoring_error") or state.get("error_message"):
        return "handle_error"

    score = state.get("ats_score", 0.0) 

    
    REJECTION_THRESHOLD = 60
    HUMAN_REVIEW_THRESHOLD = 75

    if score < REJECTION_THRESHOLD:
        return "send_rejection"
    elif REJECTION_THRESHOLD <= score < HUMAN_REVIEW_THRESHOLD:
        return "human_review"
    else: 
        return "send_acceptance"

workflow.add_conditional_edges(
    "summarize_resume", 
    decide_next,
    {
        "send_rejection": "send_rejection",
        "human_review": "human_review",
        "send_acceptance": "send_acceptance",
        "handle_error": "handle_error", 
    }
)


workflow.add_edge("send_rejection", END)
workflow.add_edge("send_acceptance", END)
workflow.add_edge("human_review", END) 
workflow.add_edge("handle_error", END)

hr_app_workflow = workflow.compile()

try:
    # This part is for visualization and may not work directly in all environments
    # Requires graphviz to be installed system-wide
    # from IPython.display import Image, display # Not for backend directly
    graph_image_bytes = hr_app_workflow.get_graph().draw_mermaid_png()
    with open("hr_workflow_graph.png", "wb") as f:
        f.write(graph_image_bytes)
except Exception as e:
    print(f"Could not generate graph visualization: {e}")
    
    