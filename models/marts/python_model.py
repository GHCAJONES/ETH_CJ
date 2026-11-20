import holidays
from snowflake.snowpark.types import (
    DateType,
    StringType,
    DoubleType,
    BooleanType,
    StructType,
    StructField,
)

def model(dbt, session):
    # NOTE: DataFrame.to_pandas() is not supported inside a Snowflake UDF
    # (it raises "255002: Optional dependency: 'pandas' is not installed" even
    # when pandas is present, because the connector's fetch_pandas_all path is
    # unavailable in the UDF context). So we fetch the rows with collect()
    # (which needs no pandas), flag French holidays in plain Python, and rebuild
    # the result as a Snowpark DataFrame.
    dbt.config(packages=["holidays"])
    df = dbt.ref("stablecoin_activity_per_day")

    # Build the holiday set once, not per row.
    french_holidays = holidays.France()
    rows = df.collect()

    new_rows = [
        (
            r["DATE"],
            r["TOKEN_ADDRESS"],
            r["TYPE"],
            r["SYMBOL"],
            r["TOTAL_USD_VALUE"],
            bool(r["DATE"] in french_holidays),
        )
        for r in rows
    ]

    schema = StructType(
        [
            StructField("DATE", DateType()),
            StructField("TOKEN_ADDRESS", StringType()),
            StructField("TYPE", StringType()),
            StructField("SYMBOL", StringType()),
            StructField("TOTAL_USD_VALUE", DoubleType()),
            StructField("IS_HOLIDAY", BooleanType()),
        ]
    )
    return session.createDataFrame(new_rows, schema=schema)
