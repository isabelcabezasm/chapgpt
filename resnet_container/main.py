from fastapi import FastAPI, File, UploadFile
import io
from embeddings import get_embeddings
from process_image import find_cap

app = FastAPI()


@app.post("/find_cap")
def extract_cap(file: UploadFile = File(...)) -> list[float]:
    image_data = file.file.read()
    bytes_data = io.BytesIO(image_data)
    return find_cap(bytes_data)

@app.post("/embed")
def process_image(file: UploadFile = File(...)) -> list[float]:
    image_data = file.file.read()
    # ...process the image...
    result = get_embeddings(io.BytesIO(image_data))
    return result
