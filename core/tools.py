from langchain_core.tools import tool
import PyPDF2
from sentence_transformers import SentenceTransformer,util
from email.message import EmailMessage
import re ,os 
import smtplib
from dotenv import load_dotenv
load_dotenv()
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("model loaded successfully")
except Exception as e:
    raise e 

@tool
def extract_text_from_pdf(pdf_path):
    """Extract text and email address from a PDF resume."""
    try:
        with open(pdf_path,"rb") as f:
            reader = PyPDF2.PdfReader(f)
            text =""
            for page in reader.pages:
                text += page.extract_text()
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",text)
        email = email_match.group(0) if email_match else ""
        
        return {"resume_text":text,"email":email,"extraction_error":False,"error_message":None}
    except Exception as e:
        return {"resume_text":"","email":"","extraction_error":True,"error_message":e}    

@tool
def llm_ats_score(resume_text:str,job_text:str):
    """
    Compute semantic similarity between resume and job description using embeddings.
    Returns an ATS score between 0–100.
    """
    if not model:
        error_msg = "SentenceTransformer model not loaded for ATS scoring."
        return {"ats_score":0.0,"scoring_error":True,"error_message":error_msg}
    
    try:
        embaddings = model.encode([resume_text,job_text])
        similarity= util.cos_sim(embaddings[0],embaddings[1]).item()
        score = round(similarity*100,2)
        return{"ats_score":score,"scoring_error":False,"error_message":None}
    except Exception as e :
        return{"ats_score":0.0,"scoring_error":True,"error_message":e}


@tool
def send_rejection_email(email:str):
    """Send a polite rejection email if ATS score is low."""
    sender = os.getenv("EMAIL_SENDER")
    password= os.getenv("EMAIL_PASSWORD")
    
    if not sender and password:
        error_msg = "Email sender or password not configured in .env"
        return {"email_sent": False, "email_error": True, "error_message": error_msg}
    
    try:
        msg = EmailMessage()
        msg["Subject"] = "Regarding Your Job Application"
        msg["From"] = sender
        msg["To"] = email
        msg.set_content("Thank you for your application. We regret to inform you that we will not be moving forward with your application at this time. Please feel free to reapply in the future if your qualifications align with our future openings. Best wishes!")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"Rejection email sent to: {email}")
        return {"email_sent": True, "email_error": False, "error_message": None}
    except Exception as e:
        error_msg = f"Error sending rejection email to {email}: {e}"
        print(f"{error_msg}")
        return {"email_sent": False, "email_error": True, "error_message": error_msg}

@tool
def send_acceptance_email(email:str):
    """Send a polite rejection email if ATS score is low."""
    sender = os.getenv("EMAIL_SENDER")
    password= os.getenv("EMAIL_PASSWORD")
    
    if not sender and password:
        error_msg = "Email sender or password not configured in .env"
        return {"email_sent": False, "email_error": True, "error_message": error_msg}
    
    try:
        msg = EmailMessage()
        msg["Subject"] = "Exciting News Regarding Your Job Application!"
        msg["From"] = sender
        msg["To"] = email
        msg.set_content("Great news! We're impressed with your application and would like to invite you for an interview. Please expect a follow-up email with scheduling details shortly. We look forward to speaking with you!")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"Acceptance email sent to: {email}")
        return {"email_sent": True, "email_error": False, "error_message": None}
    except Exception as e:
        error_msg = f"Error sending acceptance email to {email}: {e}"
        print(f"{error_msg}")
        return {"email_sent": False, "email_error": True, "error_message": error_msg}
    
       