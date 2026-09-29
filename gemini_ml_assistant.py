import os
import json
import pandas as pd
from google import genai

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = "your_dataset.csv"
ML_GOAL = "Predict the target variable in this dataset"
MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# GEMINI CLIENT
# ============================================================

def create_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Set it in your environment before running."
        )

    return genai.Client(api_key=api_key)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError("Dataset is empty.")

    return df


# ============================================================
# DATASET PROFILE
# ============================================================

def create_dataset_profile(df):
    profile = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            column: int(value)
            for column, value in df.isna().sum().items()
            if value > 0
        },
        "unique_values": {
            column: int(df[column].nunique())
            for column in df.columns
        }
    }

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    profile["numeric_summary"] = {}

    for column in numeric_columns:
        profile["numeric_summary"][column] = {
            "mean": float(df[column].mean()),
            "median": float(df[column].median()),
            "min": float(df[column].min()),
            "max": float(df[column].max())
        }

    return profile


# ============================================================
# GEMINI ML ANALYSIS
# ============================================================

def generate_ml_analysis(client, profile, ml_goal):
    prompt = f"""
You are an experienced Machine Learning Engineer.

Analyze this dataset profile and ML goal.

ML GOAL:
{ml_goal}

DATASET PROFILE:
{json.dumps(profile, indent=2)}

Provide:

1. Problem type
2. Recommended target column
3. Feature engineering
4. Data preprocessing
5. Train/test strategy
6. Three suitable ML algorithms
7. Evaluation metrics
8. Data leakage risks
9. End-to-end ML workflow

IMPORTANT:
- Use only columns present in the profile.
- Do not invent columns.
- If the target cannot be identified, clearly say so.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


# ============================================================
# GEMINI CODE GENERATION
# ============================================================

def generate_ml_code(client, profile, ml_goal):
    prompt = f"""
You are a senior Python Machine Learning Engineer.

Generate a clean ML training script using pandas and scikit-learn.

ML GOAL:
{ml_goal}

DATASET PROFILE:
{json.dumps(profile, indent=2)}

Requirements:
- Do not invent column names.
- Identify the target only if possible.
- Include preprocessing.
- Avoid data leakage.
- Use train_test_split when appropriate.
- Train at least two suitable models.
- Evaluate with appropriate metrics.
- Print model results.
- Keep the code readable.
- Return ONLY Python code.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    code = response.text.strip()

    if code.startswith("```python"):
        code = code[len("```python"):].strip()

    if code.startswith("```"):
        code = code[len("```"):].strip()

    if code.endswith("```"):
        code = code[:-3].strip()

    return code


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("GEMINI ML ASSISTANT")
    print("=" * 60)

    print("\nLoading dataset...")
    df = load_dataset(DATASET_PATH)

    print(
        f"Dataset loaded: {df.shape[0]} rows, "
        f"{df.shape[1]} columns"
    )

    print("\nCreating dataset profile...")
    profile = create_dataset_profile(df)

    print("\nConnecting to Gemini...")
    client = create_gemini_client()

    print("\nGenerating ML analysis...")
    analysis = generate_ml_analysis(
        client,
        profile,
        ML_GOAL
    )

    print("\n" + "=" * 60)
    print("GEMINI ML ANALYSIS")
    print("=" * 60)
    print(analysis)

    choice = input(
        "\nGenerate ML training code too? (y/n): "
    ).strip().lower()

    if choice == "y":
        print("\nGenerating ML training code...")

        ml_code = generate_ml_code(
            client,
            profile,
            ML_GOAL
        )

        output_file = "generated_ml_model.py"

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(ml_code)

        print(f"ML code saved to: {output_file}")


if __name__ == "__main__":
    main()
