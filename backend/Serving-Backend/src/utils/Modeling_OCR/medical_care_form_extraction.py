import cv2
import easyocr
import numpy as np
from ultralytics import YOLO
from PIL import Image
import matplotlib.pyplot as plt
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import re
import pandas as pd

model = YOLO("../../models/best.pt", task="detect")
predicted_company="STAR"

image = cv2.imread("ayoub.jpg")

class_names = [
    "nom et prenom de adherent",
    "matricule cnam",
    "matricule de adherent",
    "addresse de ladherent",
    "numero cin ou passeport",
    "nom et prenom du malade",
    "date de naissance",
    "date",
    "designation",
    "honoraire",
    "id"
]

def process_detections(image, results, class_names):
    crop_counter = 1
    cropped_regions = []
    for result in results:
        boxes = result.boxes.xyxy  
        confidences = result.boxes.conf
        class_ids = result.boxes.cls

        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = map(int, box)
            class_id = int(cls_id)
            label = class_names[class_id]
            confidence = float(conf)
            print(f"Confidence is: {confidence:.2f}")
            if label not in ["designation", "date", "honoraire"]:
                if x2 > x1 and y2 > y1:
                    cropped_image = image[y1:y2, x1:x2]
                    cropped_regions.append((label, cropped_image))
                    crop_counter += 1
    return cropped_regions

results = model(image, imgsz=640, device=None)  
cropped_regions = process_detections(image, results, class_names)

def horizontal_proximity(box1, box2, proximity_thresh=40, alignment_thresh=15):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    if abs(x1_min - x2_max) < proximity_thresh or abs(x2_min - x1_max) < proximity_thresh:
        y_center_1 = (y1_min + y1_max) / 2
        y_center_2 = (y2_min + y2_max) / 2
        if abs(y_center_1 - y_center_2) < alignment_thresh:
            return True
    return False


def merge_boxes(boxes):
    merged = []
    used = [False] * len(boxes)

    for i in range(len(boxes)):
        if used[i]:
            continue
        x1, y1, x2, y2 = boxes[i]
        new_box = [x1, y1, x2, y2]
        used[i] = True
        for j in range(i + 1, len(boxes)):
            if not used[j] and horizontal_proximity(new_box, boxes[j]):
                bx1, by1, bx2, by2 = boxes[j]
                new_box = [
                    min(new_box[0], bx1),
                    min(new_box[1], by1),
                    max(new_box[2], bx2),
                    max(new_box[3], by2)
                ]
                used[j] = True
        merged.append(new_box)
    return merged

def detect_all_words(image, lang='fr', proximity_threshold=40, predicted_company="STAR"):
    reader = easyocr.Reader([lang], gpu=False)
    results = reader.readtext(image, detail=1, paragraph=False, min_size=10, text_threshold=0.3)

    if len(results) == 0:
        print("No text detected.")
        return []

    raw_boxes = []
    for (bbox, text, prob) in results:
        (tl, tr, br, bl) = bbox
        x_min = int(min([pt[0] for pt in bbox]))
        y_min = int(min([pt[1] for pt in bbox]))
        x_max = int(max([pt[0] for pt in bbox]))
        y_max = int(max([pt[1] for pt in bbox]))
        raw_boxes.append([x_min, y_min, x_max, y_max])

    merged_boxes = merge_boxes(raw_boxes)
    
    cropped_regions = []
    for idx, (x1, y1, x2, y2) in enumerate(merged_boxes):
        if predicted_company in ["BH", "CNAM"]:
            if y2 > y1 and x2 > x1:
                cropped = image[y1:y2, x1:x2]
                cropped_regions.append(cropped)
        else:
            if (y2 - y1) > 40 and (x2 - x1) > 40:
                cropped = image[y1:y2, x1:x2]
                cropped_regions.append(cropped)
    return cropped_regions

cropped_text_regions = []

for label, cropped_image in cropped_regions:
    detected_words = detect_all_words(cropped_image, predicted_company=predicted_company)
    
    if detected_words:
        for idx, word_image in enumerate(detected_words, start=1):
            cropped_text_regions.append((label, word_image))


adherent_name = []
matricule_cnam = []
matricule_adherent = []
adresse_adherent = []
cin_ou_passeport = []
malade_name = []
date_naissance = []
id_field = []

def extract_texts_from_images(cropped_regions):
    global adherent_name, malade_name, matricule_cnam, matricule_adherent, adresse_adherent, cin_ou_passeport, id_field, date_naissance
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

    extracted_texts = {}
    region_index = 0

    for label, cropped_image in cropped_regions:
        try:
            image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            pixel_values = processor(images=image, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            predicted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            extracted_texts[label] = predicted_text

            if "nom et prenom de adherent" in label:
                adherent_name.append(predicted_text)
            elif "matricule cnam" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                matricule_cnam.append(predicted_text)
            elif "matricule de adherent" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                matricule_adherent.append(predicted_text)
            elif "addresse de ladherent" in label:
                adresse_adherent.append(predicted_text)
            elif "numero cin ou passeport" in label:
                predicted_text = re.sub(r'[^0-9]', '', predicted_text)
                cin_ou_passeport.append(predicted_text)
            elif "nom et prenom du malade" in label:
                malade_name.append(predicted_text)
            elif "date de naissance" in label:
                predicted_text = re.sub(r'[^0-9/]', '', predicted_text)
                date_naissance.append(predicted_text)
            elif label.startswith("id") or "id_" in label:
                predicted_text = re.sub(r'[^0-9/]', '', predicted_text)
                id_field.append(predicted_text)

            print(f"Extracted text from {label}: {predicted_text}")
            region_index += 1

        except Exception as e:
            print(f"Error processing {label}: {str(e)}")
            extracted_texts[f"{label}"] = "Error: Could not extract text"

#call of the code
extract_texts_from_images(cropped_text_regions)