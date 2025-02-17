from transformations import convert_image_to_base64_from_blob
from embeddings import get_embedding_from_blob
from storage import AzureStorageClient
from cap import Cap

from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import argparse
import sys






load_dotenv()

verbose = False

def log(message: str, force_log: bool = False) -> None:
    if verbose or force_log:
        print(message, file=sys.stderr)

def parse_image_name(image_name) -> tuple:
    # get brand_id and cap_num from image name
    path = image_name.split("/")

    try:
        (brand_id, cap_num)  = path[len(path)-1][:-4].split("-")
        # check if is a "chapón"
        if cap_num.lower().endswith("ch"):
            cap_num = cap_num[:-3]
        if not brand_id.isdigit() or not cap_num.isdigit():
            log(f"Invalid brand_id or cap_num in {image_name}")
    except ValueError:
        log(f"Error parsing brand_id and cap_num from {image_name}")

    return brand_id, cap_num


def read_from_storage_and_save_in_cosmos(csv_file_path:Path, 
                                         only_brands:list = None, 
                                         only_caps:list = None):
    # Read CSV file 
    caps_csv = pd.read_csv(csv_file_path)

    list_images = AzureStorageClient().list_blobs()

    for image in list_images:
        if image.name.endswith(".jpg"):            
            brand_id, cap_num = parse_image_name(image.name)
            if not brand_id or not cap_num:
                continue
            
            # in caps_csv, look for cap by brand and number
            cap_info = caps_csv[(caps_csv["NUM_MARCA"] == int(brand_id)) & (caps_csv["SUB_NUM"] == int(cap_num))]
            if cap_info.empty:
                log(f"Cap not found: {brand_id}-{cap_num}: {image.name}")
                continue

            image_bytes = AzureStorageClient().download_blob(image.name)            

            cap = Cap(
                id = str(cap_info["N_REG"].values[0]),                
                brand_id = int(cap_info["NUM_MARCA"].values[0]),
                brand = cap_info["MARCA"].values[0],
                brand_num = int(cap_info["SUB_NUM"].values[0]),
                type = str(cap_info["TIPO"].values[0]),
                brewery = str(cap_info["CERVECERA/PRODUCTOR"].values[0]),
                region = str(cap_info["PROVINCIA"].values[0]),
                country = str(cap_info["PAIS"].values[0]),
                path = image.name,
                embeddings = get_embedding_from_blob(image_bytes),
                base64=convert_image_to_base64_from_blob(image_bytes)
            )

            print(cap.path)


def main():
    read_from_storage_and_save_in_cosmos(csv_file_path="../db/chapas.csv")    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    _ = parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")
    args = parser.parse_args()
    if args.verbose:
        verbose = True
    main()