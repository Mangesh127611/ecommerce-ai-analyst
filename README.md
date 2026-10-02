# E-commerce AI Analyst

> GenAI-powered e-commerce analytics platform that converts natural-language business questions into SQL queries, executes them on real data, and generates business insights.

## 🎯 Business Problem

E-commerce teams have large amounts of website-session data but answering business questions often requires SQL or technical support.

This project provides a natural-language analytics interface where users can ask questions such as:

* What is the overall conversion rate?
* Which visitor type has the highest conversion rate?
* Which month has the highest conversion rate?
* How does engagement level affect conversion?

The system converts the question into SQL, queries the real SQLite database, and explains the result using GenAI.

## 🏗️ Architecture

```text
User Question
      ↓
React Frontend
      ↓
FastAPI Backend
      ↓
Groq LLM
      ↓
SQL Generation
      ↓
SQLite Database
      ↓
Real Query Result
      ↓
AI Business Explanation
      ↓
React UI
```

## 🛠️ Tech Stack

| Technology | Purpose                     |
| ---------- | --------------------------- |
| Python     | Data & backend logic        |
| SQL        | Business analytics          |
| SQLite     | Analytics database          |
| FastAPI    | REST API                    |
| Groq       | GenAI / LLM                 |
| React      | Frontend                    |
| Vite       | Frontend tooling            |
| Power BI   | Business dashboard          |
| Pandas     | Data preparation & analysis |

## 📊 Dataset

The project uses the **UCI Online Shoppers Purchasing Intention** dataset.

The dataset contains website-session information such as:

* Visitor type
* Traffic source
* Page views
* Product-related activity
* Bounce rate
* Exit rate
* Page values
* Weekend activity
* Purchase outcome

After cleaning and duplicate removal, the analytical dataset contains **12,205 sessions**.

### Important Data Definition

`Revenue` represents whether a session resulted in a purchase.

```text
Revenue = 1 → Purchase
Revenue = 0 → No purchase
```

It is **not monetary revenue**.

`PageValues` is also a derived page-value feature and should not be interpreted as actual sales revenue.

## 📈 Dashboard

The analytics dashboard provides:

* Total sessions
* Purchases
* Overall conversion rate
* Average PageValues
* Monthly conversion performance
* Visitor-type conversion
* Engagement-level conversion
* PageValue segment comparison

## 🤖 AI Analyst

The AI Analyst allows users to interact with the database using natural language.

Example:

```text
Which visitor type has the highest conversion rate?
```

The system generates SQL similar to:

```sql
SELECT
    VisitorType,
    AVG(Revenue) * 100 AS conversion_rate
FROM online_shoppers
GROUP BY VisitorType
ORDER BY conversion_rate DESC;
```

The SQL is executed against the SQLite database and the real result is then passed to the AI for a concise business explanation.

## 🔐 SQL Safety

The AI-generated query is validated before execution.

The backend:

* Allows only `SELECT` queries
* Blocks data modification commands
* Prevents multiple SQL statements
* Rejects unsafe SQL keywords
* Executes queries against the intended analytics table

## 💡 Key Analytical Findings

Based on the cleaned dataset:

* Overall purchase conversion is approximately **15.63%**.
* New visitors show a higher observed conversion rate than returning visitors.
* Conversion increases across the defined engagement levels.
* Sessions with `PageValues > 0` show substantially higher observed conversion than sessions with `PageValues = 0`.
* November has the highest observed monthly conversion in this dataset.

These are observed relationships in the dataset and should not automatically be interpreted as causal effects.

## 📁 Project Structure

```text
backend/
│
├── ai_analyst.py
├── database.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## ⚙️ Backend Setup

Clone the repository:

```bash
git clone https://github.com/Mangesh127611/ecommerce-ai-analyst.git
cd ecommerce-ai-analyst
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Start the FastAPI server:

```bash
python -m uvicorn main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 🌐 Frontend

The React frontend is maintained separately in the frontend project.

Start it with:

```bash
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## 🔌 API Endpoints

### Health Check

```http
GET /health
```

### Dashboard Data

```http
GET /dashboard
```

### AI Analytics

```http
POST /ask
```

Request:

```json
{
  "question": "What is the overall conversion rate?"
}
```

## 🎯 Skills Demonstrated

This project demonstrates practical experience with:

* Python
* SQL
* Data Cleaning
* Exploratory Data Analysis
* Business Analytics
* Power BI
* FastAPI
* REST APIs
* SQLite
* React
* GenAI
* Natural Language → SQL
* AI-assisted Business Intelligence
* SQL validation and security
* End-to-end analytics application development

## 🚀 Future Improvements

Potential extensions include:

* Multi-dataset AI analytics
* Automated chart generation
* Advanced forecasting
* Customer segmentation
* Anomaly detection
* Automated business reports
* Reusable AI analytics engine

## 👨‍💻 Author

**Mangesh Shinde**

Built as an end-to-end portfolio project combining **Data Analytics, Business Intelligence, Full-Stack Development and Generative AI**.
