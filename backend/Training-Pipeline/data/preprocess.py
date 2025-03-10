from PIL import Image, ImageEnhance
import os

TARGET_SIZE = (512, 512)

def preprocess_image(image_path, output_path):
    image = Image.open(image_path)
    gray_image = image.convert("L")
    enhancer = ImageEnhance.Sharpness(gray_image)
    sharp_image = enhancer.enhance(2.0)
    resized_image = sharp_image.resize(TARGET_SIZE, Image.LANCZOS)
    final_image = ImageEnhance.Sharpness(resized_image).enhance(1.5)
    final_image.save(output_path, dpi=(300, 300), quality=95)

def preprocess_dataset(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            preprocess_image(input_path, output_path)
    print(f"Preprocessed {input_dir} to {output_dir}")