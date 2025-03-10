from ..data.data_loader import split_dataset, get_data_generators
from ..models.classifier import train_classifier
from ...DB.model_store import save_model, list_blobs, download_blob
import os
import json
from azure.storage.blob import BlobServiceClient


AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME");
BLOB_PREFIX = "models/"

def fetch_model_configs():
    """Fetch model configurations from Azure Blob Storage by reading metadata.json files."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    blob_list = container_client.list_blobs(name_starts_with=BLOB_PREFIX)

    model_configs = []

    for blob in blob_list:
        if blob.name.endswith("metadata.json"):
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall()

            metadata = json.loads(blob_data.decode("utf-8"))

            metadata["output_dir"] = os.path.join("/app/models", os.path.basename(os.path.dirname(blob.name)))
            model_configs.append(metadata)

    return model_configs

def train_single_model(train_gen, val_gen, config):
    """Train a single model based on its configuration."""
    print(f"Training {config['name']}...")

    model, history = train_classifier(train_gen, val_gen, model_type=config["type"])

    os.makedirs(config["output_dir"], exist_ok=True)

    model_path = os.path.join(config["output_dir"], config["model_file"])
    model.save(model_path)

    save_model(model_path, config["name"], config["version"], config["type"], config["type"])

    print(f"Completed training and saved {config['name']} to {model_path}")

def main():

    input_dir = "/app/dataset"
    train_dir = "/app/train_dataset"
    val_dir = "/app/validation_dataset"
    test_dir = "/app/test_dataset"

    split_dataset(input_dir, train_dir, val_dir, test_dir)
    train_gen, val_gen, test_gen = get_data_generators(train_dir, val_dir, test_dir)

    MODEL_CONFIGS = fetch_model_configs()

    if not MODEL_CONFIGS:
        print("No model configurations found in Azure Blob Storage.")
        return

    for config in MODEL_CONFIGS:
        train_single_model(train_gen, val_gen, config)

    print("All models trained and uploaded successfully!")

if __name__ == "__main__":
    main()