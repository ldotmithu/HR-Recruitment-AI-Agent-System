# Smart-HR-Recruitment-AI-Agents-System(Genrative AI)🤖📄

## Introduction ✨
The **HR-Recruitment-AI-Agent-System** is a cutting-edge, modular web application designed to revolutionize the recruitment process. By harnessing the power of **Large Language Models (LLMs)** and advanced **semantic search techniques**, it automates resume analysis, evaluates ATS compatibility, generates concise summaries, and streamlines candidate communication through automated emails. Candidates are intelligently routed for rejection, acceptance, or human review based on their qualifications. 

Built with a **FastAPI backend** for robust API services and a **Streamlit frontend** for an intuitive user interface, the application uses **LangGraph** to orchestrate complex workflows, ensuring scalability and maintainability. This is not an exhaustive list of features—more exciting capabilities are in the works! 🚀

---
## 📸  Workflow of a project:- 

![image](https://github.com/ldotmithu/Dataset/blob/main/hr_workflow_graph.png)

---

## Features 🚀
- **PDF Resume Extraction** 📄: Extracts text and contact details (e.g., email) from uploaded PDF resumes with precision.
- **ATS Compatibility Scoring** 📊: Computes a semantic similarity score between resumes and job descriptions using **Sentence Transformers**.
- **LLM-Powered Summarization** 🧠: Generates concise, job-relevant resume summaries using **OpenAI's GPT-4o**.
- **Automated Decision Making** 🤖:
  - **Rejection**: Sends polite rejection emails for candidates with ATS scores below 60%.
  - **Human Review**: Flags mid-range candidates (60-75%) for manual HR review.
  - **Acceptance**: Sends acceptance emails for high-scoring candidates (above 75%) with next steps.
- **Robust Error Handling** 🛡️: Tracks and manages errors (e.g., PDF parsing issues, LLM failures) within the LangGraph workflow.
- **Modular Architecture** 🧩: Separates backend (FastAPI) and frontend (Streamlit) for scalability and ease of maintenance.
- **Email Automation** 📧: Automatically sends tailored emails using **smtplib** for seamless candidate communication.
- **Temporary File Management** 🗂️: Safely handles uploaded resume files with automatic cleanup.

*And more to come!* Stay tuned for additional features like candidate analytics and advanced ATS scoring! 🌟

## Architecture 🏗️
The application follows a **client-server architecture** for optimal performance and modularity:

- **Frontend (Streamlit)** 🖼️:
  - Interactive web interface for uploading resumes and entering job descriptions.
  - Communicates with the FastAPI backend via HTTP requests.
- **Backend (FastAPI)** ⚙️:
  - Exposes a RESTful API endpoint (`/process_resume`) for processing resumes and job descriptions.
  - Orchestrates workflows using **LangGraph** for seamless task coordination.
  - Leverages **PyPDF2** for PDF parsing, **SentenceTransformers** for semantic scoring, **smtplib** for email automation, and **LangChain** for LLM integration.
  - Manages temporary file storage for uploaded resumes.
- **LangGraph Workflow** 🔄:
  - Defines a state machine (`HRApplicationState`) to track processing stages.
  - Nodes handle specific tasks: PDF extraction, ATS scoring, summarization, email sending, and error handling.
  - Conditional edges (`decide_next`) dynamically route candidates based on ATS scores or errors.

## Setup & Installation 🔧
Get the HR AI Resume Analyzer up and running on your local machine with these steps.

### Prerequisites 📋
- **Python 3.10** 🐍
- **Git** 📦

### Clone the Repository 📦
```bash
git clone https://github.com/ldotmithu/HR-Recruitment-AI-Agent-System.git
cd HR-Recruitment-AI-Agent-System
```

### Create Virtual Environment 🛠️
Use a virtual environment to manage dependencies:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
```

### Install Dependencies 📚
Install required Python packages:
```bash
pip install -r requirements.txt
```
*Note*: The `sentence-transformers` library downloads a ~400MB model (`all-MiniLM-L6-v2`) on first use.

### Environment Variables (.env) 🔑
Create a `.env` file in the project root (`HR-Recruitment-AI-Agent-System/`) with the following:
```ini
EMAIL_SENDER="your_email@gmail.com"
EMAIL_PASSWORD="your_gmail_app_password" # Use an App Password for Gmail 
OPENAI_API_KEY="your_openai_api_key_here"

# Optional: Specify backend URL if not localhost:8000
# BACKEND_URL="http://your_backend_ip:8000"
```
**Important for Gmail Users**: Generate an [App Password](https://support.google.com/accounts/answer/185833) for `smtplib` to send emails, as Google no longer supports less secure app access.

## How to Run ▶️
Run the backend and frontend in separate terminal windows.

### Run the Backend (FastAPI) ⚙️
In the first terminal:
```bash
cd backend/
# Activate virtual environment (if not already active)
# Windows: ..\venv\Scripts\activate

uvicorn main:app --reload --port 8000
```
The server will run at `http://127.0.0.1:8000`. The `--reload` flag enables auto-restart on code changes.

### Run the Frontend (Streamlit) 🖼️
In a second terminal:
```bash
cd frontend/
# Activate virtual environment (if not already active)
# Windows: ..\venv\Scripts\activate
streamlit run app.py
```
The Streamlit app will open in your browser at `http://localhost:8501`.

## Usage 🖥️
1. **Access the App**: Navigate to `http://localhost:8501`.
2. **Upload Resume**: Use the "Browse files" button to upload a PDF resume.
3. **Enter Job Description**: Paste the job description into the text area.
4. **Process**: Click "Process Application" to analyze the resume.
5. **View Results**: See the ATS score, applicant email, resume summary, automated decision (Accepted/Rejected/Human Review), and any error messages.
6. **Debugging**: Review the JSON output for detailed processing information.

## Project Structure 📂
```
hr-ai-resume-analyzer/
├── backend/
│   ├── main.py             # FastAPI entry point with API endpoints
│   ├── core/
│   │   ├── __init__.py     # Makes 'core' a Python package
│   │   ├── state.py        # Defines HRApplicationState TypedDict
│   │   ├── tools.py        # PDF extraction, ATS scoring, email tools
│   │   ├── llm_chains.py   # LLM setup and summarization logic
│   │   └── graph.py        # LangGraph workflow with nodes and edges
│   └── temp_files/         # Temporary storage for uploaded PDFs
├── frontend/
│   └── app.py              # Streamlit UI for user interaction
├── .env                    # Environment variables (credentials, API keys)
└── requirements.txt        # Python dependencies
```

## Future Enhancements 🌟
- **Database Integration** 🗄️: Store resume data, ATS scores, and statuses in a database (e.g., PostgreSQL, SQLite) for analytics and tracking.
- **Asynchronous Task Queue** ⏳: Use Redis with Celery/RQ for scalable background processing.
- **Dockerization** 🐳: Containerize the app for seamless deployment.
- **Advanced ATS Scoring** 📈: Add custom rubrics and granular skill extraction.
- **Personalized Feedback** 💬: Provide detailed rejection feedback using LLMs.
- **Interview Question Generation** ❓: Create tailored interview questions for accepted candidates.
- **User Authentication** 🔒: Support multi-user HR systems.
- **Enhanced UI/UX** 🎨: Add progress bars, better styling, and status updates.
- **Email Templating** 📧: Use Jinja2 for professional, customizable email templates.
- **Resume Keyword Highlighting** 🔍: Visually highlight key terms in resumes matching the job description.

## Troubleshooting 🛠️
- **PDF Extraction Errors**: Ensure the PDF is text-based (not scanned). Try a different PDF library like `pdfplumber` if issues persist.
- **Email Sending Fails**: Verify your `.env` file has a valid `EMAIL_SENDER` and `EMAIL_PASSWORD`. Check Gmail's App Password setup.
- **LLM Errors**: Confirm your `OPENAI_API_KEY` is valid and you have sufficient API credits.
- **Backend Not Reachable**: Ensure the FastAPI server is running on `http://127.0.0.1:8000` and the `.env` `BACKEND_URL` (if set) is correct.
- **Large Model Downloads**: The first run of `sentence-transformers` may take time to download the model. Ensure a stable internet connection.



## License 📜
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Contact 📬
For questions, feedback, or support, reach out via:
- Built with ❤️ by Mithurshan [linkedin](https://www.linkedin.com/in/mithurshan6)
- **Email**: ldotmithurshan222@gmail.com
- **GitHub Issues**: [https://github.com/ldotmithu/](https://github.com/ldotmithu/)

Happy hiring! 🚀