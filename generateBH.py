import random
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import string
import json

def random_name():
    first_names = ["Mohammed", "Ahmed", "Fatima", "Aisha", "Ali", "Omar", "Youssef", "Mariam", "Hassan", "Nour"]
    last_names = ["Benali", "El Amrani", "Bouchra", "Saidi", "Hakimi", "Bouazza", "Lahcen", "Mansouri", "Tahiri", "Chaoui"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def random_address():
    streets = ["Rue Hassan II", "Avenue Mohammed V", "Boulevard Zerktouni", "Rue Ibn Khaldoun", "Avenue des FAR"]
    cities = ["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir"]
    return f"{random.randint(1, 200)}, {random.choice(streets)}, {random.choice(cities)}"

def random_date(start_date=datetime(2023, 1, 1), end_date=datetime(2023, 12, 31)):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_days)

def random_id():
    return ''.join(random.choices(string.digits, k=8))

def random_mfn_number():
    # Generate a random MFN number with proper format
    return ''.join(random.choices(string.digits, k=10))

def format_date(date):
    return date.strftime("%d/%m/%Y")

def random_amount():
    # Generate a random amount between 100 and 5000 with two decimal places
    return f"{random.randint(100, 5000)},{random.randint(0, 99):02d}"

def random_medical_act():
    acts = ["Consultation", "ECG", "Radiographie", "Échographie", "Analyse", 
            "Prise de sang", "Vaccination", "Suivi", "Kinésithérapie", "Scanner"]
    return random.choice(acts)

def random_dental_care():
    cares = ["Détartrage", "Extraction", "Plombage", "Dévitalisation", 
             "Couronne", "Bridge", "Implant", "Nettoyage", "Consultation", "Radiographie"]
    return random.choice(cares)

def random_teeth_number():
    # Generate a random tooth number (from 11 to 48)
    region = random.randint(1, 4)
    tooth = random.randint(1, 8)
    return f"{region}{tooth}"

def random_coefficient():
    # Generate a random coefficient common in dental care
    coefficients = ["SC7", "SC9", "SC12", "SC15", "SC20", "SPR25", "SPR30", "SPR50", "SPR70"]
    return random.choice(coefficients)

def random_signature():
    # Generate random signature-like data
    signatures = ["Dr. Brahim", "Dr. Laila S.", "Dr. Ahmed H.", "Dr. Karim", "Dr. Salma", 
                  "Dr. Younes", "Dr. Nadia", "Dr. Mohamed", "Dr. Sanae", "Dr. Rachid"]
    return random.choice(signatures)

def fill_front_form(template_path, output_path, field_mapping_path):
    # Load the template image
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Load field mapping
    with open(field_mapping_path, 'r') as f:
        field_mapping = json.load(f)
    
    # Print the structure of field_mapping for debugging
    print("Field mapping keys:", field_mapping.keys())
    if "form_number" in field_mapping:
        print("form_number keys:", field_mapping["form_number"].keys())
    
    # Load fonts
    try:
        regular_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        # Fallback to default
        regular_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Generate random data
    patient_name = random_name()
    patient_address = random_address()
    contract_number = random_id()
    adherent_number = random_id()
    form_number = random_id()[:7]
    
    # Use center_x and center_y from field mapping instead of x and y
    form_pos = (field_mapping["form_number"]["center_x"], field_mapping["form_number"]["center_y"])
    contract_pos = (field_mapping["contract_number"]["center_x"], field_mapping["contract_number"]["center_y"])
    adherent_pos = (field_mapping["adherent_number"]["center_x"], field_mapping["adherent_number"]["center_y"])
    name_pos = (field_mapping["patient_name"]["center_x"], field_mapping["patient_name"]["center_y"])
    address_pos = (field_mapping["patient_address"]["center_x"], field_mapping["patient_address"]["center_y"])
    
    # Fill form number in upper right
    draw.text(form_pos, form_number, fill=(0, 0, 0), font=regular_font)
    
    # Fill contract information
    draw.text(contract_pos, contract_number, fill=(0, 0, 0), font=regular_font)
    draw.text(adherent_pos, adherent_number, fill=(0, 0, 0), font=regular_font)
    
    # Fill patient information
    draw.text(name_pos, patient_name, fill=(0, 0, 0), font=regular_font)
    draw.text(address_pos, patient_address, fill=(0, 0, 0), font=small_font)
    
    # Select a random beneficiary type (adherent, conjoint, or enfant)
    beneficiary_type = random.choice(["adherent", "conjoint", "enfant"])
    
    # Mark the appropriate checkbox
    if beneficiary_type == "adherent":
        checkbox_pos = (field_mapping["adherent_checkbox"]["center_x"], field_mapping["adherent_checkbox"]["center_y"])
    elif beneficiary_type == "conjoint":
        checkbox_pos = (field_mapping["conjoint_checkbox"]["center_x"], field_mapping["conjoint_checkbox"]["center_y"])
    else:  # enfant
        checkbox_pos = (field_mapping["enfant_checkbox"]["center_x"], field_mapping["enfant_checkbox"]["center_y"])
    
    # Draw an X in the checkbox
    draw.text((checkbox_pos[0], checkbox_pos[1]), "X", fill=(0, 0, 0), font=regular_font)
    
    # Add signature date
    signature_date = random_date()
    date_pos = (field_mapping["signature_date"]["center_x"], field_mapping["signature_date"]["center_y"])
    draw.text(date_pos, format_date(signature_date), fill=(0, 0, 0), font=regular_font)
    
    # Add a simple signature (just a line or scribble)
    signature_pos = (field_mapping["signature"]["center_x"], field_mapping["signature"]["center_y"])
    
    # Create a signature-like squiggle
    points = []
    start_x = signature_pos[0] - 40  # Start a bit to the left
    y = signature_pos[1]
    for i in range(20):
        x = start_x + i * 5
        y_offset = random.randint(-5, 5)
        points.append((x, y + y_offset))
    
    # Draw the signature
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(0, 0, 150), width=2)
    
    # Save the filled form
    img.save(output_path)
    print(f"Generated front form saved to {output_path}")
    
    # Return some of the generated data to keep consistency between front and back
    return {
        "patient_name": patient_name,
        "form_number": form_number
    }

