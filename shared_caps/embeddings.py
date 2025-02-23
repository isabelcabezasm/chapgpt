from shared_caps.common import log
import requests
import os


def get_embedding_container_url() -> str:
    get_embedding_container_url = os.environ.get("EMBEDDING_CONTAINER_URL")
    return get_embedding_container_url


def get_embedding_from_blob(image: bytes) -> list:
    files = {'file': image}
    response = requests.post(get_embedding_container_url(), files=files)
    if response.status_code != 200:
        log(f"Error getting embedding from blob: {response.status_code} - {response.text}")
        raise Exception(f"Error getting embedding from blob: {response.status_code} - {response.text}")
    return [float(x) for x in response.json()]
