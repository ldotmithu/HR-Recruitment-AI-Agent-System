from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Optional

from core.state import HRApplicationState
from core.tools import (
    extract_text_from_pdf,
    llm_ats_score,
    send_rejection_email,
    send_acceptance_email
)
from core.llm_chains import resume_summarizer


def extract_resume_node(state: HRApplicationState) -> HRApplicationState:
    """Extracts text and email from the PDF resume."""
    print(f"--- Node: extract_resume --- Processing {state.get('pdf_path', 'N/A')}")
    pdf_path = state["pdf_path"]
    
    extracted_data = extract_text_from_pdf.invoke({"pdf_path": pdf_path})
    

    updated_state: HRApplicationState = {
        **state,
        "resume_text": extracted_data.get("resume_text", ""),
        "email": extracted_data.get("email", ""),
        "extraction_error": extracted_data.get("extraction_error", False),
        "error_message": extracted_data.get("error_message", None),
    }
    print(f"Node: extract_resume finished. State update: {updated_state}")
    return updated_state

def ats_scorer_node(state: HRApplicationState) -> HRApplicationState:
    """Computes the ATS compatibility score."""
    print(f"--- Node: ats_scorer ---")
    
    if state.get("extraction_error"):
        print("Skipping ATS scoring due to prior extraction error.")
        updated_state: HRApplicationState = {
            **state,
            "scoring_error": True,
            "error_message": "Skipped ATS scoring due to extraction error."
        }
        print(f"Node: ats_scorer skipped. State update: {updated_state}")
        return updated_state
        
    resume_text = state.get("resume_text", "")
    job_text = state.get("job_text", "")

    if not resume_text or not job_text:
        error_msg = "'resume_text' or 'job_text' is missing for ATS scoring."
        print(f"{error_msg}")
        updated_state: HRApplicationState = {
            **state,
            "ats_score": 0.0,
            "scoring_error": True,
            "error_message": error_msg
        }
        print(f"Node: ats_scorer error. State update: {updated_state}")
        return updated_state
    
    score_data = llm_ats_score.invoke({
        "resume_text": resume_text,
        "job_text": job_text
    })
    
    updated_state: HRApplicationState = {
        **state, 
        "ats_score": score_data.get("ats_score", 0.0),
        "scoring_error": score_data.get("scoring_error", False),
        "error_message": score_data.get("error_message", None),
    }
    print(f"Node: ats_scorer finished. State update: {updated_state}")
    return updated_state

def summarize_resume_node(state: HRApplicationState) -> HRApplicationState:
    """Summarizes the resume using an LLM."""
    print(f"--- Node: summarize_resume ---")
    
    if state.get("extraction_error") or state.get("scoring_error"):
        print("Skipping resume summarization due to prior errors.")
        updated_state: HRApplicationState = {
            **state,
            "resume_summary": None 
        }
        print(f"Node: summarize_resume skipped. State update: {updated_state}")
        return updated_state
    
    if not resume_summarizer:
        error_msg = "LLM summarizer is not initialized. Skipping summarization."
        print(f"{error_msg}")
        updated_state: HRApplicationState = {
            **state,
            "resume_summary": None,
            "error_message": error_msg 
        }
        print(f"Node: summarize_resume error. State update: {updated_state}")
        return updated_state

    resume_text = state.get("resume_text", "")
    job_text = state.get("job_text", "")

    if not resume_text or not job_text:
        error_msg = "'resume_text' or 'job_text' missing for summarization."
        print(f"{error_msg}")
        updated_state: HRApplicationState = {
            **state,
            "resume_summary": None,
            "error_message": error_msg 
        }
        print(f"Node: summarize_resume error. State update: {updated_state}")
        return updated_state

    try:
        summary = resume_summarizer.invoke({
            "resume_text": resume_text,
            "job_text": job_text
        })
        print("Resume summarized.")
        updated_state: HRApplicationState = {
            **state,
            "resume_summary": summary
        }
        print(f"Node: summarize_resume finished. State update: {updated_state}")
        return updated_state
    except Exception as e:
        error_msg = f"Error summarizing resume: {e}"
        print(f"{error_msg}")
        updated_state: HRApplicationState = {
            **state,
            "resume_summary": None,
            "error_message": error_msg
        }
        print(f"Node: summarize_resume error. State update: {updated_state}")
        return updated_state


