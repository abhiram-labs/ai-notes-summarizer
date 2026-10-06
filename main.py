import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from google import genai
from pydantic import BaseModel

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)

app = FastAPI()
def init_db():
    connection = sqlite3.connect("summaries.db")
    cursor = connection.cursor()
    
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               text TEXT NOT NULL,
               summary TEXT NOT NULL,
               created_at TEXT NOT NULL
            )
         """)
    connection.commit()
    connection.close()

init_db()

@app.get("/app")
def frontend():
    return FileResponse("static/index.html")

class SummarizeRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "AI Notes Summarizer API"}

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
    
    summary = response.text
    connection = sqlite3.connect("summaries.db")
    cursor = connection.cursor()
    
    cursor.execute(
        "INSERT INTO summaries (text, summary, created_at) VALUES (?, ?, ?)",
        (request.text, summary, datetime.now().isoformat())
    )
    
    connection.commit()
    connection.close()
    
    return {"summary": response.text}

@app.get("/history")
def history():
    connection = sqlite3.connect("summaries.db")
    cursor = connection.cursor()
    
    cursor.execute(
        "SELECT id, text, summary, created_at FROM summaries ORDER BY id DESC"
    )
    
    rows = cursor.fetchall()
    connection.close()
    
    return [
        {
            "id": row[0],
            "text": row[1],
            "summary": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]