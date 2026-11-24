from fastapi import FastAPI
from pydantic import BaseModel
from fin_reg_copilot import rag

app = FastAPI(title="Fin-Reag Copilot")

class Ask(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/retrieve")
def retrieve(req: Ask):
    return {"chunks": rag.retrieve(req.question)}
@app.post("/ask")

def ask(req:Ask):
    return rag.answer(req.question)
