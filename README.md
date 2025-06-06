# Ecommerce Inventory Update

This project provides a small example of automating inventory updates. It downloads inventory files from a custom API and uploads them to an Amazon Seller account using the Amazon Selling Partner API (SP API).

## Setup

1. Export the required environment variables:

- `INVENTORY_API_URL` - URL to fetch the inventory file
- `INVENTORY_API_KEY` - API key used for authentication when downloading the file
- `AMAZON_SP_ACCESS_TOKEN` - Selling Partner API access token
- `AMAZON_REGION` - Amazon region (defaults to `us-east-1`)
- `DOWNLOAD_PATH` - Path to store the downloaded file (defaults to `inventory.csv`)

## Running

Execute the inventory update script with Python:

```bash
python -m inventory_update.main
```

The script will download the inventory file and upload it to Amazon.
