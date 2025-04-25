import tensorflow as tf
import numpy as np
from PIL import Image
import os
import tempfile
from .preprocess import preprocess_image


def classify_document(image_path, binary_model, insurance_model):
    binary_class_names = {0: "Medical Care Form", 1: "Prescription"}
    insurance_class_names = ['BH', 'CNAM', 'STAR']

    temp_dir = tempfile.gettempdir()
    temp_output_path = os.path.join(temp_dir, f"preprocessed_{os.path.basename(image_path)}")
    img = preprocess_image(image_path, temp_output_path)

    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    print("Input shape to binary model:", img_array.shape)

    binary_prediction = binary_model.predict(img_array)[0][0]
    binary_class = 0 if binary_prediction < 0.5 else 1
    binary_class_name = binary_class_names[binary_class]

    result = {
        "filename": os.path.basename(image_path),
        "binary_class": binary_class_name,
        "binary_probability": float(binary_prediction),
    }

    if binary_class == 0:
        insurance_prediction = insurance_model.predict(img_array)[0]
        insurance_index = np.argmax(insurance_prediction)
        insurance_class = insurance_class_names[insurance_index]
        insurance_probability = insurance_prediction[insurance_index]

        result["insurance_class"] = insurance_class
        result["insurance_probability"] = float(insurance_probability)

    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)

    return result
