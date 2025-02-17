from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

import sys
import argparse

load_dotenv()

verbose = False

def log(message: str, force_log: bool = False) -> None:
    if verbose or force_log:
        print(message, file=sys.stderr)

def read_from_storage_and_save_in_cosmos(csv_file_path:Path, 
                                         only_brands:list = None, 
                                         only_caps:list = None):
    # Read CSV file 
    caps_csv = pd.read_csv(csv_file_path)
    print(caps_csv.head())


def main():
    read_from_storage_and_save_in_cosmos(csv_file_path="../db/sample.csv")    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    _ = parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")
    args = parser.parse_args()
    if args.verbose:
        verbose = True
    main()