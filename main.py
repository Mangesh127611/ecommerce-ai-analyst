
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_connection
from ai_analyst import ask_analyst


app = FastAPI(
    title="E-commerce AI Analyst API",
    description="GenAI-powered E-commerce Analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "E-commerce AI Analyst API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    conn = get_connection()

    try:
        result = conn.execute(
            "SELECT COUNT(*) AS total_rows FROM online_shoppers"
        ).fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "total_rows": result["total_rows"]
        }

    finally:
        conn.close()


@app.get("/dashboard")
def dashboard():

    conn = get_connection()

    try:
        total_sessions = conn.execute(
            "SELECT COUNT(*) FROM online_shoppers"
        ).fetchone()[0]

        purchases = conn.execute(
            "SELECT SUM(Revenue) FROM online_shoppers"
        ).fetchone()[0] or 0

        conversion_rate = (
            (purchases / total_sessions) * 100
            if total_sessions else 0
        )

        avg_page_value = conn.execute(
            "SELECT AVG(PageValues) FROM online_shoppers"
        ).fetchone()[0] or 0

        monthly = conn.execute("""
            SELECT
                Month AS month,
                ROUND(AVG(Revenue) * 100, 2) AS conversion_rate
            FROM online_shoppers
            GROUP BY Month
            ORDER BY
                CASE Month
                    WHEN 'Jan' THEN 1
                    WHEN 'Feb' THEN 2
                    WHEN 'Mar' THEN 3
                    WHEN 'Apr' THEN 4
                    WHEN 'May' THEN 5
                    WHEN 'June' THEN 6
                    WHEN 'Jul' THEN 7
                    WHEN 'Aug' THEN 8
                    WHEN 'Sep' THEN 9
                    WHEN 'Oct' THEN 10
                    WHEN 'Nov' THEN 11
                    WHEN 'Dec' THEN 12
                END
        """).fetchall()

        visitor_type = conn.execute("""
            SELECT
                VisitorType AS visitor_type,
                ROUND(AVG(Revenue) * 100, 2) AS conversion_rate
            FROM online_shoppers
            GROUP BY VisitorType
            ORDER BY conversion_rate DESC
        """).fetchall()

        engagement = conn.execute("""
            SELECT
                Engagement_Level AS engagement_level,
                ROUND(AVG(Revenue) * 100, 2) AS conversion_rate
            FROM online_shoppers
            GROUP BY Engagement_Level
            ORDER BY
                CASE Engagement_Level
                    WHEN 'Low' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'High' THEN 3
                    WHEN 'Very High' THEN 4
                END
        """).fetchall()

        page_value = conn.execute("""
            SELECT
                CASE
                    WHEN PageValues > 0 THEN 'PageValue > 0'
                    ELSE 'PageValue = 0'
                END AS segment,
                ROUND(AVG(Revenue) * 100, 2) AS conversion_rate
            FROM online_shoppers
            GROUP BY segment
        """).fetchall()

        return {
            "success": True,
            "data": {
                "total_sessions": total_sessions,
                "purchases": purchases,
                "conversion_rate": round(conversion_rate, 2),
                "avg_page_value": round(avg_page_value, 2),
                "monthly": [dict(row) for row in monthly],
                "visitor_type": [dict(row) for row in visitor_type],
                "engagement": [dict(row) for row in engagement],
                "page_value": [dict(row) for row in page_value]
            }
        }

    finally:
        conn.close()


@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question.strip():
        return {
            "success": False,
            "error": "Question cannot be empty."
        }

    try:
        result = ask_analyst(request.question)

        return {
            "success": True,
            "data": result
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }

