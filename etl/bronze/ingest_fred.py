import os
import time
import json
import requests
import boto3
from datetime import datetime, timezone

FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_API_BASE = "https://api.stlouisfed.org/fred/series/observations"
BUCKET = "zillow-data-lake-alex"

SERIES = {
    "FEDFUNDS": "fed_funds",
    "MORTGAGE30US": "mortgage_rate",
    "CPIAUCSL": "cpi_all",
    "CPILFESL": "cpi_core"
}

def fetch_fred_json(url, retries=5, delay=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"FRED API error ({e}). Retrying {attempt+1}/{retries}...")
            time.sleep(delay)
    raise RuntimeError("FRED API failed after multiple retries.")

def download_fred_series(series_id: str):
    if FRED_API_KEY is None:
        raise RuntimeError("FRED_API_KEY not found. Cannot run live macro ingestion.")

    url = (
        f"{FRED_API_BASE}"
        f"?series_id={series_id}"
        f"&api_key={FRED_API_KEY}"
        f"&file_type=json"
    )

    print(f"Downloading FRED series {series_id}...")
    data = fetch_fred_json(url)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{series_id}_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f)

    print(f"Saved locally as {filename}")
    return filename

def upload_to_s3(filename):
    print(f"Uploading {filename} to S3...")
    s3 = boto3.client("s3")

    key = f"bronze/fred/live/{filename}"
    s3.upload_file(filename, BUCKET, key)

    print(f"Uploaded to s3://{BUCKET}/{key}")

def main():
    for series_id, name in SERIES.items():
        filename = download_fred_series(series_id)
        upload_to_s3(filename)

    print("FRED ingestion complete.")

if __name__ == "__main__":
    main()