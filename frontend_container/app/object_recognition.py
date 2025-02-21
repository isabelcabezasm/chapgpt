
import sys
import requests
import argparse
import os
verbose = False

def get_find_cap_container_url() -> str:
    get_find_cap_container_url = os.environ.get("FIND_CAP_CONTAINER_URL")
    return get_find_cap_container_url

def log(message: str, force_log: bool = False) -> None:
    if verbose or force_log:
        print(message, file=sys.stderr)

def main():
    files = {'file': open('./caps_test_images/8.jpg', 'rb')}
    response = requests.post(get_find_cap_container_url(), files=files)
    print(response.text)
    
def search_for_a_cap_from_blob(image: bytes) -> list:
    files = {'file': image}
    response = requests.post(get_find_cap_container_url(), files=files)
    if response.status_code != 200:
        log(f"Error: {response.text}")
        return []
    return list(map(float, response.text.strip('[]').split(',')))

def search_for_a_cap(image_path: str) -> list:
    files = {'file': open(image_path, 'rb')}
    response = requests.post(get_find_cap_container_url(), files=files)
    return response.text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    args = parser.parse_args()
    main()