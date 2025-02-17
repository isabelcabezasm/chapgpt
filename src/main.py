from dotenv import load_dotenv
import sys
import argparse

load_dotenv()

verbose = False

def log(message: str, force_log: bool = False) -> None:
    if verbose or force_log:
        print(message, file=sys.stderr)

def read_from_storage_and_save_in_cosmos(only_brands:list=None, only_caps:list=None):

    csv_file = "/db/sample.csv"


def main():
    read_from_storage_and_save_in_cosmos()    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to create a embedding from a image")
    _ = parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")
    args = parser.parse_args()
    if args.verbose:
        verbose = True
    main()