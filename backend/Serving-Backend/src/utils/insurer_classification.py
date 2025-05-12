import os
import numpy as np
import logging
from PIL import Image, ImageEnhance
from tensorflow.keras.models import load_model
from .preprocess import preprocess_image

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
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
    return predicted_class,

def classify_images(binary_model, multi_model, image_path):
    binary_class_names = {0: "Medical Care Form", 1: "Prescription"}
    insurance_class_names = ['BH', 'CNAM', 'STAR']
    result = {}



    binary_class, binary_prob = predict_binary(binary_model, image_path)
    binary_class_name = binary_class_names[binary_class]

    if binary_class == 0:
        insurance_class = predict_insurance_company(multi_model, image_path, insurance_class_names)
        result = { "document_type":binary_class_name,"insurance_company":insurance_class}
    else:
        result = {"document_type":binary_class_name}


    return result
def classify_images_internal(binary_model,multi_model,image_path):
    binary_class_names = {0: "Medical Care Form", 1: "Prescription"}
    insurance_class_names = ['BH', 'CNAM', 'STAR']
    result = {}

    binary_class, binary_prob = predict_binary(binary_model, image_path)
    binary_class_name = binary_class_names[binary_class]
    if binary_class == 0:
        insurance_class = predict_insurance_company(multi_model, image_path, insurance_class_names)
        result = {"insurance_company": insurance_class}
    else:
        result = {"document_type": binary_class_name}
    return result