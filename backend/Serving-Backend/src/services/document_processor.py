from ..utils.insurer_classification import classify_images
from tensorflow.keras.models import load_model
import os

class DocumentProcessor:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        binary_model_path = os.path.join(base_path, '..', 'models', 'CNN_model.h5')
        insurance_model_path = os.path.join(base_path, '..', 'models', 'insurance_classifier_vgg16.h5')

        self.binary_model = load_model(binary_model_path)
        self.insurance_model = load_model(insurance_model_path)

    def process_image(self, image_path):
        result = classify_images( self.binary_model,self.insurance_model,image_path)
        return result
