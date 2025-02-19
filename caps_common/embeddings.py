import requests
import os




def get_embedding_from_blob(image: bytes) -> list:
    files = {'file': image}
    
    url = os.environ["EMBEDDING_CONTAINER_URL"]

    response = requests.post(url, files=files)
    return [float(x) for x in response.json()]