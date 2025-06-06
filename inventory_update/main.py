import logging
import os

from .downloader import download_file
from .amazon import upload_inventory

logging.basicConfig(level=logging.INFO)


def main():
    api_url = os.environ.get("INVENTORY_API_URL")
    api_key = os.environ.get("INVENTORY_API_KEY")
    amazon_token = os.environ.get("AMAZON_SP_ACCESS_TOKEN")
    amazon_region = os.environ.get("AMAZON_REGION", "us-east-1")
    download_path = os.environ.get("DOWNLOAD_PATH", "inventory.csv")

    if not api_url or not api_key:
        raise SystemExit("INVENTORY_API_URL and INVENTORY_API_KEY must be set")
    if not amazon_token:
        raise SystemExit("AMAZON_SP_ACCESS_TOKEN must be set")

    file_path = download_file(api_url, api_key, download_path)
    upload_inventory(file_path, amazon_token, amazon_region)


if __name__ == "__main__":
    main()
