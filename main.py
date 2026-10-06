from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SummarizeRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "AI Notes Summerizer API"}

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    words = request.text.split()
    summary = " ".join(words[:20])
    
    return {"summary": summary}