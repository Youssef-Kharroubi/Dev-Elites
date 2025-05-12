from azure.cosmos import CosmosClient
from cryptography.fernet import Fernet, InvalidToken
import json
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_and_decrypt_documents(database_name: str, container_names: list, key_path: str = "../../models/fernet.key"):
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_KEY = os.getenv('DATABASE_KEY')

    if not DATABASE_URL or not DATABASE_KEY:
        raise ValueError("DATABASE_URL and DATABASE_KEY must be set in environment variables.")

    try:
        with open(key_path, "rb") as f:
            fernet_key = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Fernet key file not found at: {key_path}")

    cipher = Fernet(fernet_key)

    client = CosmosClient(DATABASE_URL, credential=DATABASE_KEY)
    database = client.get_database_client(database_name)

    for container_name in container_names:
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

# code call
fetch_and_decrypt_documents(
    database_name="MedicalFormsDB",
    container_names=["BH", "STAR", "CNAM"],
    key_path="../../models/fernet.key"
)