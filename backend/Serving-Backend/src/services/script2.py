import os
import json
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from cryptography.fernet import Fernet
import base64
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
COSMOS_ENDPOINT = "https://medicalformdb.documents.azure.com:443/"
COSMOS_KEY = "sRvlVaXPiP2pTeAYbZ7v7ohIwws7GpUKjEMnJ1YvHe0Xar1yhsyTu3rfYIkSdf8lMBNy2FQ9doUbACDb0d4dwg=="
DATABASE_NAME = "MedicalFormsDB"
STAR_CONTAINER_NAME = "STAR"  # Updated to STAR container
METRICS_CONTAINER_NAME = "ModelMetrics"
FERNET_KEY_PATH = "C:/Users/MSI/Desktop/MODELING/fernet2.key"
STAR_CSV_PATH = "C:/Users/MSI/Desktop/MODELING/decrypted_star.csv"  # Updated output file
METRICS_CSV_PATH = "C:/Users/MSI/Desktop/MODELING/model_metrics.csv"

# Expected columns for STAR data CSV
STAR_COLUMNS = [
    "id", "image_name", "designation", "honoraire", "matricule", "date",
    "nom", "naissance", "malade", "cin", "adresse", "cnam", "state"
]

# Initialize Fernet
def init_fernet():
    if not os.path.exists(FERNET_KEY_PATH):
        logging.error(f"Fernet key not found at {FERNET_KEY_PATH}")
        raise FileNotFoundError(f"Fernet key not found at {FERNET_KEY_PATH}")
    with open(FERNET_KEY_PATH, "rb") as key_file:
        key = key_file.read()
    return Fernet(key)

cipher = init_fernet()

# Initialize Cosmos DB client
def init_cosmos_client():
    try:
        client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
        database = client.get_database_client(DATABASE_NAME)
        star_container = database.get_container_client(STAR_CONTAINER_NAME)
        metrics_container = database.get_container_client(METRICS_CONTAINER_NAME)
        logging.info(f"Connected to Cosmos DB: {DATABASE_NAME}/{STAR_CONTAINER_NAME} and {METRICS_CONTAINER_NAME}")
        return star_container, metrics_container
    except Exception as e:
        logging.error(f"Error connecting to Cosmos DB: {str(e)}")
        return None, None

star_container, metrics_container = init_cosmos_client()

def decrypt_data(encrypted_data):
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(encrypted_bytes).decode()
        return json.loads(decrypted)
    except base64.binascii.Error as e:
        logging.error(f"Base64 decoding error: {str(e)}")
        return None
    except Fernet.InvalidToken as e:
        logging.error(f"Fernet decryption error (invalid token): {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected decryption error: {str(e)}")
        return None

# Export decrypted STAR data to CSV
def export_form_data(output_file=STAR_CSV_PATH):
    if not star_container:
        logging.error("STAR container not initialized")
        return None
    
    documents = []
    try:
        # Query all items in STAR container
        query = "SELECT * FROM c"
        items = list(star_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        for item in items:
            doc = {
                "id": item.get("id", ""),
                "image_name": item.get("image_name", "")
            }
            if "encrypted_data" in item:
                decrypted = decrypt_data(item["encrypted_data"])
                if decrypted:
                    # Update with decrypted fields, default to empty string if missing
                    for col in STAR_COLUMNS:
                        if col not in doc:  # Don't overwrite id or image_name
                            doc[col] = decrypted.get(col, "")
            
            # Ensure all expected columns are present
            for col in STAR_COLUMNS:
                if col not in doc:
                    doc[col] = ""
            
            documents.append(doc)
        
        # Convert to DataFrame
        df = pd.DataFrame(documents)
        
        # Reorder columns to match STAR_COLUMNS
        df = df[STAR_COLUMNS]
        
        # Log missing columns
        missing_cols = [col for col in STAR_COLUMNS if col not in df.columns]
        if missing_cols:
            logging.warning(f"Missing columns in DataFrame: {missing_cols}")
        
        # Save to CSV with UTF-8 encoding
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        logging.info(f"Decrypted STAR data exported to {output_file} ({len(df)} records)")
        return df
    
    except Exception as e:
        logging.error(f"Error exporting STAR data: {str(e)}")
        return None

# Export ModelMetrics data to CSV (unchanged)
def export_metrics_data(output_file=METRICS_CSV_PATH):
    if not metrics_container:
        logging.error("Metrics container not initialized")
        return None
    
    documents = []
    try:
        # Query all items
        query = "SELECT * FROM c"
        items = list(metrics_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        for item in items:
            # Include all fields (no decryption needed)
            doc = {
                "id": item.get("id", ""),
                "model_version": item.get("model_version", ""),
                "timestamp": item.get("timestamp", ""),
                "precision": item.get("precision", ""),
                "recall": item.get("recall", ""),
                "mAP50": item.get("mAP50", ""),
                "mAP50_95": item.get("mAP50_95", ""),
                "box_loss": item.get("box_loss", ""),
                "cls_loss": item.get("cls_loss", ""),
                "training_time": item.get("training_time", "")
            }
            documents.append(doc)
        
        # Convert to DataFrame
        df = pd.DataFrame(documents)
        
        # Save to CSV with UTF-8 encoding
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        logging.info(f"Metrics data exported to {output_file} ({len(df)} records)")
        return df
    
    except Exception as e:
        logging.error(f"Error exporting metrics data: {str(e)}")
        return None

# Main execution
if __name__ == "__main__":
    # Export STAR data
    star_df = export_form_data()
    if star_df is not None:
        logging.info(f"Exported {len(star_df)} STAR records")
    
    # Export ModelMetrics data
    metrics_df = export_metrics_data()
    if metrics_df is not None:
        logging.info(f"Exported {len(metrics_df)} metrics records")