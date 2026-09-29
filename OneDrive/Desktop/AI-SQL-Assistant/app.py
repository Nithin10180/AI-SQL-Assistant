import ollama
import sqlite3
import pandas as pd
import re


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = sqlite3.connect(
    "retail_analytics.db",
    check_same_thread=False
)


# ============================================================
# DATABASE SCHEMA
# ============================================================

schema = """
Table: sales

Columns:
Invoice
StockCode
Description
Quantity
InvoiceDate
Price
"Customer ID"
Country
Revenue
"""


# ============================================================
# GENERATE SQL USING OLLAMA
# ============================================================

def generate_sql(question):

    prompt = f"""
You are an expert SQLite SQL generator.

Convert the user's question into ONE valid SQLite SELECT query.

Database schema:
{schema}

IMPORTANT RULES:

1. Use ONLY the sales table.
2. Use ONLY the columns listed in the schema.
3. The column "Customer ID" contains a space.
4. ALWAYS write "Customer ID" with double quotes.
5. Generate valid SQLite SQL.
6. Return ONLY the SQL query.
7. Do not explain the query.
8. Generate ONLY ONE SQL statement.
9. Only SELECT queries are allowed.
10. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
    REPLACE, or PRAGMA.
11. Do not invent tables or columns.

Example:

SELECT "Customer ID", AVG(Revenue) AS AverageRevenue
FROM sales
GROUP BY "Customer ID";

User question:
{question}
"""

    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    sql = response["message"]["content"].strip()

    # Remove markdown code fences
    sql = re.sub(
        r"```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```\s*",
        "",
        sql
    )

    return sql.strip()


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):

    sql = sql.strip()

    sql_upper = sql.upper()

    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # Only one SQL statement
    if ";" in sql[:-1]:
        return False, "Multiple SQL statements are not allowed."

    # Check tables
    tables = re.findall(
        r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
        sql,
        flags=re.IGNORECASE
    )

    for table in tables:

        if table.lower() != "sales":

            return False, (
                f"Unauthorized table detected: {table}"
            )

    # Forbidden SQL commands
    forbidden = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "PRAGMA"
    ]

    for command in forbidden:

        pattern = rf"\b{command}\b"

        if re.search(
            pattern,
            sql_upper
        ):

            return False, (
                f"Forbidden SQL command detected: {command}"
            )

    return True, "SQL is valid."


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    try:

        result = pd.read_sql(
            sql,
            conn
        )

        return result

    except Exception as e:

        return f"SQL Error: {e}"


# ============================================================
# COMPLETE AI → SQL → DATABASE PIPELINE
# ============================================================

def ask_ai(question):

    # Generate SQL
    sql = generate_sql(question)

    # Validate SQL
    valid, message = validate_sql(sql)

    if not valid:

        return sql, None, message

    # Execute SQL
    result = execute_sql(sql)

    # Handle execution error
    if isinstance(result, str):

        return sql, None, result

    return sql, result, message


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = (
        "What are the top 5 countries by total revenue?"
    )

    sql, result, message = ask_ai(
        question
    )

    print("\n=== GENERATED SQL ===")
    print(sql)

    print("\n=== VALIDATION ===")
    print(message)

    print("\n=== DATABASE RESULT ===")

    if isinstance(
        result,
        pd.DataFrame
    ):

        print(
            result.to_string(
                index=False
            )
        )

    else:

        print(result)