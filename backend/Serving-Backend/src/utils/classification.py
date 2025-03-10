import tensorflow as tf
from .preprocess import preprocess_image

def classify_document(image_path, model):
    img = preprocess_image(image_path)
    img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
    img_array = tf.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]
    return "Medical Care Form" if prediction < 0.5 else "Prescription"