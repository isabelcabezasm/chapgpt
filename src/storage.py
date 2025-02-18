from azure.storage.blob import BlobServiceClient, ContainerClient
import os


def service_client() -> BlobServiceClient:    
    # create blob service from connection string
    return BlobServiceClient.from_connection_string(
        conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    )

def container_client(
        container: str | None = None
) -> ContainerClient:
    return service_client().get_container_client(container or os.environ["IMAGES_CONTAINER_NAME"])

class AzureStorageClient:
    def __init__(self):
        self.container_client = container_client()

    def list_blobs(self, limit=10) -> list:
        try:
            return self.container_client.list_blobs(results_per_page=limit)
        except Exception as e:
            logging.error(f"Error listing blobs: {e}")
    def download_blob(self, blob: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob)
        return blob_client.download_blob().readall()