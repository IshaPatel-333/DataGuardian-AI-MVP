import streamlit as st
import pandas as pd
from ai_engine import generate_ai_analysis
from quality_engine import (
    run_quality_checks,
    get_check_summary,
    calculate_quality_score,
    determine_quality_gate
)


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="DataGuardian AI",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("DataGuardian AI")

st.write(
    "AI-assisted data quality monitoring "
    "and analysis."
)

st.divider()


# --------------------------------------------------
# File Upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a CSV dataset",
    type=["csv"]
)


# --------------------------------------------------
# Main Application
# --------------------------------------------------

if uploaded_file is not None:

    # Load dataset
    df = pd.read_csv(uploaded_file)


    # --------------------------------------------------
    # Dataset Overview
    # --------------------------------------------------

    st.subheader("Dataset Overview")

    total_rows = len(df)
    total_columns = len(df.columns)
    total_missing = int(
        df.isna().sum().sum()
    )
    total_duplicates = int(
        df.duplicated().sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Rows",
            f"{total_rows:,}"
        )

    with col2:
        st.metric(
            "Columns",
            f"{total_columns:,}"
        )

    with col3:
        st.metric(
            "Missing Values",
            f"{total_missing:,}"
        )

    with col4:
        st.metric(
            "Duplicate Rows",
            f"{total_duplicates:,}"
        )

    st.divider()


    # --------------------------------------------------
    # Run Quality Engine
    # --------------------------------------------------

    issues = run_quality_checks(df)
    
    summary = get_check_summary(issues)

    quality_score = calculate_quality_score(
        df,
        issues
    )

    gate = determine_quality_gate(
        issues
    )


    # --------------------------------------------------
    # Quality Checks Summary
    # --------------------------------------------------

    st.subheader("Data Quality Checks")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Critical",
            summary["critical_issues"]
        )

    with col2:
        st.metric(
            "Warnings",
            summary["warning_issues"]
        )

    with col3:
        st.metric(
            "Checks Passed",
            summary["passed_checks"]
        )


    # --------------------------------------------------
    # Issue Details
    # --------------------------------------------------

    if issues:

        issue_df = pd.DataFrame(
            issues
        )

        st.dataframe(
            issue_df,
            width='stretch'
        )

    else:

        st.success(
            "No data-quality issues detected."
        )


    st.divider()


    # --------------------------------------------------
    # Quality Gate
    # --------------------------------------------------

    st.subheader(
        "Data Quality Gate"
    )

    gate_col1, gate_col2 = st.columns(2)

    with gate_col1:

        st.metric(
            "Quality Score",
            f"{quality_score}/100"
        )

    with gate_col2:

        st.metric(
            "Gate Status",
            gate["status"]
        )

    st.info(
        gate["message"]
    )


    st.divider()


    # --------------------------------------------------
    # Issue Overview
    # --------------------------------------------------

    st.subheader(
        "Issues Detected"
    )

    missing_percentage = (
        total_missing /
        (total_rows * total_columns)
    ) * 100 if total_rows > 0 else 0

    duplicate_percentage = (
        total_duplicates /
        total_rows
    ) * 100 if total_rows > 0 else 0

    outlier_issues = [
        issue
        for issue in issues
        if issue["Check"] == "Numerical Outliers"
    ]

    total_outliers = sum(
        issue["Count"]
        for issue in outlier_issues
    )

    issue_col1, issue_col2, issue_col3 = st.columns(3)

    with issue_col1:

        st.metric(
            "Missing Values",
            f"{total_missing:,}"
        )

        st.caption(
            f"{missing_percentage:.2f}% of all cells"
        )

    with issue_col2:

        st.metric(
            "Duplicate Rows",
            f"{total_duplicates:,}"
        )

        st.caption(
            f"{duplicate_percentage:.2f}% of rows"
        )

    with issue_col3:

        st.metric(
            "Numerical Outliers",
            f"{total_outliers:,}"
        )


    st.divider()


    # --------------------------------------------------
    # Missing Values by Column
    # --------------------------------------------------

    st.subheader(
        "Missing Values by Column"
    )

    missing_by_column = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": (
            df.isna().sum().values
        ),
        "Missing %": (
            df.isna().mean().values * 100
        ).round(2)
    })

    missing_by_column = (
        missing_by_column[
            missing_by_column["Missing Values"] > 0
        ]
    )

    if not missing_by_column.empty:

        st.dataframe(
            missing_by_column,
            width='stretch'
        )

    else:

        st.success(
            "No missing values detected."
        )


    # --------------------------------------------------
    # Numerical Outliers
    # --------------------------------------------------

    st.subheader(
        "Numerical Outliers"
    )

    outlier_table = pd.DataFrame({
        "Column": [
            issue["Issue"]
            .replace(
                "Numerical outliers in ",
                ""
            )
            for issue in outlier_issues
        ],
        "Outlier Records": [
            issue["Count"]
            for issue in outlier_issues
        ]
    })

    if not outlier_table.empty:

        st.dataframe(
            outlier_table,
            width='stretch'
        )

    else:

        st.success(
            "No numerical outliers detected."
        )


    st.divider()

    # AI Business Impact Analysis

    st.subheader("AI Action Plan")
    st.write(
    "AI-generated impact assessment and recommended remediation.")
    if st.button("Analyze with Gemini"):

        with st.spinner("Analyzing data-quality findings..."):

            ai_result = generate_ai_analysis(
                issues,
                quality_score,
                gate["status"]
            )

        if "error" in ai_result:

            st.error(
                f"Gemini analysis failed: {ai_result['error']}"
            )

        else:

            st.session_state["ai_analysis"] = ai_result["analysis"]

            st.markdown(
                ai_result["analysis"]
            )

    # --------------------------------------------------
    # Download Quality Report
    # --------------------------------------------------

    report_lines = []

    report_lines.append("DATAGUARDIAN AI - DATA QUALITY REPORT")
    report_lines.append("=" * 50)
    report_lines.append("")

    report_lines.append(
        f"Quality Score: {quality_score}/100"
    )

    report_lines.append(
        f"Gate Status: {gate['status']}"
    )

    report_lines.append("")

    report_lines.append("DATASET SUMMARY")
    report_lines.append("-" * 30)

    report_lines.append(
        f"Rows: {total_rows}"
    )

    report_lines.append(
        f"Columns: {total_columns}"
    )

    report_lines.append(
        f"Missing Values: {total_missing}"
    )

    report_lines.append(
        f"Duplicate Rows: {total_duplicates}"
    )

    report_lines.append("")

    report_lines.append("QUALITY ISSUES")
    report_lines.append("-" * 30)

    if issues:

        for issue in issues:

            report_lines.append(
                f"[{issue['Severity']}] "
                f"{issue['Check']} - "
                f"{issue['Issue']} "
                f"(Count: {issue['Count']}, "
                f"{issue['Percentage']}%)"
            )

    else:

        report_lines.append(
            "No quality issues detected."
        )

    report_lines.append("")

    report_lines.append("GATE DECISION")
    report_lines.append("-" * 30)

    report_lines.append(
        gate["message"]
    )

    if "ai_analysis" in st.session_state:

        report_lines.append("")
        report_lines.append("AI ACTION PLAN")
        report_lines.append("-" * 30)
        report_lines.append(
            st.session_state["ai_analysis"]
        )

    report_content = "\n".join(report_lines)

    st.download_button(
        label="⬇Download Quality Report",
        data=report_content,
        file_name="dataguardian_quality_report.txt",
        mime="text/plain",
        width='stretch'
    )

    # --------------------------------------------------
    # Data Preview
    # --------------------------------------------------

    st.subheader(
        "Data Preview"
    )

    st.dataframe(
        df.head(10),
        width='stretch'
    )