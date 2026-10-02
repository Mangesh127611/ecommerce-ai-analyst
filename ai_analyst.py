
import os
import re
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=API_KEY)

DB_PATH = BASE_DIR / "ecommerce.db"

MODEL = "openai/gpt-oss-20b"


# ============================================================
# DATABASE SCHEMA
# ============================================================

def get_schema():
    conn = sqlite3.connect(DB_PATH)

    try:
        columns = conn.execute(
            "PRAGMA table_info(online_shoppers)"
        ).fetchall()

        schema = "\n".join(
            f"- {column[1]} ({column[2]})"
            for column in columns
        )

        return schema

    finally:
        conn.close()


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(sql):
    """
    Basic safety validation.
    Only allows a single SELECT query.
    """

    sql = sql.strip()

    # Remove markdown fences if the model accidentally adds them
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    if not sql.upper().startswith("SELECT"):
        raise ValueError("AI generated a non-SELECT query.")

    # Prevent multiple SQL statements
    if ";" in sql[:-1]:
        raise ValueError("Multiple SQL statements are not allowed.")

    # Block dangerous SQL keywords
    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "ATTACH",
        "DETACH",
        "PRAGMA"
    ]

    upper_sql = sql.upper()

    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise ValueError(
                f"Unsafe SQL keyword detected: {keyword}"
            )

    return sql


# ============================================================
# GENERATE SQL USING GROQ
# ============================================================

def generate_sql(question):

    schema = get_schema()

    prompt = f"""
You are an expert business data analyst and SQLite SQL generator.

Database:
SQLite

Table:
online_shoppers

Schema:
{schema}

IMPORTANT DATA DEFINITIONS:

1. Revenue is NOT monetary revenue.
2. Revenue is a boolean purchase outcome:
   - Revenue = 1 means the website session resulted in a purchase.
   - Revenue = 0 means the website session did not result in a purchase.
3. Therefore, Revenue should NEVER be interpreted as dollars, rupees,
   sales amount, order value, or monetary revenue.
4. PageValues is a derived page-value feature.
5. PageValues is NOT actual monetary sales revenue.
6. Conversion rate can be calculated using:
   AVG(Revenue)
   or
   SUM(Revenue) * 1.0 / COUNT(*)
7. If calculating conversion rate, multiply the decimal result by 100
   when appropriate.
8. Use only the online_shoppers table.

User question:
{question}

Generate ONE valid SQLite SELECT query that answers the question.

Rules:
- Return ONLY SQL.
- No markdown.
- No explanation.
- Only SELECT queries are allowed.
- Never modify data.
- Never create or delete tables.
- Use SQLite-compatible syntax.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate safe, accurate SQLite SQL "
                    "for business analytics."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    sql = validate_sql(sql)

    return sql


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.execute(sql)

        if cursor.description is None:
            raise ValueError("SQL query did not return a result.")

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        conn.close()


# ============================================================
# EXPLAIN DATABASE RESULT USING GROQ
# ============================================================

def explain_result(question, sql, result):

    prompt = f"""
You are a professional e-commerce business data analyst.

User question:
{question}

SQL query generated:
{sql}

Actual database result:
{result}

IMPORTANT DATA DEFINITIONS:

- Revenue = 1 means the session resulted in a purchase.
- Revenue = 0 means the session did not result in a purchase.
- Revenue is NOT monetary revenue.
- Never describe Revenue as dollars, rupees, currency, sales amount,
  order value, or money.
- PageValues is NOT actual monetary revenue.
- A conversion rate represents the percentage of sessions that resulted
  in a purchase.

YOUR TASK:

Explain the actual database result to a business user.

Rules:
1. Use ONLY the provided database result.
2. Never invent numbers.
3. Convert conversion-rate decimals into percentages when appropriate.
4. Clearly state what the number means.
5. Do not confuse purchase conversion with monetary revenue.
6. Do not claim causation from correlation or observed patterns.
7. Do not recommend upselling, cross-selling, pricing changes,
   or marketing actions unless the actual result directly supports
   the recommendation.
8. Keep the explanation concise and professional.
9. Mention the most important business insight supported by the result.
10. If the result is insufficient to make a business recommendation,
    simply state the observed pattern without inventing one.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You explain real database results accurately "
                    "without inventing facts."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    return response.choices[0].message.content.strip()


# ============================================================
# MAIN AI ANALYST PIPELINE
# ============================================================

def ask_analyst(question):

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    sql = generate_sql(question)

    result = execute_sql(sql)

    explanation = explain_result(
        question,
        sql,
        result
    )

    return {
        "question": question,
        "sql": sql,
        "result": result,
        "explanation": explanation
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = "What is the overall conversion rate?"

    response = ask_analyst(question)

    print("\n" + "=" * 60)
    print("QUESTION")
    print("=" * 60)

    print(response["question"])

    print("\n" + "=" * 60)
    print("GENERATED SQL")
    print("=" * 60)

    print(response["sql"])

    print("\n" + "=" * 60)
    print("DATABASE RESULT")
    print("=" * 60)

    print(response["result"])

    print("\n" + "=" * 60)
    print("AI EXPLANATION")
    print("=" * 60)

    print(response["explanation"])

    print("\n" + "=" * 60)
    print("GENAI ANALYST PIPELINE COMPLETED")
    print("=" * 60)

