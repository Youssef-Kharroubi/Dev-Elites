import os

import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import threading
import queue
from torch.cuda.amp import autocast
from azure.cosmos import CosmosClient, PartitionKey
import uuid
from cryptography.fernet import Fernet, InvalidToken
import json
import base64
from datetime import datetime
import traceback
from google.colab import drive
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.applications.vgg16 import preprocess_input
import sys


drive.mount('/content/drive')
!ls /content/drive/MyDrive/modeling/
yolo_model_path = '/content/drive/MyDrive/modeling/yolov8_medical_forms.pt'
cnn_model_path = '/content/drive/MyDrive/modeling/cnn_model.h5'
vgg_model_path = '/content/drive/MyDrive/modeling/insurance_classifier_vgg16.h5'



def preprocess_image(image_path):
    image = Image.open(image_path)
    gray_image = image.convert("L")

    enhancer = ImageEnhance.Sharpness(gray_image)
    sharp_image = enhancer.enhance(2.0)

    resized_image = sharp_image.resize((256, 256), Image.LANCZOS)
    final_image = ImageEnhance.Sharpness(resized_image).enhance(1.5)

    final_image_rgb = np.stack([np.array(final_image)] * 3, axis=-1)
    return final_image_rgb


def predict_binary(model, image_path):
    image_array = preprocess_image(image_path) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    prediction = model.predict(image_array)
    predicted_class = 1 if prediction >= 0.5 else 0
    probability = prediction[0][0]
    return predicted_class, probability

    def predict_insurance_company(model, image_path, class_names):
    image_array = preprocess_image(image_path) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    prediction = model.predict(image_array)
    predicted_index = np.argmax(prediction[0])
    predicted_class = class_names[predicted_index]
    probability = prediction[0][predicted_index]
    return predicted_class, probability

    def predict_images_in_folder(model, folder_path, class_names, target_size=(256, 256)):
    print(f"Processing folder: {folder_path}")

    # List image paths (including subfolders)
    image_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))

    if not image_paths:
        print("No images found in the folder. Check path and file extensions.")
        return

    print(f"Found {len(image_paths)} images: {image_paths}")

    # Process each image individually using a for loop
    for img_path in image_paths:
        print(f"\nProcessing image: {img_path}")

        # Load and preprocess the image for prediction
        try:
            img = load_img(img_path, target_size=target_size)  # Resize to (256, 256)
            img_array = img_to_array(img)
            img_array_pred = preprocess_input(img_array.copy())  # VGG-specific preprocessing for prediction
            img_array_pred = np.expand_dims(img_array_pred, axis=0)  # Add batch dimension for prediction
            print(f"Loaded image for prediction: {img_path}")
        except Exception as e:
            print(f"Error loading image for prediction {img_path}: {e}")
            continue

        # Make prediction
        try:
            prediction = model.predict(img_array_pred, verbose=1)
            predicted_class_idx = np.argmax(prediction[0])
            predicted_class = class_names[predicted_class_idx]
            confidence = prediction[0][predicted_class_idx]
            print(f"Image: {os.path.basename(img_path)}")
            print(f"Predicted Class: {predicted_class}, Confidence: {confidence:.4f}")
        except Exception as e:
            print(f"Error during prediction for {img_path}: {e}")
            continue

        # Display the image with its predicted class
        try:
            # Load the image again without preprocessing for display (to show the original colors)
            img_display = load_img(img_path)  # Load original image for display
            plt.figure(figsize=(8, 6))  # Set figure size
            plt.imshow(img_display)
            plt.title(f"Predicted Class: {predicted_class}\nConfidence: {confidence:.4f}", fontsize=12)
            plt.axis('off')  # Hide axes
            plt.show()
            print("-" * 50)
        except Exception as e:
            print(f"Error displaying image {img_path}: {e}")
            continue

            model = load_model(vgg_model_path)
print("Model loaded successfully.")
model.summary()  # Check input/output shapes for reference

# Define inputs
class_names = ['BH', 'CNAM', 'STAR']
test_folder = "/content/drive/MyDrive/modeling/classifier"

# Run predictions
predict_images_in_folder(model, test_folder, class_names)
sys.stdout.flush()



# Verify Google Drive contents
print("Listing contents of /content/drive/MyDrive/modeling/:")
!ls /content/drive/MyDrive/modeling/

