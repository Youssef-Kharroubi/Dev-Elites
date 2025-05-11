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
    logger.debug(f"predict_text started: image={image_path}, excel={excel_path}")
    try:
        # Validate inputs
        logger.debug("Validating input paths")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        # Load Excel data
        logger.debug("Loading and cleaning Excel data")
        name_list = load_and_clean_data(excel_path)
        logger.debug(f"Excel data loaded: {len(name_list)} entries")

        # Preprocess image
        logger.debug("Preprocessing image for detection")
        processed_img = preprocess_image_for_detection(image_path)
        logger.debug(f"Processed image shape: {processed_img.shape if hasattr(processed_img, 'shape') else 'unknown'}")

        # Detect text with EasyOCR
        logger.debug("Detecting text with EasyOCR")
        results = detect_text(processed_img, reader_easy_ocr)
        logger.debug(f"EasyOCR detected {len(results)} text regions")

        predicted_texts = []
        output_results = []

        # Process each detected region (limit to 10 to reduce load)
        for idx, (bbox, text, prob) in enumerate(results[:10]):
            logger.debug(f"Processing region {idx+1}: text={text}, prob={prob}")
            try:
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = (int(top_left[0]), int(top_left[1]))
                bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                logger.debug(f"Region {idx+1} bbox: top_left={top_left}, bottom_right={bottom_right}")

                # Crop word image
                word_img = processed_img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                if word_img.shape[0] <= 0 or word_img.shape[1] <= 0:
                    logger.debug(f"Region {idx+1} skipped: invalid dimensions")
                    output_results.append({
                        "word_index": idx + 1,
                        "status": "skipped",
                        "reason": "invalid_dimensions"
                    })
                    continue

                # Classify text
                logger.debug(f"Preprocessing region {idx+1} for classification")
                word_img_preprocessed = preprocess_for_classification(word_img)
                logger.debug(f"Running classification for region {idx+1}")
                label, confidence = classify_text(word_img_preprocessed, classification_model)
                logger.debug(f"Region {idx+1} classified: label={label}, confidence={confidence}")
                output_results.append({
                    "word_index": idx + 1,
                    "classification": {
                        "label": label,
                        "confidence": float(confidence)
                    }
                })

                # Handle handwritten text with TROCR
                if label == "Handwritten":
                    logger.debug(f"Region {idx+1} is handwritten, running TROCR")
                    word_img_rgb = cv2.cvtColor(word_img, cv2.COLOR_GRAY2RGB)
                    recognized_text = recognize_handwritten_text(word_img_rgb, processor, trocr_model)
                    logger.debug(f"Region {idx+1} TROCR result: {recognized_text}")
                    if recognized_text:
                        is_valid, cleaned_text = is_valid_text(recognized_text)
                        logger.debug(f"Region {idx+1} text validation: valid={is_valid}, cleaned_text={cleaned_text}")
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
                    else:
                        logger.debug(f"Region {idx+1} TROCR returned no text")

                # # Free memory
                # del word_img, word_img_rgb, word_img_preprocessed
                # gc.collect()

            except Exception as e:
                logger.error(f"Error processing region {idx+1}: {str(e)}", exc_info=True)
                output_results.append({
                    "word_index": idx + 1,
                    "status": "error",
                    "reason": str(e)
                })
                continue

        logger.debug("Matching predicted texts to name list")
        matches_output = []
        for pred in predicted_texts:
            logger.debug(f"Matching text: {pred}")
            matches = match_word_to_names(pred, name_list)
            match_details = [
                {"name": matched_name, "similarity": float(similarity)}
                for matched_name, similarity in matches
            ] if matches else []
            matches_output.append({
                "predicted_text": pred,
                "matches": match_details
            })
        logger.debug(f"Matches found: {len(matches_output)}")

        # Combine results
        logger.debug("Returning results")
        result = {
            "results": output_results,
            "predicted_texts": predicted_texts,
            "matches": matches_output
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error in predict_text: {str(e)}", exc_info=True)
        raise
    finally:
        logger.debug("Cleaning up memory in predict_text")
        gc.collect()