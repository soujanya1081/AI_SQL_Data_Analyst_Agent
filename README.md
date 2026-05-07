🤖AI SQL Data Analyst Agent An interactive web application built with Streamlit, LangChain, and Groq that allows users to upload CSV data and perform complex analysis using natural language. The agent translates your questions into SQL, executes them against a local SQLite database, and visualizes the results.

🚀Features CSV to SQLite: Automatically converts uploaded CSV files into a queryable SQL database.

Natural Language Querying: Uses Llama-3.1-8b (via Groq) to translate English questions into precise SQLite queries.

Multi-Statement Support: Can handle multiple questions at once and execute sequential SQL statements.

Automatic Visualization: Intelligently detects numeric data to generate bar or line charts using Plotly.

Chat History: Maintains context of the conversation within the session.

🛠️ Tech Stack Frontend: Streamlit LLM Orchestration: LangChain Inference Engine: Groq Cloud Database: SQLite & SQLAlchemy Data Visualization: Plotly Express

📋 Prerequisites Before running the application, ensure you have: Python 3.8 or higher installed.

A Groq API Key (Obtainable from the Groq Console).

⚙️ Installation & Setup Clone the repository: git clone https://github.com/your-username/ai-sql-analyst.git cd ai-sql-analyst

Create and activate a virtual environment: python -m venv venv

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Configure Environment Variables:
Create a .env file in the root directory and add your Groq API key:
Code snippet GROQ_API_KEY=your_groq_api_key_here

🖥️ Usage
Start the Streamlit server:
streamlit run app.py Upload Data: Drag and drop any CSV file (e.g., insurance.csv). Analyze: Type your question in the chat box. Example: "What is the average BMI for smokers vs non-smokers?" Example: "Show me a trend of charges by age and the total count of patients per region."

📂 Project Structure
app.py: The main Streamlit application logic.
requirements.txt: List of Python dependencies.
.env: (Ignored by git) Stores sensitive API credentials.
analysis_db.db: Local SQLite database generated at runtime.
⚠️ Important Notes Security: This tool executes AI-generated SQL. While it uses SQLite (local), always be cautious when providing LLMs with write/delete permissions in production environments.