def send_rejection_node(state: HRApplicationState) -> HRApplicationState:
    """Sends a rejection email."""
    print(f"--- Node: send_rejection ---")
    
    
    if state.get("email_error"): 
         print("Skipping rejection email due to prior email configuration error.")
         return state 
    
    email = state.get("email")
    if not email:
        error_msg = "Skipping rejection email: No email address found."
        print(f"❌ {error_msg}")
        updated_state: HRApplicationState = {
            **state,
            "email_error": True,
            "error_message": error_msg
        }
        print(f"Node: send_rejection error. State update: {updated_state}")
        return updated_state

    email_sent_data = send_rejection_email.invoke({"email": email})
    updated_state: HRApplicationState = {
        **state,
        "email_sent": email_sent_data.get("email_sent", False),
        "email_error": email_sent_data.get("email_error", False),
        "error_message": email_sent_data.get("error_message", None),
    }
    print(f"Node: send_rejection finished. State update: {updated_state}")
    return updated_state

def send_acceptance_node(state: HRApplicationState) -> HRApplicationState:
    """Sends an acceptance email."""
    print(f"--- Node: send_acceptance ---")

    if state.get("email_error"): 
         print("Skipping acceptance email due to prior email configuration error.")
         return state
         
    email = state.get("email")
    if not email:
        error_msg = "Skipping acceptance email: No email address found."
        print(f"{error_msg}")
        updated_state: HRApplicationState = {
            **state,
            "email_error": True,
            "error_message": error_msg
        }
        print(f"Node: send_acceptance error. State update: {updated_state}")
        return updated_state

    email_sent_data = send_acceptance_email.invoke({"email": email})
    updated_state: HRApplicationState = {
        **state,
        "email_sent": email_sent_data.get("email_sent", False),
        "email_error": email_sent_data.get("email_error", False),
        "error_message": email_sent_data.get("error_message", None),
    }
    print(f"Node: send_acceptance finished. State update: {updated_state}")
    return updated_state

def human_review_node(state: HRApplicationState) -> HRApplicationState:
    """Logs details for human review."""
    print(f"--- Node: human_review ---")
    print("\n--- CANDIDATE FOR HUMAN REVIEW ---")
    print(f"Email: {state.get('email', 'N/A')}")
    print(f"ATS Score: {state.get('ats_score', 'N/A')}")
    print(f"Resume Summary:\n{state.get('resume_summary', 'No summary available.')}\n")
    print("----------------------------------")
    # In a real application, this would trigger a notification, save to a
    # pending review queue in a database, etc.
    print(f"Node: human_review finished. State update: {state}")
    return state # No state change needed for this action

def handle_error_node(state: HRApplicationState) -> HRApplicationState:
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
    # This node could send an alert to HR, log to an error tracking system, etc.
    print(f"Node: handle_error finished. State update: {state}")
    return state # No state change needed, just logging/alerting




workflow = StateGraph(HRApplicationState)


workflow.add_node("extract_resume", extract_resume_node)
workflow.add_node("ats_scorer", ats_scorer_node)
workflow.add_node("summarize_resume", summarize_resume_node)
workflow.add_node("send_rejection", send_rejection_node)
workflow.add_node("send_acceptance", send_acceptance_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("handle_error", handle_error_node)



workflow.set_entry_point("extract_resume")


def check_extraction_status(state: HRApplicationState) -> str:
    print(f"--- Edge: check_extraction_status ---")
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
    print(f"--- Edge: check_scoring_status ---")
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
    print(f"--- Edge: decide_next (ATS Score: {state.get('ats_score', 'N/A')}) ---")
    
    if state.get("extraction_error") or state.get("scoring_error") or state.get("error_message"):
        print("Prior error detected, routing to handle_error.")
        return "handle_error"

    score = state.get("ats_score", 0.0) 

    
    REJECTION_THRESHOLD = 60
    HUMAN_REVIEW_THRESHOLD = 75

    if score < REJECTION_THRESHOLD:
        print(f"Score {score} < {REJECTION_THRESHOLD}, routing to send_rejection.")
        return "send_rejection"
    elif REJECTION_THRESHOLD <= score < HUMAN_REVIEW_THRESHOLD:
        print(f"Score {REJECTION_THRESHOLD} <= {score} < {HUMAN_REVIEW_THRESHOLD}, routing to human_review.")
        return "human_review"
    else: 
        print(f"Score {score} >= {HUMAN_REVIEW_THRESHOLD}, routing to send_acceptance.")
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
print("LangGraph workflow compiled successfully.")


try:
    graph_image_bytes = hr_app_workflow.get_graph().draw_mermaid_png()
    with open("hr_workflow_graph.png", "wb") as f:
        f.write(graph_image_bytes)
    print("Graph visualization saved as hr_workflow_graph.png")
except Exception as e:
    print(f"Could not generate graph visualization: {e}. Ensure graphviz is installed.")