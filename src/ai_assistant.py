from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def analyze_quality_report(
    summary_df,
    validation_df
):
    summary_text = summary_df.to_string(index=False)
    validation_text = validation_df.to_string(index=False)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
        {

            "role": "system",

            "content": """

                        You are a Senior Data Quality Architect.

                        Analyze data quality reports.

                        Provide:

                        1. Executive Summary

                        2. Root Causes

                        3. Business Impact

                        4. Recommendations

                        Keep answers concise and structured.

                        """

        },
        {
            "role": "user",
            "content": f"Analyze the following data quality report summary:\n{summary_text}\n\nAnd the validation details:\n{validation_text}"
        }
    ]
)
    return response.choices[0].message.content

def save_ai_analysis(text):
    with open("reports/ai_analysis.txt", "w") as file:
        file.write(text)