def fill_back_form(template_path, output_path, field_mapping_path, front_data=None):
    # Load the template image
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Load field mapping
    with open(field_mapping_path, 'r') as f:
        field_mapping = json.load(f)
    
    # Load fonts
    try:
        regular_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        # Fallback to default
        regular_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Generate random data for all fields
    # Medical Section
    practitioner_mfn_number = random_mfn_number()
    
    # Use the same patient name from front if provided
    if front_data and "patient_name" in front_data:
        patient_name_medical = front_data["patient_name"]
    else:
        patient_name_medical = random_name()
    
    # Fill practitioner MFN number
    draw.text((field_mapping["practitioner_mfn_number"]["center_x"], 
               field_mapping["practitioner_mfn_number"]["center_y"]), 
              practitioner_mfn_number, fill=(0, 0, 0), font=regular_font)
    
    # Fill patient name
    draw.text((field_mapping["patient_name_medical"]["center_x"], 
               field_mapping["patient_name_medical"]["center_y"]), 
              patient_name_medical, fill=(0, 0, 0), font=regular_font)
    
    # Fill medical table with random data
    num_medical_entries = random.randint(3, 5)  # Generate 3-5 medical entries
    
    for i in range(num_medical_entries):
        # Calculate y-position for each row (evenly spaced within the column)
        row_height = (field_mapping["medical_dates_column"]["y2"] - field_mapping["medical_dates_column"]["y1"]) / (num_medical_entries + 1)
        y_pos = field_mapping["medical_dates_column"]["y1"] + row_height * (i + 1)
        
        # Generate entry data
        entry_date = format_date(random_date())
        entry_signature = random_signature()
        entry_act = random_medical_act()
        entry_fees = random_amount()
        entry_amount = random_amount()
        
        # Add date
        date_x = field_mapping["medical_dates_column"]["x1"] + 5
        draw.text((date_x, y_pos), entry_date, fill=(0, 0, 0), font=small_font)
        
        # Add signature
        signature_x = field_mapping["medical_signature_column"]["x1"] + 10
        draw.text((signature_x, y_pos), entry_signature, fill=(0, 0, 0), font=small_font)
        
        # Add act nature
        act_x = field_mapping["medical_act_nature_column"]["x1"] + 5
        draw.text((act_x, y_pos), entry_act, fill=(0, 0, 0), font=small_font)
        
        # Add fees
        fees_x = field_mapping["medical_fees_column"]["x1"] + 10
        draw.text((fees_x, y_pos), entry_fees, fill=(0, 0, 0), font=small_font)
        
        # Add amount
        amount_x = field_mapping["medical_amount_column"]["x1"] + 10
        draw.text((amount_x, y_pos), entry_amount, fill=(0, 0, 0), font=small_font)
    
    # Hospitalization Section
    hospitalization_mfn_number = random_mfn_number()
    draw.text((field_mapping["hospitalization_mfn_number"]["center_x"], 
               field_mapping["hospitalization_mfn_number"]["center_y"]), 
              hospitalization_mfn_number, fill=(0, 0, 0), font=regular_font)
    
    # Hospitalization data
    admission_date = random_date()
    discharge_date = random_date(admission_date, admission_date + timedelta(days=15))
    cost_amount = random_amount()
    
    # Add admission date
    draw.text((field_mapping["admission_date"]["center_x"], 
               field_mapping["admission_date"]["center_y"]), 
              format_date(admission_date), fill=(0, 0, 0), font=regular_font)
    
    # Add discharge date
    draw.text((field_mapping["discharge_date"]["center_x"], 
               field_mapping["discharge_date"]["center_y"]), 
              format_date(discharge_date), fill=(0, 0, 0), font=regular_font)
    
    # Add cost amount
    draw.text((field_mapping["cost_amount"]["center_x"], 
               field_mapping["cost_amount"]["center_y"]), 
              cost_amount, fill=(0, 0, 0), font=regular_font)
    
    # Add visa stamp (a simple circle with some text)
    stamp_x = (field_mapping["visa_stamp_area"]["x1"] + field_mapping["visa_stamp_area"]["x2"]) // 2
    stamp_y = (field_mapping["visa_stamp_area"]["y1"] + field_mapping["visa_stamp_area"]["y2"]) // 2
    stamp_radius = min((field_mapping["visa_stamp_area"]["x2"] - field_mapping["visa_stamp_area"]["x1"]),
                      (field_mapping["visa_stamp_area"]["y2"] - field_mapping["visa_stamp_area"]["y1"])) // 3
    
    # Draw stamp circle
    draw.ellipse((stamp_x - stamp_radius, stamp_y - stamp_radius, 
                  stamp_x + stamp_radius, stamp_y + stamp_radius), 
                 outline=(0, 0, 150), width=2)
    
    # Add stamp text
    draw.text((stamp_x - stamp_radius + 20, stamp_y - 10), 
              f"VISA\n{format_date(datetime.now())}", 
              fill=(0, 0, 150), font=small_font)
    
    # Dental Section
    dental_mfn_number = random_mfn_number()
    draw.text((field_mapping["dental_mfn_number"]["center_x"], 
               field_mapping["dental_mfn_number"]["center_y"]), 
              dental_mfn_number, fill=(0, 0, 0), font=regular_font)
    
    # Fill dental table with random data
    num_dental_entries = random.randint(2, 4)  # Generate 2-4 dental entries
    
    for i in range(num_dental_entries):
        # Calculate y-position for each row (evenly spaced within the column)
        row_height = (field_mapping["dental_dates_column"]["y2"] - field_mapping["dental_dates_column"]["y1"]) / (num_dental_entries + 1)
        y_pos = field_mapping["dental_dates_column"]["y1"] + row_height * (i + 1)
        
        # Generate entry data
        entry_date = format_date(random_date())
        entry_teeth = random_teeth_number()
        entry_care = random_dental_care()
        entry_coefficient = random_coefficient()
        entry_fees = random_amount()
        
        # Add date
        date_x = field_mapping["dental_dates_column"]["x1"] + 5
        draw.text((date_x, y_pos), entry_date, fill=(0, 0, 0), font=small_font)
        
        # Add teeth number
        teeth_x = field_mapping["dental_teeth_column"]["x1"] + 10
        draw.text((teeth_x, y_pos), entry_teeth, fill=(0, 0, 0), font=small_font)
        
        # Add care nature
        care_x = field_mapping["dental_care_nature_column"]["x1"] + 5
        draw.text((care_x, y_pos), entry_care, fill=(0, 0, 0), font=small_font)
        
        # Add coefficient
        coeff_x = field_mapping["dental_coefficient_column"]["x1"] + 10
        draw.text((coeff_x, y_pos), entry_coefficient, fill=(0, 0, 0), font=small_font)
        
        # Add fees
        fees_x = field_mapping["dental_fees_column"]["x1"] + 10
        draw.text((fees_x, y_pos), entry_fees, fill=(0, 0, 0), font=small_font)
    
    # Fill prosthesis table (simpler, just add some random X marks)
    prosthesis_x1 = field_mapping["prosthesis_table_area"]["x1"]
    prosthesis_y1 = field_mapping["prosthesis_table_area"]["y1"]
    prosthesis_x2 = field_mapping["prosthesis_table_area"]["x2"]
    prosthesis_y2 = field_mapping["prosthesis_table_area"]["y2"]
    
    # Add some X marks in random positions
    num_marks = random.randint(3, 6)
    for _ in range(num_marks):
        x = random.randint(prosthesis_x1 + 20, prosthesis_x2 - 20)
        y = random.randint(prosthesis_y1 + 20, prosthesis_y2 - 20)
        draw.text((x, y), "X", fill=(0, 0, 0), font=regular_font)
    
    # Add some marks to dental diagrams (random dots or X marks)
    # Soins diagram
    soins_x1 = field_mapping["dental_diagram_soins"]["x1"]
    soins_y1 = field_mapping["dental_diagram_soins"]["y1"]
    soins_x2 = field_mapping["dental_diagram_soins"]["x2"]
    soins_y2 = field_mapping["dental_diagram_soins"]["y2"]
    
    num_soins_marks = random.randint(2, 5)
    for _ in range(num_soins_marks):
        x = random.randint(soins_x1 + 20, soins_x2 - 20)
        y = random.randint(soins_y1 + 20, soins_y2 - 20)
        # Randomly choose between dot and X
        if random.choice([True, False]):
            draw.text((x, y), "X", fill=(0, 0, 150), font=small_font)
        else:
            draw.ellipse((x-3, y-3, x+3, y+3), fill=(0, 0, 150))
    
    # Prothese diagram
    prothese_x1 = field_mapping["dental_diagram_prothese"]["x1"]
    prothese_y1 = field_mapping["dental_diagram_prothese"]["y1"]
    prothese_x2 = field_mapping["dental_diagram_prothese"]["x2"]
    prothese_y2 = field_mapping["dental_diagram_prothese"]["y2"]
    
    num_prothese_marks = random.randint(1, 4)
    for _ in range(num_prothese_marks):
        x = random.randint(prothese_x1 + 20, prothese_x2 - 20)
        y = random.randint(prothese_y1 + 20, prothese_y2 - 20)
        # Randomly choose between dot and X
        if random.choice([True, False]):
            draw.text((x, y), "O", fill=(255, 0, 0), font=small_font)
        else:
            draw.rectangle((x-5, y-5, x+5, y+5), outline=(255, 0, 0), width=2)
    
    # Add reference to form number if provided from front
    if front_data and "form_number" in front_data:
        draw.text((field_mapping["dental_mfn_number"]["x1"] + 200, 
                   field_mapping["dental_mfn_number"]["y1"] - 20), 
                  f"Ref: {front_data['form_number']}", fill=(0, 0, 0), font=small_font)
    
    # Save the filled form
    img.save(output_path)
    print(f"Generated back page saved to {output_path}")

