
import os
from azure.cosmos import CosmosClient, exceptions, ContainerProxy

from cap import Cap
import common

# create type called Container that wrapps a ContainerProxy
Container = ContainerProxy

def get_cosmos_client():
    try:
        account_name = os.getenv('COSMOS_ACCOUNT_NAME')
        client = CosmosClient(f"https://{account_name}.documents.azure.com:443/", common.credentials())        
        return client
    except exceptions.CosmosHttpResponseError as e:
        print(f"Failed to create Cosmos client: {e}")
        raise e
def get_database():
    try:
        database_name = os.getenv('DATABASE_NAME')
        database = get_cosmos_client().get_database_client(database_name)
        return database
    except exceptions.CosmosResourceNotFoundError as e:
        print(f"Database {database_name} not found.")
        raise e

def get_container() -> Container:
    try:
        container_name = os.getenv('CONTAINER_NAME')
        container = get_database().get_container_client(container_name)
        return container
    except exceptions.CosmosResourceNotFoundError as e :
        print(f"Container {container_name} not found.")
        raise e

def insert_cap(cap:Cap, container_client: Container):
    try:        
        cap_dictionary = cap.to_dict()

        # check if a cap with the same id already exists        
        # if container_client.query_items(query=f"SELECT * FROM c WHERE c.id = '{cap_dictionary['id']}'"):
        if container_client.read_item(item=cap_dictionary['id'], partition_key=cap_dictionary['country']):
            print(f"Cap {cap_dictionary['id']} already exists.")
    except exceptions.CosmosResourceNotFoundError:
        try:
            # if the item does not exist, create it
            _ = container_client.create_item(body=cap_dictionary)                    
        except exceptions.CosmosHttpResponseError as e:
            print(f"Failed to insert cap: {e}")

if __name__ == "__main__":

    cap = Cap(
        id="12",
        brand_id=1,
        brand="brand",
        brand_num=1,
        type="type",
        brewery="brewery",
        region="region",
        country="country",
        path="path",
        embeddings=[],
        base64="base64"
    )
    insert_cap(cap)