# Configuration
MEDICAL_FORMS_DIR = "/content/drive/MyDrive/modeling/classifier"  # Directory containing images
BASE_DIR = "/content/modeling"  # Temporary directory in Colab
LABELS = ["nom", "cin", "adresse", "cnam", "matricule", "malade", "naissance", "date", "designation", "honoraire"]
COLORS = {
    "nom": (255, 0, 0), "cin": (0, 255, 0), "adresse": (0, 0, 255), "cnam": (255, 255, 0),
    "matricule": (255, 165, 0), "malade": (255, 0, 255), "naissance": (75, 0, 130),
    "date": (0, 255, 255), "designation": (128, 0, 128), "honoraire": (0, 128, 128)
}

# Azure Cosmos DB Configuration
COSMOS_ENDPOINT = "https://medicalformdb.documents.azure.com:443/"
COSMOS_KEY = "sRvlVaXPiP2pTeAYbZ7v7ohIwws7GpUKjEMnJ1YvHe0Xar1yhsyTu3rfYIkSdf8lMBNy2FQ9doUbACDb0d4dwg=="
DATABASE_NAME = "MedicalFormsDB"
BH_CONTAINER_NAME = "BH"
CNAM_CONTAINER_NAME = "CNAM"
STAR_CONTAINER_NAME = "STAR"

# Encryption Configuration
FERNET_KEY_PATH = os.path.join(BASE_DIR, "fernet.key")

# Create BASE_DIR if it doesn't exist
os.makedirs(BASE_DIR, exist_ok=True)

# Initialize Fernet encryption
def init_fernet():
    if not os.path.exists(FERNET_KEY_PATH):
        key = Fernet.generate_key()
        with open(FERNET_KEY_PATH, "wb") as key_file:
            key_file.write(key)
        print(f"New Fernet key generated at {FERNET_KEY_PATH}")

    with open(FERNET_KEY_PATH, "rb") as key_file:
        key = key_file.read()
    return Fernet(key)

cipher = init_fernet()

# Initialize YOLO and TrOCR
yolo_model_path = "/content/drive/MyDrive/modeling/yolov8_medical_forms.pt"
if not os.path.exists(yolo_model_path):
    raise FileNotFoundError(f"YOLO model file not found at {yolo_model_path}. Please ensure the file exists and the path is correct.")
yolo_model = YOLO(yolo_model_path)

try:
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")
    TROCR_AVAILABLE = True
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"TROCR initialized on {device}")
except Exception as e:
    print(f"Error loading TrOCR: {str(e)}")
    TROCR_AVAILABLE = False

# Load VGG model for classification
if not os.path.exists(vgg_model_path):
    raise FileNotFoundError(f"VGG model file not found at {vgg_model_path}. Please ensure the file exists and the path is correct.")

# Re-save VGG model to address FailedPreconditionError
try:
    vgg_model = load_model(vgg_model_path)

except Exception as e:
    print(f"Error loading or re-saving VGG model: {e}")
    sys.exit(1)

# Define inputs for VGG prediction
class_names = ['BH', 'CNAM', 'STAR']

# Initialize Cosmos DB client
def init_cosmos_client():
    try:
        client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
        database = client.create_database_if_not_exists(id=DATABASE_NAME)

        bh_container = database.create_container_if_not_exists(
            id=BH_CONTAINER_NAME,
            partition_key=PartitionKey(path="/bh")
        )
        cnam_container = database.create_container_if_not_exists(
            id=CNAM_CONTAINER_NAME,
            partition_key=PartitionKey(path="/cnam")
        )
        star_container = database.create_container_if_not_exists(
            id=STAR_CONTAINER_NAME,
            partition_key=PartitionKey(path="/star")
        )

        print(f"Connected to Cosmos DB: {DATABASE_NAME}/{BH_CONTAINER_NAME}, {CNAM_CONTAINER_NAME}, {STAR_CONTAINER_NAME}")
        return bh_container, cnam_container, star_container
    except Exception as e:
        print(f"Error connecting to Cosmos DB: {str(e)}")
        return None, None, None

bh_container, cnam_container, star_container = init_cosmos_client()

# [Unchanged Functions: encrypt_data, decrypt_data, trocr_transcribe, predict_image_class, process_form_image, get_form_data, test_decryption]
# Paste these functions from your original code here if needed, as they remain unchanged.

