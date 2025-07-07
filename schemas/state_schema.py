# TypedDict for shared LangGraph state
from typing_extensions import TypedDict

class AgentState(TypedDict):
    pdf_path:str 
    resume_text:str
    email:str
    job_text:str
    ats_score:float
    
