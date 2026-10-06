import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from google import genai
from pydantic import BaseModel

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)

app = FastAPI()

@app.get("/app")
def frontend():
    return FileResponse("static/index.html")

class SummarizeRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "AI Notes Summerizer API"}

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    response=client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
        Summarize the following text in a short, clear paragraph.
        Do not add information that is not in the original text.
        
        Text:
        {request.text}
        """,
    )
    
    return {"summary": response.text}