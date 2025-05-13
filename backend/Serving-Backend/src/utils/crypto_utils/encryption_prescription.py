from azure.cosmos import CosmosClient
import json
import os
import uuid
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

def store_prescription_document(decrypted_json: str):
    base_path = os.path.dirname(__file__)
    fernet_key_path = os.path.join(base_path, '..', '..', 'models', 'fernet.key')
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_KEY = os.getenv('DATABASE_KEY')

    if not DATABASE_URL or not DATABASE_KEY:
        raise ValueError("DATABASE_URL and DATABASE_KEY must be set in environment variables.")

    try:
        with open(fernet_key_path, "rb") as key_file:
            fernet_key = key_file.read()
    except FileNotFoundError:
        print(f"Fernet key not found at: {fernet_key_path}")
        return

    cipher = Fernet(fernet_key)

    client = CosmosClient(DATABASE_URL, credential=DATABASE_KEY)
    database = client.get_database_client("insured-patients")
    container = database.get_container_client("prescriptions")

    try:
        data = json.loads(decrypted_json)
        original_id = data.get("id_medical_care_form")
        medications = data.get("medications")

        if not original_id or not isinstance(medications, list):
            print(f"Invalid data format: {data}")
            return

        fields = list(data.keys())  
        encrypted_data = cipher.encrypt(decrypted_json.encode()).decode()

    except json.JSONDecodeError:
        print(f"Invalid JSON string: {decrypted_json}")
        return

    document = {
        "id": str(uuid.uuid4()),
        "encrypted_data": encrypted_data,
        "fields": fields
    }

    container.create_item(body=document)
    print(f"Inserted prescription document for source ID: {original_id}")

# decrypted_doc = '{"id_medical_care_form": "18549", "medications": ["Lisinopril", "Metformin"]}'
# store_prescription_document(decrypted_doc)
