from PIL import Image, ImageEnhance
import os

TARGET_SIZE = (260, 260)  # Try 144x144 to match model expectation


def preprocess_image(image_path, output_path):
    # Load image
    image = Image.open(image_path).convert('RGB')  # Ensure RGB

    # Apply sharpness enhancement
    enhancer = ImageEnhance.Sharpness(image)
    sharp_image = enhancer.enhance(2.0)

    # Resize image
    resized_image = sharp_image.resize(TARGET_SIZE, Image.LANCZOS)

    # Apply second sharpness enhancement
    enhancer = ImageEnhance.Sharpness(resized_image)
    final_image = enhancer.enhance(1.5)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save preprocessed image
    final_image.save(output_path, dpi=(300, 300), quality=95)

    return final_image