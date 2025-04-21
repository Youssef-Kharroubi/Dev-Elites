import tensorflow as tf
from ..DB.model_store import load_model

def load_model_from_db(name, version, output_path="temp_model.h5"):
    """
    Loads the model from Azure Blob Storage and returns the TensorFlow model.
    :param name: Model name
    :param version: Model version
    :param output_path: Local path to save the downloaded model
    :return: Loaded TensorFlow model
    """
    load_model(name, version, output_path)
    model = tf.keras.models.load_model(output_path)
    return model