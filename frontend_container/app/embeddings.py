from common import log
import requests
import argparse
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


def get_embedding(image_path: str) -> list:
    files = {'file': open(image_path, 'rb')}
    response = requests.post(get_embedding_container_url(), files=files)
    return [float(x) for x in response.json()]


def main():
    files = {'file': open('./src/alhambra_1925_barcode_db.jpg', 'rb')}
    response = requests.post(get_embedding_container_url(), files=files)
    embedding = response.json()["embedding"]
    print([float(x) for x in embedding])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    args = parser.parse_args()
    main()