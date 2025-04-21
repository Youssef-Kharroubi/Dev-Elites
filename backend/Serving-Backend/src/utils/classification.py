import tensorflow as tf
import numpy as np
from PIL import Image
from .preprocess import preprocess_image
import os
import tempfile


def classify_document(image_path, model):
    # Create temporary path for preprocessed image
    temp_dir = tempfile.gettempdir()
    temp_output_path = os.path.join(temp_dir, f"preprocessed_{os.path.basename(image_path)}")

    # Preprocess image
    img = preprocess_image(image_path, temp_output_path)

    # Load preprocessed image and convert to array
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize to [0,1]

    # Log shape for debugging
    print("Input shape to model:", img_array.shape)

    # Predict
    prediction = model.predict(img_array)[0][0]

    # Clean up temporary file
    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)

    return "Medical Care Form" if prediction < 0.5 else "Prescription"