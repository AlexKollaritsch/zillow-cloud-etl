import os
import requests
import boto3
from datetime import datetime
from botocore.config import Config

ZILLOW_URL = "https://files.zillowstatic.com/research/public_csvs/zhvi/City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
BUCKET = "zillow-data-lake-alex"

def download_zillow():
    print("Downloading Zillow ZHVI data...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"City_zhvi_{timestamp}.csv"

    with requests.get(ZILLOW_URL, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"Saved locally as {filename}")
    return filename

def upload_to_s3(filename):
    print(f"Uploading {filename} to S3...")
    s3 = boto3.client(
        "s3",
        config=Config(
            multipart_chunksize=8 * 1024 * 1024,
            max_concurrency=1
        )
    )

    key = f"bronze/zhvi/live/{filename}"
    s3.upload_file(filename, BUCKET, key)
    print(f"Uploaded to s3://{BUCKET}/{key}")

def main():
    filename = download_zillow()
    upload_to_s3(filename)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()