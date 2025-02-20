
import sys
import requests
import argparse

verbose = False

url = 'http://embeddings:8080/find_cap'

def log(message: str, force_log: bool = False) -> None:
    if verbose or force_log:
        print(message, file=sys.stderr)

def main():
    files = {'file': open('./caps_test_images/8.jpg', 'rb')}
    response = requests.post(url, files=files)
    print(response.text)
    
def search_for_a_cap_from_blob(image: bytes) -> list:
    files = {'file': image}
    response = requests.post(url, files=files)
    if response.status_code != 200:
        log(f"Error: {response.text}")
        return []
    return list(map(float, response.text.strip('[]').split(',')))

def search_for_a_cap(image_path: str) -> list:
    files = {'file': open(image_path, 'rb')}
    response = requests.post(url, files=files)
    return response.text

if __name__ == "__main__":
    # send a file to the http://embeddings:8080/embed endpoint via post
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    _ = parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")
    args = parser.parse_args()
    if args.verbose:
        verbose = True
    main()