def encrypt_data(data):
    """Encrypt dictionary data using Fernet"""
    json_data = json.dumps(data)
    encrypted = cipher.encrypt(json_data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_data(encrypted_data):
    """Decrypt data back to dictionary"""
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(encrypted_bytes).decode()
        return json.loads(decrypted)
    except (InvalidToken, ValueError, json.JSONDecodeError) as e:
        print(f"Decryption error: {str(e)}")
        return None

def trocr_transcribe(image_path, timeout=30):
    if not TROCR_AVAILABLE:
        print(f"TrOCR unavailable for {os.path.basename(image_path)}")
        return ""

    result_queue = queue.Queue()

    def process_image():
        try:
            image = Image.open(image_path).convert("RGB")
            image = image.resize((384, 384), Image.LANCZOS)
            pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
            with autocast(enabled=device == "cuda"):
                generated_ids = model.generate(pixel_values)
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            result_queue.put(generated_text.strip())
        except Exception as e:
            print(f"TrOCR error for {os.path.basename(image_path)}: {str(e)}")
            result_queue.put("")

    thread = threading.Thread(target=process_image)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print(f"TrOCR timed out after {timeout} seconds for {os.path.basename(image_path)}")
        return ""

    return result_queue.get()

def predict_image_class(image_path, model, class_names, target_size=(256, 256)):
    """Predict the class of an image using the VGG model"""
    try:
        # Load and resize the image
        img = load_img(image_path, target_size=target_size)
        if img is None:
            raise ValueError("Failed to load image")

        # Convert to array and check shape
        img_array = img_to_array(img)
        if img_array.shape != (target_size[0], target_size[1], 3):
            raise ValueError(f"Expected image shape {target_size + (3,)}, but got {img_array.shape}")

        # Preprocess the image
        img_array = preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

        # Check for NaN or Inf values
        if np.any(np.isnan(img_array)) or np.any(np.isinf(img_array)):
            raise ValueError("Image array contains NaN or Inf values after preprocessing")

        # Make prediction
        prediction = model.predict(img_array, verbose=0)
        predicted_class_idx = np.argmax(prediction[0])
        predicted_class = class_names[predicted_class_idx]
        confidence = prediction[0][predicted_class_idx]
        return predicted_class, confidence

    except Exception as e:
        print(f"Error predicting class for {image_path}: {str(e)}")
        return None, None

def process_form_image(image_path, conf=0.5):
    if not os.path.exists(image_path):
        raise ValueError(f"Image not found at {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image at {image_path}")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    vis_image = image.copy()

    # Predict the class using VGG model
    predicted_class, confidence = predict_image_class(image_path, vgg_model, class_names)
    if predicted_class is None:
        print(f"Skipping processing for {image_path} due to prediction error")
        return None, None

    print(f"Image: {os.path.basename(image_path)}")
    print(f"Predicted Class: {predicted_class}, Confidence: {confidence:.4f}")

    # Predict bounding boxes using YOLO
    results = yolo_model.predict(image_rgb, conf=conf, iou=0.5)
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confidences = results[0].boxes.conf.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()

    # Prepare data structure
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    form_data = {
        "id": str(uuid.uuid4()),
        "image_name": image_name,
    }

    # Process each detected field
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        if x2 <= x1 or y2 <= y1 or x1 < 0 or y1 < 0 or x2 > image.shape[1] or y2 > image.shape[0]:
            continue

        label = LABELS[int(classes[i])]
        cropped_image = image_rgb[y1:y2, x1:x2]
        if cropped_image.size == 0:
            continue

        # Preprocess and transcribe
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        cropped_image = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

        temp_path = os.path.join(BASE_DIR, "temp_crop.jpg")
        cv2.imwrite(temp_path, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))

        text = trocr_transcribe(temp_path)
        os.remove(temp_path)

        if text:
            form_data[label] = text

        color = COLORS.get(label, (255, 255, 255))
        cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(vis_image, f"{label}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save visualization
    vis_path = os.path.join(BASE_DIR, "visualizations", f"{image_name}_processed.jpg")
    os.makedirs(os.path.dirname(vis_path), exist_ok=True)
    cv2.imwrite(vis_path, vis_image)

    # Save form data to the appropriate Cosmos DB container
    if len(form_data) > 2:
        try:
            sensitive_data = {k: v for k, v in form_data.items() if k not in ["id", "image_name"]}
            sensitive_data["state"] = "tunisia"
            encrypted_data = encrypt_data(sensitive_data)

            document = {
                "id": form_data["id"],
                "image_name": form_data["image_name"],
                "encrypted_data": encrypted_data,
                "fields": list(sensitive_data.keys()),
                "state": "tunisia"
            }

            container = None
            partition_key_field = None
            if predicted_class == "BH":
                container = bh_container
                document["bh"] = image_name
                partition_key_field = "bh"
            elif predicted_class == "CNAM":
                container = cnam_container
                document["cnam"] = image_name
                partition_key_field = "cnam"
            elif predicted_class == "STAR":
                container = star_container
                document["star"] = image_name
                partition_key_field = "star"

            if container:
                existing_items = list(container.query_items(
                    query=f"SELECT * FROM c WHERE c.{partition_key_field} = @image_name",
                    parameters=[{"name": "@image_name", "value": image_name}],
                    enable_cross_partition_query=True
                ))

                if existing_items:
                    existing_doc = existing_items[0]
                    existing_doc.update(document)
                    container.replace_item(item=existing_doc['id'], body=existing_doc)
                    print(f"Updated existing document for {image_name} in {predicted_class} container")
                else:
                    container.create_item(body=document)
                    print(f"Created new document for {image_name} in {predicted_class} container")
            else:
                print(f"No container available for predicted class {predicted_class}")
        except Exception as e:
            print(f"Error saving to Cosmos DB: {str(e)}")

    return form_data, vis_path

def get_form_data(image_name, predicted_class, decrypt=True):
    if not predicted_class:
        print("Predicted class must be provided to query the correct container")
        return None

    container = None
    partition_key_field = None
    if predicted_class == "BH":
        container = bh_container
        partition_key_field = "bh"
    elif predicted_class == "CNAM":
        container = cnam_container
        partition_key_field = "cnam"
    elif predicted_class == "STAR":
        container = star_container
        partition_key_field = "star"

    if not container:
        print(f"No container available for predicted class {predicted_class}")
        return None

    try:
        items = list(container.query_items(
            query=f"SELECT * FROM c WHERE c.{partition_key_field} = @image_name",
            parameters=[{"name": "@image_name", "value": image_name}],
            enable_cross_partition_query=True
        ))

        if not items:
            return None

        document = items[0]

        if decrypt and "encrypted_data" in document:
            decrypted = decrypt_data(document["encrypted_data"])
            if decrypted:
                result = {
                    "id": document["id"],
                    "image_name": document["image_name"],
                    "state": document.get("state", "tunisia"),
                    **decrypted
                }
                return result

        return document
    except Exception as e:
        print(f"Error querying Cosmos DB: {str(e)}")
        return None

def test_decryption(image_name, predicted_class):
    document = get_form_data(image_name, predicted_class, decrypt=False)
    if not document or "encrypted_data" not in document:
        print(f"No encrypted data found for {image_name} in {predicted_class} container")
        return

    print("\nTesting decryption...")
    print(f"Document ID: {document['id']}")
    print(f"Fields present: {document.get('fields', [])}")

    decrypted = decrypt_data(document["encrypted_data"])
    if decrypted:
        print("\nSuccessfully decrypted data:")
        for field, value in decrypted.items():
            print(f"{field}: {value}")
    else:
        print("Failed to decrypt data")

# Main block to process a single image
if __name__ == "__main__":
    try:
        # Specify the single image to process
        image_path = "/content/drive/MyDrive/modeling/classifier/0675--9124833--20230705_page_0.jpg"

        # Verify image exists
        if not os.path.exists(image_path):
            print(f"Image file not found at {image_path}")
            sys.exit(1)

        print(f"Processing single image: {image_path}")

        # Process the image
        form_data, vis_path = process_form_image(image_path, conf=0.5)
        if form_data:
            print(f"Extracted form data: {form_data}")
            print(f"Visualization saved to: {vis_path}")

            # Test decryption
            predicted_class, _ = predict_image_class(image_path, vgg_model, class_names)
            if predicted_class:
                test_decryption(form_data["image_name"], predicted_class)

    except Exception as e:
        print(f"Error during image processing or saving: {str(e)}")
        sys.exit(1)