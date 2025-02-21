from io import BytesIO
import base64

def convert_image_to_base64_from_blob(image: bytes) -> str:
    image_data = BytesIO(image)
    base64_string = base64.b64encode(image_data.getvalue()).decode("utf-8")
    return base64_string