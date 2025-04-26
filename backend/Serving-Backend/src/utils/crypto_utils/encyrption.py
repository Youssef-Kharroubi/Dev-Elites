from azure.cosmos import CosmosClient
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json
import os



DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_KEY = os.getenv('DATABASE_KEY')
insurance_company = "BH"

with open("fernet.key", "rb") as f:
    fernet_key = f.read()
cipher = Fernet(fernet_key)

client = CosmosClient(DATABASE_URL , credential=DATABASE_KEY)

company_to_container = {
    "BH": "bh_collection",
    "CNAM": "cnam_collection",
    "STAR": "star_collection"
}

if insurance_company not in company_to_container:
    raise ValueError(f"Unknown insurance company: {insurance_company}")

database = client.get_database_client("cosmicworks")
container_name = company_to_container[insurance_company]
container = database.get_container_client(container_name)

json_file_path = f"cropped_fields/extracted_text.json"
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"JSON file for {insurance_company} not found.")

with open(json_file_path, "r") as file:
    data = json.load(file)

encrypted = cipher.encrypt(json.dumps(data).encode()).decode()

container.create_item(
    body={"category": "text_data", "insurance": insurance_company, "encrypted_data": encrypted},
    enable_automatic_id_generation=True
)

print(f"Encrypted data for {insurance_company} saved to {container_name}.")
