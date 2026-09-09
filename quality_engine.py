import pandas as pd
import numpy as np


# --------------------------------------------------
# Missing Value Check
# --------------------------------------------------

def check_missing_values(df):
    """
    Detect missing values in each column.
    """

    results = []
    total_rows = len(df)

    if total_rows == 0:
        return results

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        if missing_count > 0:

            missing_percentage = (
                missing_count / total_rows
            ) * 100

            if missing_percentage >= 5:
                severity = "CRITICAL"
            else:
                severity = "WARNING"

            results.append({
                "Check": "Missing Values",
                "Issue": f"Missing values in {column}",
                "Severity": severity,
                "Count": missing_count,
                "Percentage": round(missing_percentage, 2)
            })

    return results


# --------------------------------------------------
# Duplicate Check
# --------------------------------------------------

def check_duplicates(df):
    """
    Detect duplicate records in the dataset.
    """

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count == 0:
        return []

    duplicate_percentage = (
        duplicate_count / len(df)
    ) * 100

    if duplicate_percentage >= 5:
        severity = "CRITICAL"
    else:
        severity = "WARNING"

    return [{
        "Check": "Duplicate Records",
        "Issue": "Duplicate records",
        "Severity": severity,
        "Count": duplicate_count,
        "Percentage": round(duplicate_percentage, 2)
    }]


# --------------------------------------------------
# Outlier Check
# --------------------------------------------------

def check_outliers(df):
    """
    Detect numerical outliers using the IQR method.
    """

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    results = []

    for column in numeric_columns:
    # Avoid unreliable IQR detection on very small samples
        if df[column].dropna().count() < 10:
            continue

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        # If there is no variation, there cannot
        # be meaningful IQR-based outliers.
        if iqr == 0:
            continue

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = df[
            (df[column] < lower_bound) |
            (df[column] > upper_bound)
        ]

        outlier_count = len(outliers)

        if outlier_count > 0:

            outlier_percentage = (
                outlier_count / len(df)
            ) * 100

            if outlier_percentage >= 5:
                severity = "CRITICAL"
            else:
                severity = "WARNING"

            results.append({
                "Check": "Numerical Outliers",
                "Issue": f"Numerical outliers in {column}",
                "Severity": severity,
                "Count": outlier_count,
                "Percentage": round(
                    outlier_percentage,
                    2
                )
            })

    return results


# --------------------------------------------------
# Schema Validation
# --------------------------------------------------

def validate_schema(df, expected_schema):
    """
    Validate required columns, unexpected columns,
    and expected data types.
    """

    results = []

    # --------------------------------------------------
    # Check required columns
    # --------------------------------------------------

    for column in expected_schema:

        if column not in df.columns:

            results.append({
                "Check": "Schema Validation",
                "Issue": f"Missing required column: {column}",
                "Severity": "CRITICAL",
                "Count": 0,
                "Percentage": 0
            })


    # --------------------------------------------------
    # Check unexpected columns
    # --------------------------------------------------

    for column in df.columns:

        if column not in expected_schema:

            results.append({
                "Check": "Schema Validation",
                "Issue": f"Unexpected column: {column}",
                "Severity": "WARNING",
                "Count": 0,
                "Percentage": 0
            })


    # --------------------------------------------------
    # Check data types
    # --------------------------------------------------

    for column, expected_type in expected_schema.items():

        # Only check columns that actually exist
        if column not in df.columns:
            continue

        actual_type = str(df[column].dtype)

        if expected_type == "numeric":

            if not pd.api.types.is_numeric_dtype(
                df[column]
            ):

                results.append({
                    "Check": "Schema Validation",
                    "Issue": (
                        f"Invalid data type for {column}. "
                        f"Expected numeric, got {actual_type}"
                    ),
                    "Severity": "CRITICAL",
                    "Count": len(df),
                    "Percentage": 100
                })

    return results
# --------------------------------------------------
# Run All Quality Checks
# --------------------------------------------------

def run_quality_checks(df):
    """
    Run all available data-quality checks.
    """

    expected_schema = {
        "Customer_ID": "numeric",
        "Age": "numeric",
        "Annual_Income": "numeric",
        "Spending_Score": "numeric",
        "Purchase_Frequency": "numeric",
        "Transaction_Amount": "numeric"
    }

    issues = []

    issues.extend(
        check_missing_values(df)
    )

    issues.extend(
        check_duplicates(df)
    )

    issues.extend(
        check_outliers(df)
    )

    issues.extend(
        validate_schema(
            df,
            expected_schema
        )
    )

    return issues


# --------------------------------------------------
# Quality Score
# --------------------------------------------------

def calculate_quality_score(df, issues):
    """
    Calculate the overall data-quality score.
    """

    total_cells = df.shape[0] * df.shape[1]

    total_missing = int(
        df.isna().sum().sum()
    )

    total_duplicates = int(
        df.duplicated().sum()
    )

    missing_percentage = (
        total_missing / total_cells
    ) * 100 if total_cells > 0 else 0

    duplicate_percentage = (
        total_duplicates / len(df)
    ) * 100 if len(df) > 0 else 0

    outlier_issues = [
        issue
        for issue in issues
        if issue["Check"] == "Numerical Outliers"
    ]

    total_outliers = sum(
        issue["Count"]
        for issue in outlier_issues
    )

    outlier_percentage = (
        total_outliers / len(df)
    ) * 100 if len(df) > 0 else 0

    missing_penalty = min(
        missing_percentage,
        30
    )

    duplicate_penalty = min(
        duplicate_percentage,
        20
    )

    outlier_penalty = min(
        outlier_percentage,
        20
    )

    score = round(
        100
        - missing_penalty
        - duplicate_penalty
        - outlier_penalty
    )

    return max(0, score)


# --------------------------------------------------
# Check Summary
# --------------------------------------------------

def get_check_summary(issues):
    """
    Return a summary of the four quality checks.
    """

    all_checks = {
        "Missing Values",
        "Duplicate Records",
        "Numerical Outliers",
        "Schema Validation"
    }

    failed_checks = {
        issue["Check"]
        for issue in issues
    }

    passed_checks = (
        len(all_checks) - len(failed_checks)
    )

    critical_count = sum(
        1
        for issue in issues
        if issue["Severity"] == "CRITICAL"
    )

    warning_count = sum(
        1
        for issue in issues
        if issue["Severity"] == "WARNING"
    )

    return {
        "total_checks": len(all_checks),
        "passed_checks": passed_checks,
        "failed_checks": len(failed_checks),
        "critical_issues": critical_count,
        "warning_issues": warning_count
    }


# --------------------------------------------------
# Quality Gate
# --------------------------------------------------

def determine_quality_gate(issues):
    """
    Determine whether the dataset should pass,
    receive a warning, or be blocked.
    """

    critical_issues = [
        issue
        for issue in issues
        if issue["Severity"] == "CRITICAL"
    ]

    warning_issues = [
        issue
        for issue in issues
        if issue["Severity"] == "WARNING"
    ]

    if critical_issues:

        return {
            "status": "BLOCK",
            "message": (
                f"{len(critical_issues)} critical issue(s) "
                "must be resolved before downstream analysis."
            )
        }

    if warning_issues:

        return {
            "status": "WARNING",
            "message": (
                f"{len(warning_issues)} warning(s) detected. "
                "Review the dataset before using it."
            )
        }

    return {
        "status": "PASS",
        "message": (
            "No critical data-quality issues detected."
        )
    }