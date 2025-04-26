from azure.cosmos import CosmosClient
from cryptography.fernet import Fernet, InvalidToken
import json
import os
from dotenv import load_dotenv




DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_KEY = os.getenv('DATABASE_KEY')


with open("fernet.key", "rb") as f:
    fernet_key = f.read()

cipher = Fernet(fernet_key)

client = CosmosClient(DATABASE_URL, credential=DATABASE_KEY)
database = client.get_database_client("cosmicworks")
CONTAINER_NAMES = ["bh_collection", "star_collection", "cnam_collection"]

for container_name in CONTAINER_NAMES:
    print(f"\nFetching from {container_name}...")
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c"
    items = container.query_items(query=query, enable_cross_partition_query=True)

    for item in items:
        encrypted = item.get("encrypted_data")
        if encrypted:
            try:
                decrypted_data = cipher.decrypt(encrypted.encode()).decode()
                parsed = json.loads(decrypted_data)
                print(json.dumps(parsed, indent=4))
            except InvalidToken:
                print(f"Could not decrypt item with id: {item.get('id')}")
        else:
            print(f"No 'encrypted_data' field in item with id: {item.get('id')}")
