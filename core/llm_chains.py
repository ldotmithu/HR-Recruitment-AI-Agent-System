import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI


try:
    llm = ChatGroq(model="openai/gpt-oss-20b",temperature=0.2)
    #llm = GoogleGenerativeAI(model="gemini-1.5-pro")
    print(" LLM initialized successfully")
except Exception as e:
    raise e 

if llm:
    resume_summarizer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an HR assistant. Summarize the following resume for a quick review, highlighting key skills and experience relevant to the job description."),
        ("user", "Resume:\n{resume_text}\n\nJob Description:\n{job_text}")
    ])
    resume_summarizer = resume_summarizer_prompt | llm | StrOutputParser()

    # Interview Chain
    interview_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an experienced and professional HR interviewer. Your goal is to conduct a mock interview with a candidate based on their resume and the job description.
        
        Guidelines:
        1.  Start by welcoming the candidate if the chat history is empty.
        2.  Ask ONE relevant question at a time. Do not overwhelm the candidate.
        3.  Base your questions on the candidate's resume skills/experience and the job requirements.
        4.  Evaluate the candidate's previous response (if any) briefly before asking the next question.
        5.  Keep the tone professional yet encouraging.
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_text}
        
        Chat History:
        {chat_history}
        """),
        ("user", "{user_input}")
    ])
    interview_chain = interview_prompt | llm | StrOutputParser()

else:
    resume_summarizer = None
    interview_chain = None