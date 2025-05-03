import os
import cv2
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import easyocr
from thefuzz import fuzz
import pandas as pd
from ultralytics import YOLO

YOLO_MODEL_PATH = "../../models/best.pt"
ARABIC_NAMES_PATH = "../../models/dataset_names.csv"
TEMPLATE = "STAR"  
LANG = "fr"

yolo_model = YOLO(YOLO_MODEL_PATH)
ocr_reader = easyocr.Reader([LANG], gpu=False)
trocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")

class_names = [
    "nom et prenom de adherent", "matricule cnam", "matricule de adherent", 
    "addresse de ladherent", "numero cin ou passeport", "nom et prenom du malade",
    "date de naissance", "date", "designation", "honoraire", "id"
]

def run_detection(image):
    return yolo_model(image, imgsz=640, device=None)

def crop_relevant_boxes(image, results):
    crops = {}
    for result in results:
        boxes = result.boxes.xyxy
        class_ids = result.boxes.cls
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            class_id = int(class_ids[i])
            label = class_names[class_id]
            if label in ["designation", "date", "honoraire"]:  
                continue
            if x2 > x1 and y2 > y1:
                cropped = image[y1:y2, x1:x2]
                cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)  
                crops[label.replace(" ", "_")] = cropped_rgb  
    return crops

def horizontal_proximity(box1, box2, proximity_thresh=40, alignment_thresh=15):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    if abs(x1_min - x2_max) < proximity_thresh or abs(x2_min - x1_max) < proximity_thresh:
        y_center_1 = (y1_min + y1_max) / 2
        y_center_2 = (y2_min + y2_max) / 2
        return abs(y_center_1 - y_center_2) < alignment_thresh
    return False

def merge_boxes(boxes):
    merged = []
    used = [False] * len(boxes)
    for i in range(len(boxes)):
        if used[i]: continue
        new_box = boxes[i]
        used[i] = True
        for j in range(i + 1, len(boxes)):
            if not used[j] and horizontal_proximity(new_box, boxes[j]):
                x1, y1, x2, y2 = new_box
                bx1, by1, bx2, by2 = boxes[j]
                new_box = [
                    min(x1, bx1), min(y1, by1),
                    max(x2, bx2), max(y2, by2)
                ]
                used[j] = True
        merged.append(new_box)
    return merged

def recognize_text_with_trocr(image_crops):
    field_text_pairs = {}
    for crop_name, crop in image_crops.items():
        try:
            pixel_values = trocr_processor(images=crop, return_tensors="pt").pixel_values
            generated_ids = trocr_model.generate(pixel_values)
            predicted_text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            predicted_text = predicted_text.strip()
            
            field_text_pairs[crop_name] = predicted_text
            
            print(f"{crop_name.replace('_', ' ').title()}: {predicted_text}")
            
        except Exception as e:
            field_text_pairs[crop_name] = f"Error: {str(e)}"
            print(f"Error with crop {crop_name}: {str(e)}")  
    
    return field_text_pairs

def match_word_to_names(word, name_list, threshold=60):
    matches = []
    for name in name_list:
        similarity = fuzz.ratio(word.lower(), name.lower())
        if similarity >= threshold:
            matches.append((name, similarity))
    if not matches:  # If no matches are found
        matches.append((word, "No matching names"))
    return matches

def process_image(image_path, name_list):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image {image_path}")
        return
    
    results = run_detection(image)
    crops = crop_relevant_boxes(image, results)
    
    recognized_texts = recognize_text_with_trocr(crops)
    
    adherent_name = None
    malade_name = None
    
    for crop_name, text in zip(crops.keys(), recognized_texts.values()):
        if "nom_et_prenom_de_adherent" in crop_name:
            adherent_name = text
        elif "nom_et_prenom_du_malade" in crop_name:
            malade_name = text
    
    if adherent_name:
        adherent_name_splitted = [word for word in adherent_name.split(' ') if word]
        for name in adherent_name_splitted:
            matches = match_word_to_names(name, name_list, threshold=80)
            for matched_name, similarity in matches:
                if similarity == "No matching names":
                    print(f"No match found for adherent name: {name}")
                else:
                    print(f"Matched name for adherent: {matched_name} (Similarity: {similarity}%)")
    
    if malade_name:
        malade_name_splitted = [word for word in malade_name.split(' ') if word]
        for name in malade_name_splitted:
            matches = match_word_to_names(name, name_list, threshold=80)
            for matched_name, similarity in matches:
                if similarity == "No matching names":
                    print(f"No match found for malade name: {name}")
                else:
                    print(f"Matched name for malade: {matched_name} (Similarity: {similarity}%)")


#calling of the code
df = pd.read_csv(ARABIC_NAMES_PATH)
name_list = df['names'].dropna().astype(str).tolist()

image_path = "hi2.jpg"  
process_image(image_path, name_list)
