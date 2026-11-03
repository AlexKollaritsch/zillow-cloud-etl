import requests
import os
import boto3
from datetime import datetime, timezone

YEAR = datetime.now(timezone.utc).year

GAZ_URL = (
    f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
    f"{YEAR}_Gazetteer/{YEAR}_Gaz_place_national.zip"
)

BUCKET = "zillow-data-lake-alex"

def download_gazetteer():
    print("Downloading Gazetteer data...")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"Gaz_place_national_{timestamp}.zip"

    with requests.get(GAZ_URL, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"Saved locally as {filename}")
    return filename

def upload_to_s3(filename):
    print(f"Uploading {filename} to S3...")
    s3 = boto3.client("s3")

    key = f"bronze/gazetteer/live/{filename}"
    s3.upload_file(filename, BUCKET, key)
    print(f"Uploaded to s3://{BUCKET}/{key}")

def main():
    filename = download_gazetteer()
    upload_to_s3(filename)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()