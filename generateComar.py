import cv2
import numpy as np
import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import glob

# Paths configuration
COMAR_TEMPLATE_PATH = r"C:\Users\MSI\Downloads\ComarAssurance_page-0001.jpg" # CHANGE THIS PATH
MAPPING_JSON_PATH = r"field_mapping_comar.json"  # Path to your mapping JSON file
HANDWRITING_FONTS_DIR = r"C:\Users\MSI\Desktop\4DS1\Test101OCR\GeneratedTry\Handwritings"
OUTPUT_DIR = r"C:\Users\MSI\Desktop\Test101OCR\GeneratedTry\Output"  # Output directory for generated forms
NUM_SAMPLES = 500  # Number of forms to generate

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load all available handwriting fonts
def load_handwriting_fonts(fonts_dir, size_range=(50, 60)):  # Increased font size range
    font_files = glob.glob(os.path.join(fonts_dir, "*.ttf"))
    font_files.extend(glob.glob(os.path.join(fonts_dir, "*.otf")))
    
    fonts = []
    for font_file in font_files:
        try:
            # Get random font size within range
            font_size = random.randint(size_range[0], size_range[1])
            font = ImageFont.truetype(font_file, font_size)
            fonts.append(font)
        except Exception as e:
            print(f"Could not load font {font_file}: {e}")
    
    if not fonts:
        # Fallback to default font if no fonts are loaded
        print("No handwriting fonts loaded. Using default font.")
        fonts.append(ImageFont.load_default())
    
    return fonts

# Generate random data for fields
def generate_random_data():
    # Generate NUMERO_CONTRAT in format XXX X XXXXX X
    part1 = '  '.join(str(random.randint(0, 9)) for _ in range(3))
    part2 = str(random.randint(0, 9))
    part3 = '  '.join(str(random.randint(0, 9)) for _ in range(5))
    part4 = str(random.randint(0, 9))
    numero_contrat = f"{part1} {part2} {part3} {part4}"
    
    # Generate MATRICULE in format XXXXXX (exactly 6 digits)
    matricule = ' '.join(str(random.randint(0, 9)) for _ in range(6))
    
    data = {
        "IDENTIFIANT_UNIQUE": f"{random.randint(10000, 99999)}",
        "ENTREPRISE": random.choice([
            "TechSolutions SA", "GlobalCorp", "MediHealth", "InnoTech", 
            "EcoGreen", "DataStream", "SecureNet", "BuildPro", 
            "TransGlobal", "FoodDelights"
        ]),
        "NUMERO_CONTRAT": numero_contrat,
        "ADHERENT": f"{random.choice(['M.', 'Mme.'])} {random.choice(['Ben Ahmed', 'Trabelsi', 'Mejri', 'Chaabane', 'Gharbi', 'Jebali', 'Hamdi', 'Kouki', 'Lahmar', 'Riahi'])}",
        "MATRICULE": matricule,
        "ADRESSE": random.choice([
            "12 Rue de la Liberté, Tunis", 
            "45 Avenue Habib Bourguiba, Sousse",
            "8 Rue Ibn Khaldoun, Sfax",
            "23 Avenue de Carthage, Bizerte",
            "17 Rue de la République, Monastir",
            "5 Avenue Mohamed V, Gabès",
            "31 Rue Mokhtar Attia, Kairouan",
            "9 Boulevard de l'Environnement, Nabeul",
            "27 Rue Ali Belhouane, Gafsa",
            "14 Avenue de Paris, Ariana"
        ])
    }
    return data

def add_text_to_image(image, text, bbox, font, text_color=(0, 0, 0)):
    """Add text within the bounding box using PIL"""
    # Convert OpenCV image to PIL Image
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Calculate text position (center of bbox)
    x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
    
    # Get text size using font.getbbox()
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate position to center text in bbox
    text_x = x1 + (x2 - x1 - text_width) // 2
    text_y = y1 + (y2 - y1 - text_height) // 2
    
    # Ensure text stays within bbox
    text_x = max(x1, text_x)
    text_y = max(y1, text_y)
    
    # Add text to image
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Convert back to OpenCV image
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def generate_filled_form(template_path, mapping_data, fonts, output_path, form_data):
    """Generate a filled form with handwritten text"""
    # Load template image
    img = cv2.imread(template_path)
    if img is None:
        print(f"ERROR: Could not load template image at {template_path}")
        return False
    
    # For each field, add text with random handwriting font
    for field_name, field_value in form_data.items():
        if field_name in mapping_data:
            bbox = {
                'x1': mapping_data[field_name]['x1'],
                'y1': mapping_data[field_name]['y1'],
                'x2': mapping_data[field_name]['x2'],
                'y2': mapping_data[field_name]['y2']
            }
            
            # Choose a random font for this field
            font = random.choice(fonts)
            
            # Add text to image
            img = add_text_to_image(img, field_value, bbox, font)
    
    # Save the generated form
    cv2.imwrite(output_path, img)
    return True

def main():
    # Load mapping data
    try:
        with open(MAPPING_JSON_PATH, 'r') as f:
            mapping_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load mapping data: {e}")
        return
    
    # Load handwriting fonts
    fonts = load_handwriting_fonts(HANDWRITING_FONTS_DIR)
    if not fonts:
        print(f"ERROR: No fonts loaded from {HANDWRITING_FONTS_DIR}")
        return
    
    print(f"Loaded {len(fonts)} handwriting fonts")
    
    # Generate forms
    print(f"Generating {NUM_SAMPLES} sample forms...")
    for i in range(1, NUM_SAMPLES + 1):
        # Generate random data
        form_data = generate_random_data()
        
        # Define output path
        output_path = os.path.join(OUTPUT_DIR, f"comar_form_{i:03d}.jpg")
        
        # Generate filled form
        success = generate_filled_form(
            COMAR_TEMPLATE_PATH,
            mapping_data,
            fonts,
            output_path,
            form_data
        )
        
        if success:
            print(f"Generated form {i}/{NUM_SAMPLES}: {output_path}")
    
    print(f"Done! Generated {NUM_SAMPLES} forms in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()