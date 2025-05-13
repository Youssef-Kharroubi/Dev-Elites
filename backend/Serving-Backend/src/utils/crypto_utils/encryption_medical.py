from azure.cosmos import CosmosClient, PartitionKey
from cryptography.fernet import Fernet
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

def encrypt_and_store_json_data(json_data: dict):
    base_path = os.path.dirname(__file__)
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_KEY = os.getenv('DATABASE_KEY')
    fernet_key_path = os.path.join(base_path, '..', '..', 'models', 'fernet.key')

    if not DATABASE_URL or not DATABASE_KEY:
        raise ValueError("DATABASE_URL and DATABASE_KEY must be set in environment variables.")

    try:
        with open(fernet_key_path, "rb") as key_file:
            fernet_key = key_file.read()
    except FileNotFoundError:
        print(f"Fernet key not found at: {fernet_key_path}")
        return

    cipher = Fernet(fernet_key)


    encrypted = cipher.encrypt(json.dumps(json_data).encode()).decode()
    
    fields_list = list(json_data.keys())
    if "state" not in fields_list:
        fields_list.append("state")

    client = CosmosClient(DATABASE_URL, credential=DATABASE_KEY)
    database = client.get_database_client("MedicalFormsDB")
    container = database.get_container_client("BH")

    existing_items = list(container.query_items(
        query=f"SELECT * FROM c WHERE c.state = @state AND c.fields = @fields",
        parameters=[{"name": "@state", "value": "tunisia"}, {"name": "@fields", "value": fields_list}],
        enable_cross_partition_query=True
    ))

    document_data = {
        "id": str(uuid.uuid4()),  
        "encrypted_data": encrypted,
        "fields": fields_list,
        "state": "tunisia"
    }

    #if existing_items:
        #existing_doc = existing_items[0]
        #existing_doc.update(document_data)
        #container.replace_item(item=existing_doc['id'], body=existing_doc)
        #print(f"Updated existing document for {insurance_company} in {company_to_container[insurance_company]} container.")
    #else:
    container.create_item(body=document_data)
    # print(f"Created new document for {insurance_company} in {company_to_container[insurance_company]} container.")

# #call of the code
# my_data = {"birth_date": "2020-08-03", "subscriber_name": "amyyne", "patient_name": "ben abdallahh", "id_form":"123542", "cnam_code": "31478", "cin_or_passport": "213836", "address": "soussee"}
# encrypt_and_store_json_data(my_data, "BH")
