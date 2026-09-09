from google import genai
import streamlit as st


def generate_ai_analysis(issues, quality_score, gate_status):

    if not issues:
        return {
            "summary": "No significant data-quality issues were detected.",
            "business_impact": "The dataset is suitable for downstream analysis.",
            "recommendations": [
                "Continue monitoring data quality.",
                "Maintain the current validation rules."
            ]
        }

    issue_text = "\n".join(
        [
            f"- {issue['Check']}: "
            f"{issue['Issue']} | "
            f"Severity: {issue['Severity']} | "
            f"Count: {issue['Count']} | "
            f"Percentage: {issue['Percentage']}%"
            for issue in issues
        ]
    )

    prompt = f"""
You are a senior data quality engineer.

The Python validation engine has already detected the issues below.
Your job is to convert them into a SHORT, ACTIONABLE incident report.

Do NOT:
- repeat the full dataset analysis
- explain generic data-quality concepts
- discuss every possible downstream system
- invent issues
- change the severity
- provide long paragraphs

Quality Score: {quality_score}/100
Quality Gate: {gate_status}

Detected Issues:
{issue_text}

For EACH detected issue, provide:

1. Issue
2. Impact — ONE short sentence
3. Action — ONE concrete action

Then provide:

NEXT STEP — ONE sentence telling the engineer what to do next.

Keep the entire response under 180 words.

Use this format exactly:

DATA QUALITY SUMMARY
[One sentence describing the situation]

ISSUES TO FIX

1. [Issue]
Impact: [one sentence]
Action: [one concrete action]

2. [Issue]
Impact: [one sentence]
Action: [one concrete action]

NEXT STEP
[one sentence]
"""

    try:

        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {
            "analysis": response.text
        }

    except Exception as e:

        return {
            "error": str(e)
        }