from fastapi import FastAPI
from pydantic import BaseModel
from app import ask_ai


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI SQL Analytics API",
    description="Natural Language to SQL Analytics API",
    version="1.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str


# ============================================================
# HOME ROUTE
# ============================================================

@app.get("/")
def home():

    return {
        "message": "AI SQL Analytics API is running"
    }


# ============================================================
# SQL ANALYTICS ENDPOINT
# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    sql, result, message = ask_ai(
        request.question
    )

    # SQL validation / execution failed
    if result is None:

        return {
            "question": request.question,
            "sql": sql,
            "status": "error",
            "message": message
        }

    # Convert DataFrame to JSON-compatible format
    data = result.to_dict(
        orient="records"
    )

    return {
        "question": request.question,
        "sql": sql,
        "status": "success",
        "message": message,
        "result": data
    }