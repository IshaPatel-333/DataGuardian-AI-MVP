import sqlite3
import pandas as pd


def run_sql_quality_checks(df):
    """
    Run SQL-based data quality checks using SQLite.
    Returns dataset-level health metrics.
    """

    connection = sqlite3.connect(":memory:")

    try:
        # Load dataframe into an in-memory SQL table
        df.to_sql(
            "dataset",
            connection,
            index=False,
            if_exists="replace"
        )

        # Row count

        row_count_query = """
        SELECT COUNT(*) AS row_count
        FROM dataset
        """

        row_count = int(
            pd.read_sql_query(
                row_count_query,
                connection
            ).iloc[0]["row_count"]
        )
        # Missing cell count

        null_expressions = " + ".join(
            [
                f'SUM(CASE WHEN "{column}" IS NULL THEN 1 ELSE 0 END)'
                for column in df.columns
            ]
        )

        missing_query = f"""
        SELECT
            {null_expressions} AS total_missing
        FROM dataset
        """

        missing_result = pd.read_sql_query(
            missing_query,
            connection
        )

        total_missing = int(
            missing_result.iloc[0]["total_missing"]
        )

        # Duplicate row count

        column_list = ", ".join(
            [f'"{column}"' for column in df.columns]
        )

        duplicate_query = f"""
        SELECT COUNT(*) - COUNT(DISTINCT
            {column_list}
        ) AS duplicate_count
        FROM dataset
        """

        # SQLite does not support COUNT(DISTINCT col1, col2...)
        # consistently across versions, so use a grouped query.

        duplicate_query = f"""
        SELECT COALESCE(SUM(duplicate_group_count - 1), 0)
        AS duplicate_count
        FROM (
            SELECT COUNT(*) AS duplicate_group_count
            FROM dataset
            GROUP BY {column_list}
            HAVING COUNT(*) > 1
        )
        """

        duplicate_result = pd.read_sql_query(
            duplicate_query,
            connection
        )

        duplicate_count = int(
            duplicate_result.iloc[0]["duplicate_count"]
        )

        # SQL health metrics

        total_cells = row_count * len(df.columns)

        missing_percentage = (
            (total_missing / total_cells) * 100
            if total_cells > 0
            else 0
        )

        duplicate_percentage = (
            (duplicate_count / row_count) * 100
            if row_count > 0
            else 0
        )

        return {
            "row_count": row_count,
            "column_count": len(df.columns),
            "total_missing": total_missing,
            "missing_percentage": round(
                missing_percentage,
                2
            ),
            "duplicate_count": duplicate_count,
            "duplicate_percentage": round(
                duplicate_percentage,
                2
            )
        }

    finally:
        connection.close()