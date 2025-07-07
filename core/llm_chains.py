import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

try:
    llm = ChatGroq(model="gemma2-9b-it",temperature=0.2)
    print("Groq LLM initialized successfully")
except Exception as e:
    raise e 

if llm:
    resume_summarizer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an HR assistant. Summarize the following resume for a quick review, highlighting key skills and experience relevant to the job description."),
        ("user", "Resume:\n{resume_text}\n\nJob Description:\n{job_text}")
    ])
    resume_summarizer = resume_summarizer_prompt | llm | StrOutputParser()
    