def generate_complete_form(front_template_path, back_template_path, front_field_mapping_path, back_field_mapping_path, output_dir, form_id=None):
    # Create a unique form ID if none is provided
    if form_id is None:
        form_id = random.randint(10000, 99999)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate front form
    front_output_path = os.path.join(output_dir, f"form_{form_id}_front.jpg")
    front_data = fill_front_form(front_template_path, front_output_path, front_field_mapping_path)
    
    # Generate back form using same patient data for consistency
    back_output_path = os.path.join(output_dir, f"form_{form_id}_back.jpg")
    fill_back_form(back_template_path, back_output_path, back_field_mapping_path, front_data)
    
    return front_output_path, back_output_path

def main():
    # Paths to template images
    front_template_path = r"C:\Users\MSI\Desktop\front.jpg"
    back_template_path = r"C:\Users\MSI\Desktop\back.jpg"
    
    # Paths to field mappings for templates
    front_field_mapping_path = r"C:\Users\MSI\Downloads\field_mapping_template1.json"
    back_field_mapping_path = r"C:\Users\MSI\Downloads\field_mapping_template2.json"
    
    # Create output directory
    output_dir = r"C:\Users\MSI\Desktop\Test101OCR\generated_forms"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate multiple forms
    num_forms = 5  # Change this to generate more or fewer forms
    
    print(f"Generating {num_forms} complete forms (front and back)...")
    
    for i in range(num_forms):
        form_id = random.randint(10000, 99999)
        front_path, back_path = generate_complete_form(
            front_template_path, 
            back_template_path, 
            front_field_mapping_path,
            back_field_mapping_path, 
            output_dir, 
            form_id
        )
        print(f"Generated form {i+1}/{num_forms} - ID: {form_id}")
    
    print(f"\nSuccessfully generated {num_forms} complete forms in {output_dir}")

if __name__ == "__main__":
    main()
