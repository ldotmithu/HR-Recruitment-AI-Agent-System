from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import json

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

try:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
except Exception as e:
    print(f"Error initializing ChatGroq: {e}")
    raise ConnectionError("Failed to initialize LLM. Check API key and model name.") from e

template = ChatPromptTemplate.from_messages([
    ("system", """You are an ATS scoring assistant.
    Score the match between a candidate resume and a job description out of 100.
    Provide 3 concise reasons for your score.
    Your output MUST be a JSON object with the following structure:
    {{
        "score": (integer between 0 and 100),
        "reasons": [
            "Reason 1",
            "Reason 2",
            "Reason 3"
        ]
    }}
    Ensure the score is an integer and reasons are strings in a list."""),
    ("human", "Resume:\n{resume}\n\nJob Description:\n{job}")
])

def llm_ats_score(resume_text, job_text):
    """
    Scores the match between a candidate resume and a job description using an LLM.
    """
    prompt = template.format_messages(resume=resume_text, job=job_text)
    
    try:
        response = llm.invoke(prompt)
        response_content = json.loads(response.content)
        
        score = float(response_content.get("score", 50))
        reasons = response_content.get("reasons", ["No reasons provided.", "No reasons provided.", "No reasons provided."])
        
        score = max(0, min(100, int(score)))
        if not isinstance(reasons, list) or len(reasons) != 3:
            reasons = ["Invalid reasons format.", "Invalid reasons format.", "Invalid reasons format."]

    except json.JSONDecodeError:
        print(f"Warning: LLM response was not valid JSON. Response: {response.content}")
        score = 50.0
        reasons = ["Could not parse LLM output.", "Output format unexpected.", "Please check LLM response structure."]
    except Exception as e:
        print(f"An unexpected error occurred during LLM invocation or parsing: {e}")
        score = 50.0
        reasons = ["An error occurred.", "Please try again.", "Check input texts."]

    return {"ats_score": score}