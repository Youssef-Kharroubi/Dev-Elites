import cv2
import numpy as np
import pandas as pd
import json
import easyocr
import re
import tensorflow as tf
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from thefuzz import fuzz

# processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
# trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

def load_and_clean_data(excel_path):
    """Load and clean the medicine dataset from an Excel file."""
    df = pd.read_excel('../../models/cleaned_file.xlsx')
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
    output_results = []

    for idx, (bbox, text, prob) in enumerate(results):
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = (int(top_left[0]), int(top_left[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))

        word_img = processed_img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        if word_img.shape[0] <= 0 or word_img.shape[1] <= 0:
            output_results.append({
                "word_index": idx + 1,
                "status": "skipped",
                "reason": "invalid_dimensions"
            })
            continue

        word_img_preprocessed = preprocess_for_classification(word_img)
        label, confidence = classify_text(word_img_preprocessed, classification_model)
        output_results.append({
            "word_index": idx + 1,
            "classification": {
                "label": label,
                "confidence": float(confidence)
            }
        })

        if label == "Handwritten":
            word_img_rgb = cv2.cvtColor(word_img, cv2.COLOR_GRAY2RGB)
            recognized_text = recognize_handwritten_text(word_img_rgb, processor, trocr_model)
            if recognized_text:
                is_valid, cleaned_text = is_valid_text(recognized_text)
                if is_valid and len(cleaned_text) > 2:
                    predicted_texts.append(cleaned_text)
                    output_results.append({
                        "word_index": idx + 1,
                        "status": "valid",
                        "recognized_text": cleaned_text,
                        "confidence": float(confidence)
                    })
                else:
                    output_results.append({
                        "word_index": idx + 1,
                        "status": "skipped",
                        "reason": "invalid_or_too_short",
                        "recognized_text": recognized_text
                    })

    matches_output = []
    for pred in predicted_texts:
        matches = match_word_to_names(pred, name_list)
        match_details = [
            {"name": matched_name, "similarity": float(similarity)}
            for matched_name, similarity in matches
        ] if matches else []
        matches_output.append({
            "predicted_text": pred,
            "matches": match_details
        })

    return json.dumps({
        "results": output_results,
        "predicted_texts": predicted_texts,
        "matches": matches_output
    }, indent=2)

# reader = easyocr.Reader(['fr'], gpu=False)
# cnn_model = tf.keras.models.load_model("../../models/text_classification_model.h5")
# image_path = "prescription1.jpeg"
# excel_path = "../../models/cleaned_file.xls"
#
# predict_text(image_path, excel_path, cnn_model,reader)