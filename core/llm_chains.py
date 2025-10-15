import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI


try:
    llm = ChatGroq(model="openai/gpt-oss-20b",temperature=0.2)
    #llm = GoogleGenerativeAI(model="gemini-1.5-pro")
    print("Google LLM initialized successfully")
except Exception as e:
    raise e 

if llm:
    resume_summarizer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an HR assistant. Summarize the following resume for a quick review, highlighting key skills and experience relevant to the job description."),
        ("user", "Resume:\n{resume_text}\n\nJob Description:\n{job_text}")
    ])
    resume_summarizer = resume_summarizer_prompt | llm | StrOutputParser()
else:
    resume_summarizer = None    