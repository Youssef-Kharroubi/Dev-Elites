from PIL import Image, ImageEnhance

TARGET_SIZE = (512, 512)

def preprocess_image(image_path):
    image = Image.open(image_path)
    gray_image = image.convert("L")
    enhancer = ImageEnhance.Sharpness(gray_image)
    sharp_image = enhancer.enhance(2.0)
    resized_image = sharp_image.resize(TARGET_SIZE, Image.LANCZOS)
    final_image = ImageEnhance.Sharpness(resized_image).enhance(1.5)
    return final_image