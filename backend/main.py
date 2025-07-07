import os
import shutil
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()

from core.graph import hr_app_workflow
from core.state import HRApplicationState

app = FastAPI(title="HR AI Application Backend", version="1.0.0")


origins = [
    "http://localhost",
    "http://localhost:8501", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


TEMP_FILES_DIR = Path("backend/temp_files")
TEMP_FILES_DIR.mkdir(parents=True, exist_ok=True)


executor = ThreadPoolExecutor(max_workers=4) 

def get_executor():
    """Dependency for getting the shared ThreadPoolExecutor."""
    return executor


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down... Cleaning up temporary files.")
    if TEMP_FILES_DIR.exists():
        shutil.rmtree(TEMP_FILES_DIR)
        print(f"Cleaned up {TEMP_FILES_DIR}")
    executor.shutdown(wait=True)
    print("ThreadPoolExecutor shut down.")



@app.post("/process_resume/")
async def process_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    executor: ThreadPoolExecutor = Depends(get_executor)
):
    """
    Processes a resume PDF against a job description using the LangGraph workflow.
    """
    if not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_filename = f"{uuid.uuid4()}_{resume_file.filename}"
    pdf_path = TEMP_FILES_DIR / unique_filename

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
        print(f"Received and saved PDF to: {pdf_path}")

        
        initial_state: HRApplicationState = {
            'pdf_path': str(pdf_path),
            'job_text': job_description,
            'resume_text': '',
            'email': '',
            'ats_score': 0.0,
            'resume_summary': None,
            'extraction_error': False,
            'scoring_error': False,
            'email_error': False,
            'error_message': None,
            'email_sent': False, # Add this initialization
        }

        print("Invoking LangGraph workflow in background...")
        future = executor.submit(hr_app_workflow.invoke, initial_state)
        final_state = future.result() 
        print("LangGraph workflow completed.")

        
        return JSONResponse(content=final_state)

    except Exception as e:
        print(f"Unhandled error during resume processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        
        if pdf_path.exists():
            os.remove(pdf_path)
            print(f"Cleaned up temporary PDF: {pdf_path}")

@app.get("/")
async def root():
    return {"message": "HR AI Application Backend is running! Use /docs for API documentation."}