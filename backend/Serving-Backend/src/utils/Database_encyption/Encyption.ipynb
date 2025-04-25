{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "fbf667bd",
   "metadata": {},
   "source": [
    "# Save per insurance company"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "57c48709",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Encrypted data for BH saved to bh_collection.\n"
     ]
    }
   ],
   "source": [
    "from azure.cosmos import CosmosClient\n",
    "from cryptography.fernet import Fernet\n",
    "import json\n",
    "import os\n",
    "\n",
    "url = \"https://insuredpatients.documents.azure.com:443/\"\n",
    "key = \"AQFk1movQza5orCTnBNi1ZlOBTZPiGp0gTMSLEZOLXtXxYp4EKlGLMyor7VCZivXJIeZCGOgjq6vACDbqbsyLQ==\"\n",
    "\n",
    "with open(\"fernet.key\", \"rb\") as f:\n",
    "    fernet_key = f.read()\n",
    "cipher = Fernet(fernet_key)\n",
    "\n",
    "client = CosmosClient(url, credential=key)\n",
    "\n",
    "company_to_container = {\n",
    "    \"BH\": \"bh_collection\",\n",
    "    \"CNAM\": \"cnam_collection\",\n",
    "    \"STAR\": \"star_collection\"\n",
    "}\n",
    "\n",
    "insurance_company = \"BH\"  \n",
    "\n",
    "if insurance_company not in company_to_container:\n",
    "    raise ValueError(f\"Unknown insurance company: {insurance_company}\")\n",
    "\n",
    "database = client.get_database_client(\"cosmicworks\")\n",
    "container_name = company_to_container[insurance_company]\n",
    "container = database.get_container_client(container_name)\n",
    "\n",
    "json_file_path = f\"cropped_fields/extracted_text.json\"\n",
    "if not os.path.exists(json_file_path):\n",
    "    raise FileNotFoundError(f\"JSON file for {insurance_company} not found.\")\n",
    "\n",
    "with open(json_file_path, \"r\") as file:\n",
    "    data = json.load(file)\n",
    "\n",
    "encrypted = cipher.encrypt(json.dumps(data).encode()).decode()\n",
    "\n",
    "container.create_item(\n",
    "    body={\"category\": \"text_data\", \"insurance\": insurance_company, \"encrypted_data\": encrypted},\n",
    "    enable_automatic_id_generation=True\n",
    ")\n",
    "\n",
    "print(f\"Encrypted data for {insurance_company} saved to {container_name}.\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "237e5944",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "Fetching from bh_collection...\n",
      "{\n",
      "    \"cin_passport_subscriber\": \"98765432\",\n",
      "    \"patient_name\": \"Mohamed Mouhamed\",\n",
      "    \"subscriber_name\": \"Abderazak Braham\",\n",
      "    \"subscriber_address\": \"Sfax\"\n",
      "}\n",
      "\n",
      "Fetching from star_collection...\n",
      "{\n",
      "    \"cin_passport_subscriber\": \"98765432\",\n",
      "    \"patient_name\": \"Mohamed Mouhamed\",\n",
      "    \"subscriber_name\": \"Abderazak Braham\",\n",
      "    \"subscriber_address\": \"Sfax\"\n",
      "}\n",
      "\n",
      "Fetching from cnam_collection...\n",
      "{\n",
      "    \"cin_passport_subscriber\": \"98765432\",\n",
      "    \"patient_name\": \"Mohamed Mouhamed\",\n",
      "    \"subscriber_name\": \"Abderazak Braham\",\n",
      "    \"subscriber_address\": \"Sfax\"\n",
      "}\n"
     ]
    }
   ],
   "source": [
    "from azure.cosmos import CosmosClient\n",
    "from cryptography.fernet import Fernet, InvalidToken\n",
    "import json\n",
    "\n",
    "url = \"https://insuredpatients.documents.azure.com:443/\"\n",
    "key = \"AQFk1movQza5orCTnBNi1ZlOBTZPiGp0gTMSLEZOLXtXxYp4EKlGLMyor7VCZivXJIeZCGOgjq6vACDbqbsyLQ==\"\n",
    "\n",
    "# Load Fernet key\n",
    "with open(\"fernet.key\", \"rb\") as f:\n",
    "    fernet_key = f.read()\n",
    "\n",
    "cipher = Fernet(fernet_key)\n",
    "\n",
    "client = CosmosClient(url, credential=key)\n",
    "database = client.get_database_client(\"cosmicworks\")\n",
    "CONTAINER_NAMES = [\"bh_collection\", \"star_collection\", \"cnam_collection\"]\n",
    "\n",
    "for container_name in CONTAINER_NAMES:\n",
    "    print(f\"\\nFetching from {container_name}...\")\n",
    "    container = database.get_container_client(container_name)\n",
    "    \n",
    "    query = \"SELECT * FROM c\"\n",
    "    items = container.query_items(query=query, enable_cross_partition_query=True)\n",
    "    \n",
    "    for item in items:\n",
    "        encrypted = item.get(\"encrypted_data\")\n",
    "        if encrypted:\n",
    "            try:\n",
    "                decrypted_data = cipher.decrypt(encrypted.encode()).decode()\n",
    "                parsed = json.loads(decrypted_data)\n",
    "                print(json.dumps(parsed, indent=4))\n",
    "            except InvalidToken:\n",
    "                print(f\"Could not decrypt item with id: {item.get('id')}\")\n",
    "        else:\n",
    "            print(f\"No 'encrypted_data' field in item with id: {item.get('id')}\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0884d52d",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
