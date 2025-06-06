import logging
from urllib import request, error


def download_file(api_url: str, api_key: str, dest_path: str) -> str:
    """Download an inventory file from a remote API."""
    headers = {"Authorization": f"Bearer {api_key}"}
    logging.info("Downloading inventory from %s", api_url)
    req = request.Request(api_url, headers=headers)
    try:
        with request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except error.HTTPError as exc:
        logging.error("Download failed: %s", exc)
        raise
    with open(dest_path, "wb") as file:
        file.write(data)
    logging.info("Saved inventory to %s", dest_path)
    return dest_path
