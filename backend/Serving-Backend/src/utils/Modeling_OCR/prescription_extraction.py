import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def recognize_text_from_image(image_path):
    # Step 1: Preprocessing
    def preprocess(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sharpened = cv2.filter2D(gray, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
        kernel = np.ones((1, 1), np.uint8)
        denoised = cv2.medianBlur(cv2.morphologyEx(cv2.erode(cv2.dilate(sharpened, kernel, iterations=1), kernel, iterations=1), cv2.MORPH_CLOSE, kernel), 3)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        inverted = cv2.bitwise_not(contrast)
        thicker = cv2.dilate(inverted, np.ones((2,2),np.uint8), iterations=1)
        return cv2.bitwise_not(thicker)

    def segment_lines(binary):
        projection = gaussian_filter1d(np.sum(binary, axis=1), sigma=3)
        threshold = max(np.max(projection) * 0.01, 50)
        lines = []
        start = None
        for i, val in enumerate(projection):
            if val > threshold and start is None:
                start = i
            elif val <= threshold and start is not None:
                if i - start >= 30:
                    lines.append((start, i))
                start = None
        if start is not None and len(projection) - start >= 30:
            lines.append((start, len(projection)))
        merged = []
        if lines:
            current_start, current_end = lines[0]
            for s, e in lines[1:]:
                if s - current_end <= 30:
                    current_end = e
                else:
                    merged.append((current_start, current_end))
                    current_start, current_end = s, e
            merged.append((current_start, current_end))
        padding = 60
        return [binary[max(0,s-padding):min(binary.shape[0],e+padding), :] for s,e in merged]

    def segment_words(line_img):
        _, binary = cv2.threshold(line_img, 127, 255, cv2.THRESH_BINARY)
        height, width = binary.shape
        gaps = []
        gap_start = None
        gap_count = 0
        for col in range(width):
            if np.all(binary[:, col] < 100):
                if gap_start is None:
                    gap_start = col
                gap_count += 1
            else:
                if gap_start is not None and gap_count >= 100:
                    gaps.append((gap_start, col))
                gap_start = None
                gap_count = 0
        if gap_start is not None and gap_count >= 100:
            gaps.append((gap_start, width))
        word_boundaries = []
        if not gaps:
            word_boundaries.append((0, width))
        else:
            if gaps[0][0] > 0:
                word_boundaries.append((0, gaps[0][0]))
            for i in range(len(gaps) - 1):
                start = gaps[i][1]
                end = gaps[i + 1][0]
                if end - start >= 50:
                    word_boundaries.append((start, end))
            if gaps[-1][1] < width:
                word_boundaries.append((gaps[-1][1], width))
        return [binary[:, max(0,s-2):min(width,e+2)] for s,e in word_boundaries if (e-s) > 50]

    def recognize_word(img):
        rgb_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(rgb_img).convert("RGB")
        pixel_values = processor(pil_img, return_tensors="pt").pixel_values.to(device)
        generated_ids = model.generate(pixel_values)
        return processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at: {image_path}")

    processed = preprocess(img)
    _, binary = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, binary = cv2.threshold(binary, 127, 255, cv2.THRESH_BINARY)

    lines = segment_lines(binary)
    final_text = []
    for line_img in lines:
        words = segment_words(line_img)
        line_text = ' '.join(recognize_word(word) for word in words)
        final_text.append(line_text)

    return '\n'.join(final_text)

text = recognize_text_from_image("prescription.jpg")
print(text)