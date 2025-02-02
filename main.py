import sqlite3
from openai import OpenAI 
import dotenv
import os

dotenv.load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"), 
)

model = "gpt-4o-mini"

# Full description of the database schema
DATABASE_SCHEMA = """
The 'sales' table contains the following columns:
- ORDERNUMBER (INTEGER)
- QUANTITYORDERED (INTEGER)
- PRICEEACH (FLOAT)
- ORDERLINENUMBER (INTEGER)
- SALES (FLOAT)
- ORDERDATE (DATE)
- STATUS (TEXT)
- QTR_ID (INTEGER)
- MONTH_ID (INTEGER)
- YEAR_ID (INTEGER)
- PRODUCTLINE (TEXT)
- MSRP (FLOAT)
- PRODUCTCODE (TEXT)
- CUSTOMERNAME (TEXT)
- PHONE (TEXT)
- ADDRESSLINE1 (TEXT)
- ADDRESSLINE2 (TEXT)
- CITY (TEXT)
- STATE (TEXT)
- POSTALCODE (TEXT)
- COUNTRY (TEXT)
- TERRITORY (TEXT)
- CONTACTLASTNAME (TEXT)
- CONTACTFIRSTNAME (TEXT)
- DEALSIZE (TEXT)
"""

# Main handler for user input
def handle_user_input(question):
    sql_query = generate_sql_query(question)
    result = query_sales(sql_query)
    
    if isinstance(result, list):  
        natural_language_response = interpret_sql_result(question, sql_query, result)
        return natural_language_response
    else:  # If there's an error message (e.g., SQL Error)
        return result

# Ask OpenAI to generate an SQL query based on the user's question and knowledge of the database schema
def generate_sql_query(question):
    prompt = f"""
    The following is the schema of the sales database:
    {DATABASE_SCHEMA}

    The database is a SQLite database called 'sales_data.db'.
    The user has asked the following question: "{question}"
    
    Based on this information, write an SQLlite query that answers the user's question.
    Only reply in valid SQLlite queries, do not add any commentary.
    Double-check that your SQL query is valid before replying with it.
    """
    
    chat_completion = client.chat.completions.create(
    messages=[
            {"role": "system", "content": "You are a helpful SQL assistant."},
            {"role": "user", "content": prompt},
        ],
    temperature=0.5,
    max_tokens=1000,
    model=model,
    
)
    clean_query = chat_completion.choices[0].message.content.strip().replace("```sql", "").replace("```", "").strip()
    print(f"\033[33mSQL Query (for debugging purposes):\n{clean_query}\033[0m")
    return(clean_query)


# Connect to the SQLite database and run the SQL query that was generated
def query_sales(query):
    try:
        conn = sqlite3.connect('sales_data.db')
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.OperationalError as e:
        return f"SQL Error: {e}"

# Ask OpenAI to interpret the SQL result in natural language (also providing the original user input for context) )
def interpret_sql_result(user_query, sql_query, result):
    result_str = "\n".join([str(row) for row in result]) if isinstance(result, list) else result
    print(f"\033[36mSQL Result (for debugging purposes):\n{result_str}\033[0m")
    
    prompt = f"""
    The following is the schema of the sales database:
    {DATABASE_SCHEMA}

    The user asked the following question: "{user_query}"

    The SQL query that was generated to answer this question is:
    {sql_query}

    The result of the SQL query is:
    {result_str}

    Based on this, provide a natural language response explaining the result to the user in a clear and concise way, without missing any important details. Please ensure to address the full intent of the user's question, even if some aspects were not directly handled by the SQL query. Do not mention SQL or the Query in the response, and keep it natural language.
    You don't need to remind the user that they can ask further questions, you can assume they understand how a chatbot works. Do not suggest anything to encourage the user to ask more questions.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that explains SQL query results."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=1000,
        model=model,
    )
    return chat_completion.choices[0].message.content.strip()


# Chatbot loop
def chatbot():
    print("Welcome to the Sales Chatbot! Ask me anything about the sales data.\nThis is an AI chatbot prototype and answers may not be correct at all times.\n\nType 'exit' or 'quit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye', '']:
            print("Goodbye!")
            break
        
        answer = handle_user_input(user_input)
        
        # Format the result for better display
        if isinstance(answer, list): 
            formatted_answer = "\n".join([str(row) for row in answer])
            print("Bot:", formatted_answer)
        else:
            print("Bot:", answer)

if __name__ == "__main__":
    chatbot()
