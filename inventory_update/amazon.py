import json
import logging
from typing import Dict
from urllib import request


def upload_inventory(file_path: str, access_token: str, region: str) -> Dict:
    """Upload inventory file to Amazon Seller using SP API."""
    endpoint = f"https://sellingpartnerapi-{region}.amazon.com"
    document_url = f"{endpoint}/feeds/2021-06-30/documents"

    logging.info("Requesting document to upload inventory")
    document_payload = json.dumps(
        {"contentType": "text/tab-separated-values; charset=UTF-8"}
    ).encode()
    req = request.Request(
        document_url,
        data=document_payload,
        headers={
            "x-amz-access-token": access_token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=30) as resp:
        document_info = json.loads(resp.read().decode())
    upload_url = document_info["url"]

    logging.info("Uploading inventory file")
    with open(file_path, "rb") as file:
        file_data = file.read()
    req = request.Request(
        upload_url,
        data=file_data,
        headers={"Content-Type": "text/tab-separated-values; charset=UTF-8"},
        method="PUT",
    )
    with request.urlopen(req, timeout=30):
        pass

    feed_url = f"{endpoint}/feeds/2021-06-30/feeds"
    feed_payload = json.dumps(
        {
            "feedType": "POST_INVENTORY_AVAILABILITY_DATA",
            "marketplaceIds": ["ATVPDKIKX0DER"],
            "inputFeedDocumentId": document_info["feedDocumentId"],
        }
    ).encode()
    req = request.Request(
        feed_url,
        data=feed_payload,
        headers={
            "x-amz-access-token": access_token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=30) as resp:
        feed_response = json.loads(resp.read().decode())
    logging.info("Created feed %s", feed_response.get("feedId"))
    return feed_response
