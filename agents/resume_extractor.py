# Extract text + email from resume

import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and attempts to find an email address within the text.
    """
    text = "" 
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or "" 
    
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return {"resume_text": text, "email": email_match.group() if email_match else None}
            
