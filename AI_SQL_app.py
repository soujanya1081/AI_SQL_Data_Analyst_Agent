import os
import sqlite3
import re
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import plotly.express as px

# 1. --- CONFIGURATION ---
load_dotenv()
st.set_page_config(page_title="AI SQL  Data Analyst Agent", layout="wide", page_icon="📊")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = "llama-3.3-70b-versatile" 
DB_PATH = "analysis_db.db"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  
if "display_history" not in st.session_state:
    st.session_state.display_history = [] 

if not GROQ_API_KEY:
    st.error("🔑 API Key missing. Please check your .env file.")
    st.stop()

# 2. --- UTILITIES ---
def clean_code_text(text: str, language: str) -> str:
    pattern = rf"```{language.lower()}(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.replace(f"```{language.lower()}", "").replace("```", "").strip()

def execute_sql(sql_query: str):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df_res = pd.read_sql_query(sql_query, conn)
            return df_res, None
    except Exception as e:
        return None, str(e)

# 3. --- UI SETUP ---
st.title("📊 AI Executive Data Analyst")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("Step 1: Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df.to_sql("uploaded_table", engine, index=False, if_exists="replace")
    
    st.subheader("📋 Dataset Overview")
    st.dataframe(df.head(5), use_container_width=True)
    st.markdown("---")

    # Display History
    for chat in st.session_state.display_history:
        with st.chat_message(chat["role"]):
            st.success(chat["content"])
            res_col, log_col = st.columns([1, 1])
            with res_col:
                st.dataframe(chat["df"], use_container_width=True)
                if chat.get("fig"): st.plotly_chart(chat["fig"], use_container_width=True)
            with log_col:
                st.code(chat["sql"], language="sql")
                st.code(chat["py"], language="python")

    # --- CHAT LOGIC ---
    if prompt := st.chat_input("Ask a question (e.g., 'Compare customers with and without backup')..."):
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            try:
                llm = ChatGroq(model=MODEL_NAME, api_key=GROQ_API_KEY, temperature=0)

                # Send sample for context
                sample_data = df.head(2).to_dict() 
                
                code_prompt = (
                    f"Table: 'uploaded_table'. Columns: {list(df.columns)}\n"
                    f"Question: {prompt}\n\n"
                    "Output exactly: SQL: <sql> PYTHON: <pandas code using 'df'>. "
                    "For Python, DO NOT use plt.show(). Just provide the data transformation logic."
                )
                
                code_res = llm.invoke([("system", "Expert Coder."), ("user", code_prompt)]).content
                
                # Split and Clean
                sql_raw = code_res.split("PYTHON:")[0].replace("SQL:", "").strip()
                py_raw = code_res.split("PYTHON:")[1].strip() if "PYTHON:" in code_res else ""
                sql_code = clean_code_text(sql_raw, "sql")
                py_code = clean_code_text(py_raw, "python")

                # EXECUTE SQL
                df_result, err = execute_sql(sql_code)

                if err:
                    st.error(f"SQL Error: {err}")
                else:
                    # ANALYZE & INSIGHT
                    data_summary = df_result.head(5).to_string()
                    explanation = llm.invoke([
                        ("system", "Senior Analyst. Be brief and direct."),
                        ("user", f"Question: {prompt}\nResult Data:\n{data_summary}")
                    ]).content

                    # RENDER
                    st.subheader("💡 Analysis")
                    st.success(explanation)

                    res_col, log_col = st.columns([1, 1])
                    
                    fig = None
                    with res_col:
                        st.markdown("**🔍 Data Result**")
                        st.dataframe(df_result, use_container_width=True)
                        
                        # SMART PLOTTING (Replaces matplotlib)
                        if len(df_result) > 0:
                            num_cols = df_result.select_dtypes(include='number').columns
                            if not num_cols.empty:
                                x_ax = df_result.columns[0]
                                y_ax = num_cols[0]
                                fig = px.bar(df_result, x=x_ax, y=y_ax, title=f"{y_ax} by {x_ax}", template="plotly_white")
                                st.plotly_chart(fig, use_container_width=True)

                    with log_col:
                        st.markdown("**🛠️ Logic**")
                        st.code(sql_code, language="sql")
                        st.code(py_code, language="python")

                    # SAVE TO HISTORY
                    st.session_state.display_history.append({
                        "role": "assistant", "content": explanation, 
                        "df": df_result, "sql": sql_code, "py": py_code, "fig": fig
                    })

            except Exception as e:
                st.error(f"Error: {e}")