from cap import Cap
from embeddings import get_embedding_from_blob
from cosmosdb import search_similar_caps
from object_recognition import search_for_a_cap_from_blob

from streamlit.runtime.uploaded_file_manager import UploadedFile
from PIL import Image
import io

class UserImage():
    file_id: str
    name: str
    type: str
    size: int
    file_urls: dict[str, str]

def search_the_cap_in_the_image(image: UploadedFile) -> list[int]:
    # first find the cap with yolo    
    image_content = image.read()
    result = [int(x) for x in search_for_a_cap_from_blob(image_content)]
    return result

def search_similar_caps_cropped_cap(image: Image) -> list[Cap]:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    image_content = buffered.getvalue()
    similar_caps = search_similar_caps(get_embedding_from_blob(image_content))
    return similar_caps