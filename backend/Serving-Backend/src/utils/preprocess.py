from PIL import Image, ImageEnhance
import numpy as np
import os

TARGET_SIZE = (256, 256)

def preprocess_image(image_path, output_path=None):

    image = Image.open(image_path)
    gray_image = image.convert("L")

    enhancer = ImageEnhance.Sharpness(gray_image)
    sharp_image = enhancer.enhance(2.0)

    resized_image = sharp_image.resize(TARGET_SIZE, Image.LANCZOS)

    final_image = ImageEnhance.Sharpness(resized_image).enhance(1.5)

    final_image_rgb = np.stack([np.array(final_image)] * 3, axis=-1)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        Image.fromarray(final_image_rgb).save(output_path, dpi=(300, 300), quality=95)

    return final_image_rgb
