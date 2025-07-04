import cv2
import numpy as np
import os
import pandas as pd
import json
import logging
import re
import gc
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from thefuzz import fuzz


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', filename='app.log')
logger = logging.getLogger(__name__)
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

def load_and_clean_data(excel_path):
    """Load and clean the medicine dataset from an Excel file."""
    df = pd.read_excel(excel_path)
    name_list = df['Nom'].dropna().astype(str).tolist()
    return name_list

def preprocess_image_for_detection(image_path):
    """Load and preprocess image for text detection."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not loaded correctly.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    processed_img = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return processed_img

def detect_text(image, reader):
    """Detect text in the preprocessed image using EasyOCR."""
    results = reader.readtext(
        image,
        detail=1,
        paragraph=False,
        ycenter_ths=0.3,
        height_ths=2,
        min_size=20,
        mag_ratio=1.5
    )
    return results

def preprocess_for_classification(img, img_height=256, img_width=128):
    """Preprocess cropped image for classification."""
    if img is None or img.size == 0:
        return None
    img = cv2.resize(img, (img_width, img_height))
    img = img / 255.0
    img = np.expand_dims(img, axis=(0, -1))
    return img

def classify_text(img, model):
    """Classify text as handwritten or printed."""
    if img is None:
        return None
    prediction = model.predict(img)
    label = "Handwritten" if prediction[0][0] < 0.5 else "Printed"
    confidence = 1 - prediction[0][0] if label == "Handwritten" else prediction[0][0]
    return label, confidence


def recognize_handwritten_text(img, processor, model):
    """Recognize handwritten text using TrOCR."""
    if img is None:
        return None
    pil_img = Image.fromarray(img, mode='RGB')
    pixel_values = processor(pil_img, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text

def is_valid_text(text):
    """Check if text contains at most one non-letter character (excluding spaces)."""
    non_letter_count = len(re.findall(r'[^a-zA-Z\s]', text))
    cleaned_text = re.sub(r'[^a-zA-Z]', '', text)
    return non_letter_count <= 1, cleaned_text

def match_word_to_names(word, name_list, threshold=65):
    """Match a word to a list of names based on fuzzy similarity."""
    matches = []
    for name in name_list:
        similarity = fuzz.ratio(word.lower(), name.lower())
        if similarity >= threshold:
            matches.append((name, similarity))
    return sorted(matches, key=lambda x: x[1], reverse=True)


def predict_text(image_path, excel_path, classification_model, reader_easy_ocr):
    name_list = load_and_clean_data(excel_path)

    processed_img = preprocess_image_for_detection(image_path)

    results = detect_text(processed_img, reader_easy_ocr)

    predicted_texts = []
    for idx, (bbox, text, prob) in enumerate(results):
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = (int(top_left[0]), int(top_left[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))

        word_img = processed_img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        if word_img.shape[0] <= 0 or word_img.shape[1] <= 0:
            print(f"Word {idx + 1} has invalid dimensions and will be skipped.")
            continue

        word_img_preprocessed = preprocess_for_classification(word_img)
        label, confidence = classify_text(word_img_preprocessed, classification_model)
        print(f"the image is {label}")
        if label == "Handwritten":
            word_img_rgb = cv2.cvtColor(word_img, cv2.COLOR_GRAY2RGB)
            recognized_text = recognize_handwritten_text(word_img_rgb, processor, trocr_model)
            if recognized_text:
                is_valid, cleaned_text = is_valid_text(recognized_text)
                if is_valid and len(cleaned_text) > 2:
                    predicted_texts.append(cleaned_text)
                    print(f"Word {idx + 1}: {cleaned_text} (Valid, Confidence: {confidence:.2f})")
                else:
                    print(f"Word {idx + 1}: {recognized_text} (Skipped: Invalid or too short)")

    # Initialize output list
    output = []

    # Process each predicted text to find the best match
    for pred in predicted_texts:
        matches = match_word_to_names(pred, name_list)
        best_match = ""
        if matches:
            # Sort matches by similarity (descending) and take the top one
            top_match = max(matches, key=lambda x: x[1])
            matched_name, similarity = top_match
            # Use a similarity threshold (e.g., 0.8) to ensure quality
            if similarity >= 0.8:
                best_match = matched_name
                print(f"Best match for '{pred}': {matched_name} (Similarity: {similarity:.2f})")
            else:
                print(f"No high-confidence match for '{pred}' (best similarity: {similarity:.2f})")
        else:
            print(f"No matches found for '{pred}'")

        output.append({
            "predicted_text": pred,
            "best_match": best_match
        })

    # Convert output to a JSON-like string with unquoted keys
    def to_unquoted_json(obj):
        if isinstance(obj, list):
            return "[" + ", ".join(to_unquoted_json(item) for item in obj) + "]"
        if isinstance(obj, dict):
            items = []
            for key, value in obj.items():
                # Format value: strings are quoted, others are not
                if isinstance(value, str):
                    # Escape double quotes in the value
                    escaped_value = value.replace('"', '\\"')
                    formatted_value = f'"{escaped_value}"'
                else:
                    formatted_value = str(value)
                items.append(f"{key}: {formatted_value}")
            return "{" + ", ".join(items) + "}"
        return str(obj)

    return to_unquoted_json(output)