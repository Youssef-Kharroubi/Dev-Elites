from azure.storage.blob import BlobServiceClient
import os
import json

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME");

def save_model(model_files, name, version, model_type, framework):
    """
    Uploads model files and metadata to Azure Blob Storage.
    :param model_files: List of local file paths (e.g., ["path/to/model.h5"])
    :param name: Model name (e.g., 'classifier')
    :param version: Model version (e.g., 'v1.0')
    :param model_type: Type of model (e.g., 'classifier', 'generator')
    :param framework: Framework used (e.g., 'tensorflow', 'pytorch')
    """
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)


    metadata = {
        "name": name,
        "version": version,
        "type": model_type,
        "framework": framework,
        "files": [os.path.basename(f) for f in model_files]
    }


    for file_path in model_files:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=f"{name}/{version}/{os.path.basename(file_path)}"
        )
        with open(file_path, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        print(f"Uploaded {file_path} to {CONTAINER_NAME}/{name}/{version}/{os.path.basename(file_path)}")

    # Upload metadata
    metadata_blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=f"{name}/{version}/metadata.json"
    )
    metadata_blob_client.upload_blob(json.dumps(metadata), overwrite=True)
    print(f"Metadata for {name} v{version} uploaded")

def load_model(name, version, output_dir):
    """
    Downloads model files from Azure Blob Storage based on metadata.
    :param name: Model name
    :param version: Model version
    :param output_dir: Local directory to save the model files
    """
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    os.makedirs(output_dir, exist_ok=True)

    metadata_blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=f"{name}/{version}/metadata.json"
    )
    metadata = json.loads(metadata_blob_client.download_blob().readall())


    for file_name in metadata["files"]:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=f"{name}/{version}/{file_name}"
        )
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, "wb") as f:
            blob_data = blob_client.download_blob()
            f.write(blob_data.readall())
        print(f"Downloaded {file_name} to {output_path}")

    return metadata
def list_blobs(prefix=None):
    """
    List all blobs in the specified container, optionally filtered by a prefix.

    Args:
        prefix (str, optional): Filter blobs that start with this prefix (e.g., "models/").

    Returns:
        list: A list of blob names.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        blobs = container_client.list_blobs(name_starts_with=prefix)

        blob_names = [blob.name for blob in blobs]
        return blob_names

    except Exception as e:
        print(f"Error listing blobs: {str(e)}")
        return []

def download_blob(blob_name, destination_path=None):
    """
    Download a blob from Azure Blob Storage to a local file or return its content.

    Args:
        blob_name (str): The name of the blob to download (e.g., "models/classifier_cnn_v1/metadata.json").
        destination_path (str, optional): Local path to save the blob. If None, returns content as bytes.

    Returns:
        bytes: Blob content if destination_path is None, otherwise None.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        blob_client = container_client.get_blob_client(blob_name)

        if destination_path:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, "wb") as file:
                blob_data = blob_client.download_blob()
                file.write(blob_data.readall())
            print(f"Downloaded {blob_name} to {destination_path}")
            return None
        else:
            blob_data = blob_client.download_blob()
            return blob_data.readall()

    except Exception as e:
        print(f"Error downloading blob {blob_name}: {str(e)}")
        return None