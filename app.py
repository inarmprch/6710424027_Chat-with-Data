import streamlit as st
import pandas as pd
import google.generativeai as genai

# ตั้งค่า Gemini API Key
try:
  key = st.secrets['gemini_api_key']
  genai.configure(api_key='AIzaSyBLFOfPKLSV6RnDM_IaMI_U_dCePNjD-20')
  model = genai.GenerativeModel('gemini-2.0-flash-lite')
  st.success("✅ Gemini model initialized.")
except Exception as e:
  st.error(f'Failed to configure Gemini API: {e}')
  st.stop()

# ตั้งชื่อแอป
st.title("Auto Data Chatbot - Class 10")
st.caption("Use preloaded data or upload your own CSV to ask AI-powered questions!")

# ส่วนใช้ไฟล์ที่มีให้
def load_data_from_github():
    try:
        data_dict_url = "https://raw.githubusercontent.com/inarmprch/Chat_with_DB-HW/main/data_dict.csv"
        txn_url = "https://raw.githubusercontent.com/inarmprch/Chat_with_DB-HW/main/transactions.csv"
        df_dict = pd.read_csv(data_dict_url)
        df_txn = pd.read_csv(txn_url)
        return df_dict, df_txn
    except Exception as e:
        st.error(f"❌ Failed to load GitHub CSVs: {e}")
        return None, None

# เลือกต้นทางข้อมูล
st.subheader("Choose your data source")
use_github_data = st.radio("Select data input option:", ["Use GitHub CSVs", "Upload CSV files"])

df_dict, df_txn = None, None

if use_github_data == "Use GitHub CSVs":
    df_dict, df_txn = load_data_from_github()
else:
    uploaded_dict = st.file_uploader("Upload data_dict.csv", type="csv")
    uploaded_txn = st.file_uploader("Upload transactions.csv", type="csv")
    if uploaded_dict and uploaded_txn:
        try:
            df_dict = pd.read_csv(uploaded_dict)
            df_txn = pd.read_csv(uploaded_txn)
            st.success("✅ Uploaded files successfully.")
        except Exception as e:
            st.error(f"❌ File upload error: {e}")

# แสดงตัวอย่างไฟล์
if df_dict is not None and df_txn is not None:
    st.write("### 🧾 Data Dictionary Preview")
    st.dataframe(df_dict.head())

    st.write("### 📊 Transactions Preview")
    st.dataframe(df_txn.head(2))
else:
    st.info("Please load data to continue.")
    st.stop()

# รับข้อความจากผู้ใช้
st.subheader("Ask a data question 💬")
question = st.text_input("Your Question:")

if question and model:
    try:
        df_name = "df_txn"
        df_txn['date'] = pd.to_datetime(df_txn['date'], errors='coerce')
        data_dict_text = df_dict.to_string(index=False)
        example_record = df_txn.head(2).to_string(index=False)

        # 🔮 Prompt for Code Generation
        prompt = f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question
and the provided DataFrame information.

Here's the context:
**User Question:**
{question}
**DataFrame Name:**
{df_name}
**DataFrame Details:**
{data_dict_text}
**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. **Crucially, use the `exec()` function to execute the generated code.**
3. Do not import pandas
4. Change date column type to datetime
5. **Store the result of the executed code in a variable named `ANSWER`.**
This variable should hold the answer to the user's question (e.g., a filtered DataFrame, a calculated value, etc.).
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`. Do not include code to load the DataFrame.
7. Keep the generated code concise and focused on answering the question.
8. If the question requires a specific output format (e.g., a list, a single value), ensure the `ANSWER` variable holds that format.
"""

        response = model.generate_content(prompt)
        code_to_run = response.text.replace("```python", "").replace("```", "")
        st.markdown("### 🧠 Generated Code")
        st.code(code_to_run, language="python")

        # 🧪 Execute generated code
        local_scope = {"df_txn": df_txn}
        exec(code_to_run, {}, local_scope)

        # 🎯 Get the result
        ANSWER = local_scope.get("ANSWER", "No ANSWER returned.")
        st.markdown("### ✅ Execution Result")
        st.write(ANSWER)

        # 📖 Explanation
        explain_prompt = f'''
The user asked: "{question}"

Here is the result: {ANSWER}

Summarize the answer and describe the persona/behavior of the customer based on the result.
'''
        explain_response = model.generate_content(explain_prompt)
        st.markdown("### 🤖 Gemini's Explanation")
        st.write(explain_response.text)

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
