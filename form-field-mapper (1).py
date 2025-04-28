import cv2
import numpy as np
import json
import os

# CHANGE THIS PATH to your COMAR template JPEG image
COMAR_IMAGE_PATH = r"C:\Users\MSI\Downloads\ComarAssurance_page-0001.jpg"  # CHANGE THIS PATH
OUTPUT_JSON_DIR = "."  # Directory to save JSON files

class FormFieldMapper:
    def __init__(self, template_path, output_json, fields_to_map=None):
        # Load the template image
        self.template_path = template_path
        self.img = cv2.imread(template_path)
        if self.img is None:
            print(f"ERROR: Could not load image at {template_path}")
            exit(1)
        
        self.height, self.width = self.img.shape[:2]
        self.field_map = {}
        self.current_field = None
        self.output_json = output_json
        
        # Create a window to display the image with proper proportions
        cv2.namedWindow('Form Mapper', cv2.WINDOW_NORMAL)
        
        # Calculate appropriate window size while maintaining aspect ratio
        max_display_height = 900  # Maximum display height (adjust as needed)
        max_display_width = 1600  # Maximum display width (adjust as needed)
        
        # Calculate scaling factor to maintain aspect ratio
        height_scale = max_display_height / self.height
        width_scale = max_display_width / self.width
        scale = min(height_scale, width_scale)
        
        # Set window size
        display_width = int(self.width * scale)
        display_height = int(self.height * scale)
        cv2.resizeWindow('Form Mapper', display_width, display_height)
        
        # Set up mouse callback
        cv2.setMouseCallback('Form Mapper', self.mouse_callback)
        
        # List of fields to map
        self.fields_to_map = fields_to_map or []
        self.current_field_index = 0
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for marking field positions"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start marking a field
            if self.current_field:
                self.field_map[self.current_field] = {'x1': x, 'y1': y}
                print(f"Starting point for {self.current_field}: ({x}, {y})")
                
        elif event == cv2.EVENT_LBUTTONUP:
            # Complete marking a field
            if self.current_field and self.current_field in self.field_map:
                self.field_map[self.current_field].update({'x2': x, 'y2': y})
                print(f"Field {self.current_field} mapped: {self.field_map[self.current_field]}")
                
                # Draw rectangle on the image
                x1, y1 = self.field_map[self.current_field]['x1'], self.field_map[self.current_field]['y1']
                cv2.rectangle(self.img, (x1, y1), (x, y), (0, 255, 0), 2)
                
                # Move to next field
                self.current_field = None
                self.current_field_index += 1
                if self.current_field_index < len(self.fields_to_map):
                    self.set_current_field(self.fields_to_map[self.current_field_index])
                else:
                    print("All fields mapped! Press 's' to save or 'q' to quit without saving.")
    
    def set_current_field(self, field_name):
        """Set the current field being mapped"""
        self.current_field = field_name
        print(f"Click and drag to mark the position of: {field_name}")
    
    def run(self):
        """Main loop for the mapper"""
        print("=== Form Field Mapper ===")
        print("Instructions:")
        print("1. Click and drag on the image to mark each field")
        print("2. Press 's' to save the mapping to a JSON file")
        print("3. Press 'q' to quit without saving")
        print("4. Press 'r' to reset current field")
        print("5. Press 'p' to go back to previous field")
        
        # Start with the first field
        if self.fields_to_map:
            self.set_current_field(self.fields_to_map[0])
        
        while True:
            # Display the image
            cv2.imshow('Form Mapper', self.img)
            
            # Wait for key press
            key = cv2.waitKey(1) & 0xFF
            
            # Check for save or quit
            if key == ord('s'):
                self.save_mapping()
                break
            elif key == ord('q'):
                break
            elif key == ord('r'):
                # Reset current field to remap it
                if self.current_field and self.current_field in self.field_map:
                    del self.field_map[self.current_field]
                    print(f"Reset mapping for {self.current_field}")
            elif key == ord('p'):
                # Go to previous field
                if self.current_field_index > 0:
                    self.current_field_index -= 1
                    prev_field = self.fields_to_map[self.current_field_index]
                    if prev_field in self.field_map:
                        del self.field_map[prev_field]
                    self.current_field = None
                    self.set_current_field(prev_field)
                    # Redraw image to remove previous rectangle
                    self.img = cv2.imread(self.template_path)
                    if self.img is None:
                        print(f"ERROR: Could not reload image.")
                        break
                    # Redraw remaining rectangles
                    for field, coords in self.field_map.items():
                        if 'x1' in coords and 'y1' in coords and 'x2' in coords and 'y2' in coords:
                            cv2.rectangle(self.img, 
                                        (coords['x1'], coords['y1']), 
                                        (coords['x2'], coords['y2']), 
                                        (0, 255, 0), 2)
        
        cv2.destroyAllWindows()
    
    def save_mapping(self):
        """Save the field mapping to a JSON file"""
        # Convert to percentage-based and pixel-based coordinates
        full_map = {}
        for field, coords in self.field_map.items():
            if 'x1' in coords and 'y1' in coords and 'x2' in coords and 'y2' in coords:
                full_map[field] = {
                    'x1_pct': round(coords['x1'] / self.width, 4),
                    'y1_pct': round(coords['y1'] / self.height, 4),
                    'x2_pct': round(coords['x2'] / self.width, 4),
                    'y2_pct': round(coords['y2'] / self.height, 4),
                    'center_x_pct': round((coords['x1'] + coords['x2']) / (2 * self.width), 4),
                    'center_y_pct': round((coords['y1'] + coords['y2']) / (2 * self.height), 4),
                    # Absolute coordinates
                    'x1': coords['x1'],
                    'y1': coords['y1'],
                    'x2': coords['x2'],
                    'y2': coords['y2'],
                    'center_x': (coords['x1'] + coords['x2']) // 2,
                    'center_y': (coords['y1'] + coords['y2']) // 2
                }
        
        output_path = os.path.join(OUTPUT_JSON_DIR, self.output_json)
        with open(output_path, 'w') as f:
            json.dump(full_map, f, indent=4)
        
        print(f"Mapping saved to {output_path}")

def map_comar_template():
    """Map the COMAR form with specific required fields"""
    fields_to_map = [
        "IDENTIFIANT_UNIQUE",
        "ENTREPRISE",
        "NUMERO_CONTRAT",
        "ADHERENT",
        "MATRICULE",
        "ADRESSE"
    ]
    
    mapper = FormFieldMapper(COMAR_IMAGE_PATH, "field_mapping_comar.json", fields_to_map)
    mapper.run()

def main():
    """Main function to run the COMAR form mapper"""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    
    print("=== COMAR Form Field Mapper ===")
    print(f"Using template: {COMAR_IMAGE_PATH}")
    map_comar_template()

if __name__ == "__main__":
    main()