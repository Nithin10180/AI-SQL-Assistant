import streamlit as st
from app import ask_ai
import pandas as pd
import ollama


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI SQL Analytics Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 AI SQL Assistant")

    st.write(
        "Natural Language → SQL → Analytics"
    )

    st.divider()

    st.subheader("💡 Sample Questions")

    st.write("Try asking:")

    st.code(
        "What is the total revenue?"
    )

    st.code(
        "What are the top 10 products by revenue?"
    )

    st.code(
        "Which countries generated the most revenue?"
    )

    st.code(
        "What is the monthly revenue?"
    )

    st.code(
        "Which products have the highest quantity sold?"
    )

    st.divider()

    st.subheader("🛠️ Technologies")

    st.write(
        """
        • Python
        • SQLite
        • Pandas
        • Ollama / Phi-3
        • Streamlit
        • SQL
        """
    )

    st.divider()

    st.caption(
        "AI-Powered Natural Language SQL Analytics"
    )


# ============================================================
# TITLE
# ============================================================

st.title(
    "🤖 AI SQL Analytics Assistant"
)

st.write(
    "Ask questions about your retail sales data in natural language."
)


# ============================================================
# AI BUSINESS ANSWER
# ============================================================

def generate_business_answer(question, result):

    prompt = f"""
You are a business data analyst.

Question:
{question}

Database result:
{result.to_string(index=False)}

Give a short business-friendly answer using only this result.
Mention the important numbers.
Do not invent information.
Keep the answer concise.
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

    return response["message"]["content"].strip()


# ============================================================
# USER QUESTION
# ============================================================

question = st.text_input(
    "Enter your question:",
    placeholder=(
        "Example: What are the top 5 countries by total revenue?"
    )
)


# ============================================================
# RUN QUERY
# ============================================================

if st.button("Run Query"):

    if not question:

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Generating SQL and analyzing data..."
        ):

            sql, result, message = ask_ai(
                question
            )


        # ====================================================
        # VALIDATION
        # ====================================================

        st.subheader(
            "🔐 Validation"
        )

        if message == "SQL is valid.":

            st.success(message)

        else:

            st.error(message)


        # ====================================================
        # GENERATED SQL
        # ====================================================

        st.subheader(
            "🧠 Generated SQL"
        )

        st.code(
            sql,
            language="sql"
        )


        # ====================================================
        # DATABASE RESULT
        # ====================================================

        if isinstance(
            result,
            pd.DataFrame
        ):

            st.subheader(
                "📊 Database Result"
            )

            st.dataframe(
                result,
                use_container_width=True
            )


            # =================================================
            # SMART VISUALIZATION
            # =================================================

            st.subheader(
                "📈 Visualization"
            )


            # -------------------------------------------------
            # SINGLE VALUE
            # -------------------------------------------------

            if (
                len(result.columns) == 1
                and len(result) == 1
            ):

                value = result.iloc[0, 0]

                st.metric(
                    label=result.columns[0],
                    value=(
                        f"{value:,.2f}"
                        if isinstance(
                            value,
                            (int, float)
                        )
                        else value
                    )
                )


            # -------------------------------------------------
            # TWO OR MORE COLUMNS
            # -------------------------------------------------

            elif len(result.columns) >= 2:

                x_column = result.columns[0]

                y_column = result.columns[1]

                chart_data = result.set_index(
                    x_column
                )


                # ---------------------------------------------
                # TIME SERIES
                # ---------------------------------------------

                if (
                    "month" in x_column.lower()
                    or "date" in x_column.lower()
                ):

                    st.line_chart(
                        chart_data[y_column]
                    )


                # ---------------------------------------------
                # CATEGORY DATA
                # ---------------------------------------------

                else:

                    st.bar_chart(
                        chart_data[y_column]
                    )


            # -------------------------------------------------
            # FALLBACK
            # -------------------------------------------------

            else:

                st.dataframe(
                    result,
                    use_container_width=True
                )


            # =================================================
            # AI BUSINESS INSIGHT
            # =================================================

            st.subheader(
                "💡 AI Business Insight"
            )

            with st.spinner(
                "Generating business insight..."
            ):

                answer = generate_business_answer(
                    question,
                    result
                )

            st.info(answer)


        # ====================================================
        # ERROR
        # ====================================================

        else:

            if result is not None:

                st.error(result)

            else:

                st.error(message)