import streamlit as st
import pandas as pd
import google.generativeai as genai

st.title("Auto Data Chatbot - Class 10")

try:
  key = st.secrets['gemini_api_key']
  genai.configure(api_key='AIzaSyBLFOfPKLSV6RnDM_IaMI_U_dCePNjD-20')
  model = genai.GenerativeModel('gemini-2.0-flash-lite')
  st.success("✅ Gemini model initialized.")
except Exception as e:
        st.error(f"Model init error:{e}")

@st.cache_data
def load_data():
    try:
        data_dict_url = "https://raw.githubusercontent.com/inarmprch/Chat_with_DB-HW/main/data_dict.csv"
        txn_url = "https://raw.githubusercontent.com/inarmprch/Chat_with_DB-HW/main/transactions.csv"
        df_dict = pd.read_csv(data_dict_url)
        df_txn = pd.read_csv(txn_url)
        return df_dict, df_txn
    except Exception as e:
        st.error(f"Error loading from GitHub:{e}")
        return None, None
      
df_dict, df_txn = load_csvs()
  if df_dict is not None and df_txn is not None:
    st.success("CSV data loaded from GitHub.")
    st.dataframe(df_txn.head(2))
  else:
    st.stop()
    
st.subheader("Ask a data question")
question = st.text_input("Your Question:")

if question and model:
  try:
    df_name = "df_txn"
    df_txn['date'] = pd.to_datetime(df_txn['date'], errors='coerce')
        data_dict_text = df_dict.to_string(index=False)
    example_record = df_txn.head(2).to_string(index=False)
    
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
    st.code(code_to_run, language='python')

    local_scope = {"df_txn": df_txn}
    exec(code_to_run, {}, local_scope)

    ANSWER = local_scope.get("ANSWER", "No ANSWER returned.")
        st.markdown(Execution Result")
        st.write(ANSWER)

explain_the_results = f'''
  The user asked: "{question}"

  Here is the result: {answer}

Summarize the answer and describe the persona/behavior of the customer based on the result.
'''
        explain_response = model.generate_content(explain_the_results)
        st.markdown("AI Explanation")
        st.write(explain_response.text)

response = model.generate_content(explain_the_results)

to_markdown(response.text)

except Exception as e:
  st.error(f'An error occurred {e}')
