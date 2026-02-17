import argparse
import pandas as pd
from dotenv import load_dotenv
from LoaderClass.loaderCLass import PayerLoader

load_dotenv()

def prepare_dataframe(*args):
    data = args[0]

    # Case 1: File path
    if isinstance(data, str):
        return pd.read_csv(data)

    # Case 2: Manual list of dicts
    elif isinstance(data, list):
        if not all(isinstance(item, dict) for item in data):
            raise ValueError("List must contain dictionaries.")
        return pd.DataFrame(data)

    else:
        raise ValueError("Unsupported input type")


def process_dataframe(df, payer):

    # Payer-specific logic
    if payer.lower() == "anthem":
        df["claim_amount"] = df["claim_amount"] * 4.13

    # Convert columns to uppercase for Snowflake
    df.columns = df.columns.str.upper()

    return df

def main():

    parser = argparse.ArgumentParser(description="Multi-Source Payer Loader")

    parser.add_argument("--source")
    parser.add_argument(
        "--payer",
        choices=["anthem", "cigna", "manual"],
        required=True
    )

    args = parser.parse_args()

    # Manual hardcoded data
    if args.payer == "manual":
        manual_data = [
            {
                "member_id": "3",
                "claim_id": "M3",
                "claim_amount": 9000,
                "service_date": "2026-02-05",
                "payer_name": "MANUAL"
            }
        ]

        df = prepare_dataframe(manual_data)

    else:
        df = prepare_dataframe(args.source)

    df = process_dataframe(df, args.payer)

    loader = PayerLoader(args.payer)
    loader.load(df)


if __name__ == "__main__":
    main()
