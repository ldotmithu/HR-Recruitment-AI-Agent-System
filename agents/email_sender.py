# Sends rejection email
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["EMAIL_SENDER"] = os.getenv("EMAIL_SENDER")
os.environ["EMAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")

def send_rejection_email(candidate_email):
    msg = EmailMessage()
    msg.set_content("Thanks for applying. Unfortunately, your resume didn't match our current role requirements. Please apply again in the future.")
    msg['Subject'] = "Application Status"
    msg['From'] = os.getenv("EMAIL_SENDER")
    msg['To'] = candidate_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)
    return {"email_sent": True}