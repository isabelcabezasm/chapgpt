import sys
from azure.identity import DefaultAzureCredential

def log(message: str) -> None:
    print(message, file=sys.stderr)


def credentials() -> DefaultAzureCredential:
    return DefaultAzureCredential()
