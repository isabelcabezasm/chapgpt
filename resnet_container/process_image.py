import io
import sys
from uuid import uuid4
import torch
import argparse
from PIL import Image
import os

MODEL_DIRECTORY="yolo5_finetunned/yolo5_caps.pt"

def log(message: str, force_log: bool = False) -> None:
    if verbose or force_log:
        print(message, file=sys.stderr)


def find_cap(image_content: io.BytesIO) -> list[float]:
    # Find the bounding box of the cap
    # Load the YOLOv5 model from a .pt file
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_DIRECTORY)
    
    # Save image_content to disk and send the path to model
    temp_image_path = f"/tmp/{uuid4().hex}.jpg"
    with open(temp_image_path, "wb") as f:
        f.write(image_content.getbuffer())
    
    # Perform inference
    results = model(temp_image_path)

    # Clean up the temporary file
    os.remove(temp_image_path)

    # Perform inference
    if results:
        if results.pandas().xyxy[0].empty:
            log("No detections found.", force_log=True)
            return []
        max_conf_result = results.pandas().xyxy[0].iloc[results.pandas().xyxy[0]['confidence'].idxmax()]
        cap_bbox = [max_conf_result['xmin'], max_conf_result['ymin'], max_conf_result['xmax'], max_conf_result['ymax']]
        print(cap_bbox)
        return cap_bbox
    else:
        return []


def crop_image(image_path: str, bbox: list[int]) -> Image:
    directory = os.path.dirname(image_path)
    file_name = os.path.splitext(os.path.basename(image_path))[0]
    im = Image.open(image_path)
    im1 = im.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
    im1.save(directory +"/"+ uuid4().hex + file_name + "_cropped.jpg")
    return im1
    
        
def find_and_crop(image_path: str) -> Image:
    # Find the bounding box of the cap
    cap_bbox = find_cap(image_path)

    # Crop the image to the bounding box
    cap_image = crop_image(image_path, cap_bbox)

    return cap_image


def main(image_path: str) -> None:
    
    image = find_and_crop(image_path)
    image.show()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    _ = parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")
    _ = parser.add_argument("image_path", type=str, help="Path to the input image")
    
    args = parser.parse_args()
    if args.verbose:
        verbose = True
        
    main(args.image_path)
