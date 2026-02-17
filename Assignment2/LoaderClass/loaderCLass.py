import os
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

class BaseLoader:
    def load(self, df):
        pass


class PayerLoader(BaseLoader):

    def __init__(self, payer):
        self.payer = payer.lower()
        self.table_map = {
            "anthem": "ANTHEM",
            "cigna": "CIGNA",
            "manual": "GENERIC_CLAIMS"
        }

    def load(self, df):

        table_name = self.table_map.get(self.payer)

        if not table_name:
            raise ValueError("Invalid payer")

        print("Connecting to Snowflake...")

        conn = snowflake.connector.connect(
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            account=os.getenv("ACCOUNT"),
            warehouse=os.getenv("WAREHOUSE"),
            database=os.getenv("DATABASE"),
            schema=os.getenv("SCHEMA"),
        )

        try:
            cursor = conn.cursor()

            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                MEMBER_ID STRING,
                CLAIM_ID STRING,
                CLAIM_AMOUNT FLOAT,
                SERVICE_DATE DATE,
                PAYER_NAME STRING,
                INGESTION_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """

            cursor.execute(create_table_sql)

            print(f"Loading data into {os.getenv('DATABASE')}.{os.getenv('SCHEMA')}.{table_name}")

            # write_pandas returns 4 values
            success = write_pandas(conn, df, table_name)

            if success:
                print(f"Loaded rows into {table_name} ✅")
            else:
                print("Load failed ❌")

        finally:
            conn.close()
            print("Connection closed.")


