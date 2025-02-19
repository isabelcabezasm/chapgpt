from transformations import convert_image_to_base64_from_blob
from storage import AzureStorageClient

from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

from caps_common.cosmosdb import get_container, insert_cap
from caps_common.embeddings import get_embedding_from_blob
from caps_common.common import log
from caps_common.cap import Cap


load_dotenv()

def parse_image_name(image_name) -> tuple:
    # get brand_id and cap_num from image name
    path = image_name.split("/")

    try:
        (brand_id, cap_num)  = path[len(path)-1][:-4].split("-")
        assert brand_id
        assert cap_num
        
        # check if is a "chapón"
        if cap_num.lower().endswith("ch"):
            cap_num = cap_num[:-3]
        if not brand_id.isdigit() or not cap_num.isdigit():
            log(f"Invalid brand_id or cap_num in {image_name}")
    except ValueError:
        log(f"Error parsing brand_id and cap_num from {image_name}")
        return None, None
    return brand_id, cap_num


def read_from_storage_and_save_in_cosmos(csv_file_path:Path, 
                                         only_brands:list = None, 
                                         only_caps:list = None):
    # Read CSV file 
    caps_csv = pd.read_csv(csv_file_path)

    try:
        list_images = AzureStorageClient().list_blobs()
    except Exception as e:
        log(f"Failed to list blobs: {e}", force_log=True)
        return
    
    # create the cosmos db container client: 
    container = get_container()

    for image in list_images:
        try:
            if image.name.endswith(".jpg"):            
                brand_id, cap_num = parse_image_name(image.name)
                if not brand_id or not cap_num:
                    continue
                
                # in caps_csv, look for cap by brand and number
                cap_info = caps_csv[(caps_csv["NUM_MARCA"] == int(brand_id)) & (caps_csv["SUB_NUM"] == int(cap_num))]
                if cap_info.empty:
                    log(f"Cap not found: {brand_id}-{cap_num}: {image.name}")
                    continue

                if only_brands: # if only_brands is set, skip caps not in the list
                    if int(brand_id) not in only_brands:
                        continue
                if only_brands and only_caps: # if only_caps is set, skip caps not in the list
                    if int(cap_num) not in only_caps and int(brand_id) not in only_brands:
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

                # insert cap in cosmos
                insert_cap(cap, container)
        except Exception as e:          
            log(f"Failed inserting cap {image.name}. Error:{e}. ")
       
def main():
    read_from_storage_and_save_in_cosmos(csv_file_path="../db/chapas.csv")    


if __name__ == "__main__":
    main()