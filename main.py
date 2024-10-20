import fitz  # PyMuPDF
import pytesseract
import pandas as pd
from PIL import Image, ImageOps
from io import BytesIO
import os
import glob
import numpy as np
from skimage.metrics import structural_similarity as ssim
import cv2  # OpenCV

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Directory containing the PDF documents
pdf_folder = r"E:\Antony\College co-curriculars\ARXTLabs Internship\Tile Project\PDFs"

# Directory to save extracted images
output_dir = "extracted_images"
os.makedirs(output_dir, exist_ok=True)

# Initialize lists to store extracted data
data = []
symbols_data = []

# Function to preprocess image using OpenCV
def preprocess_image(image):
    # Convert PIL image to OpenCV format
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    height, width = image_cv.shape[:2]
    image_cv = cv2.resize(image_cv, (width * 2, height * 2), interpolation=cv2.INTER_LINEAR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    
    # Convert to binary
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # Convert back to PIL format
    image_pil = Image.fromarray(binary)
    
    return image_pil

# Function to extract text from an image using OCR
def extract_text_from_image(image):
    preprocessed_image = preprocess_image(image)
    return pytesseract.image_to_string(preprocessed_image)

# Function to crop a region from an image based on given coordinates
def crop_region(image, left, upper, right, lower):
    try:
        return image.crop((left, upper, right, lower))
    except ValueError as e:
        print(f"Error cropping region ({left}, {upper}, {right}, {lower}) from image: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while cropping region ({left}, {upper}, {right}, {lower}): {e}")
        return None

# Function to save an image and return its path
def save_image(image, base_path, name_suffix):
    image_path = os.path.join(output_dir, f"{base_path}_{name_suffix}.png")
    image.save(image_path)
    return image_path

# Function to preprocess and normalize images for comparison
def preprocess_image_for_comparison(image, target_size=(100, 100)):
    # Resize the image to a standard size
    resized_image = image.resize(target_size)
    gray_image = ImageOps.grayscale(resized_image)
    normalized_image = ImageOps.equalize(gray_image)
    return normalized_image

# Function to compare two images using SSIM
def compare_images(image1, image2):
    image1_array = np.array(image1)
    image2_array = np.array(image2)
    return ssim(image1_array, image2_array)

# Function to remove background and set it to white
def remove_background(image):
    image = image.convert("RGBA")
    datas = image.getdata()

    new_data = []
    for item in datas:
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    
    image.putdata(new_data)
    background = Image.new("RGBA", image.size, "WHITE")
    combined = Image.alpha_composite(background, image).convert("RGB")
    return combined

# Function to check if an image is blank
def is_blank_image(image):
    image = image.convert("L")
    np_image = np.array(image)
    return np.all(np_image == np_image[0])

# Extract symbols from specific pages and regions of each PDF and save their paths in the extracted_symbols.csv
def extract_symbols(pdf_path):
    symbols_key = {}
    doc = fitz.open(pdf_path)

    # Define the specific pages and their corresponding symbol coordinates
    symbols_info = {
        2: [
            [(572, 386, 614, 422)],  
            [(674, 429, 716, 465)],  
            [(606, 471, 648, 507)],  
            [(708, 513, 750, 549)],  
        ],
        4: [
            [(301, 89, 318, 103)],  
            [(324, 89, 340, 104)],  
            [(347, 89, 363, 104)],  
            [(369, 88, 385, 103)],  
            [(392, 89, 409, 103)],  
        ],
        5: [
            [(1014, 819, 1037, 842)],  
            [(1047, 819, 1070, 842)],  
            [(1078, 819, 1101, 842)], 
            [(1110, 820, 1133, 843)],  
            [(1142, 820, 1165, 843)],  
        ],
    }

    meanings = [
        "Anti Slip Surface",
        "Easy Installation",
        "Water Resistance",
        "High Durability",
        "Wall Tiles / Floor Tiles",
        "Random Design",
        "Fire Resistance",
        "Easy Maintenance",
        "Residential / Commercial Area"
    ]

    meaning_index = 0
    for page_num, symbol_coords_list in symbols_info.items():
        if page_num < len(doc):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            image = Image.open(BytesIO(img_data))

            for symbol_coords in symbol_coords_list:
                symbol_image = None
                for symbol_coord in symbol_coords:
                    region_image = crop_region(image, *symbol_coord)
                    if region_image and not is_blank_image(region_image):
                        symbol_image = region_image
                        break
                
                if symbol_image:
                    # Preprocess the symbol image
                    processed_symbol_image = preprocess_image_for_comparison(symbol_image)
                    
                    # Save the preprocessed image and get its path
                    symbol_image_path = save_image(processed_symbol_image, os.path.splitext(os.path.basename(pdf_path))[0], f"symbol_{meaning_index + 1}")
                    
                    # Store symbol data
                    symbols_key[f"symbol_{meaning_index + 1}"] = {
                        'path': symbol_image_path,
                        'meaning': meanings[meaning_index],
                        'image': processed_symbol_image
                    }
                    
                    symbols_data.append({
                        'Symbol': symbol_image_path,  # Save the full path
                        'Meaning': meanings[meaning_index]
                    })
                    meaning_index += 1

    # Save symbols data to CSV
    df_symbols = pd.DataFrame(symbols_data)
    df_symbols.to_csv("extracted_symbols.csv", index=False, columns=["Symbol", "Meaning"])

# Extract symbols from each PDF document in the folder
for pdf_path in glob.glob(os.path.join(pdf_folder, "*.pdf")):
    extract_symbols(pdf_path)

# Load symbols key from the extracted symbols CSV file
symbols_df = pd.read_csv("extracted_symbols.csv")
symbols_key = {}
for _, row in symbols_df.iterrows():
    symbol_path = row['Symbol']
    symbol_image = Image.open(symbol_path)
    symbols_key[symbol_path] = {
        'meaning': row['Meaning'],
        'image': preprocess_image_for_comparison(symbol_image)
    }

# Function to process each PDF document and extract tile details
def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(pdf_output_dir, exist_ok=True)

    # Iterate over each page in the PDF starting from the 4th page and ignoring the last page
    for page_num in range(3, len(doc) - 2):
        try:
            page = doc.load_page(page_num)
            
            # Convert the page to an image
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            image = Image.open(BytesIO(img_data))

            # Coordinates for regions
            design_name_region = (56, 54, 300, 91)  # Extended the width to capture full text
            tile_type_region = (57, 91, 232, 112)
            tile_design_region = (66, 138, 409, 478)
            design_preview_region = (441, 70, 1195, 796)
            size_tile_class_region = (53, 484, 296, 520)
            logo_regions = [
                (301, 89, 318, 103), (324, 89, 340, 104), (347, 89, 363, 104), (369, 88, 385, 103), (392, 89, 409, 103),
                (1014, 819, 1037, 842), (1047, 819, 1070, 842), (1078, 819, 1101, 842), (1110, 820, 1133, 843), (1142, 820, 1165, 843)
            ]

            # Extract text from specific regions
            design_name_text = extract_text_from_image(crop_region(image, *design_name_region)).strip()
            tile_type_text = extract_text_from_image(crop_region(image, *tile_type_region)).strip()
            size_tile_class_text = extract_text_from_image(crop_region(image, *size_tile_class_region)).strip()

            if design_name_text:
                design_name = design_name_text

                # Split size and tile class
                size_tile_class_split = size_tile_class_text.split('/')
                size = size_tile_class_split[0].strip() if len(size_tile_class_split) > 0 else 'Unknown'
                tile_class = size_tile_class_split[1].strip() if len(size_tile_class_split) > 1 else 'Unknown'

                # Extract and save tile design and design preview images
                tile_design_image = crop_region(image, *tile_design_region)
                tile_design_image_path = os.path.join(pdf_output_dir, f"{design_name}_tile_design.png")
                tile_design_image.save(tile_design_image_path)

                design_preview_image = crop_region(image, *design_preview_region)
                design_preview_image_path = os.path.join(pdf_output_dir, f"{design_name}_design_preview.png")
                design_preview_image.save(design_preview_image_path)

                # Extract logos, remove background, and their corresponding meanings
                characteristics = []
                for i, logo_coord in enumerate(logo_regions):
                    logo_image = crop_region(image, *logo_coord)
                    if logo_image and not is_blank_image(logo_image):
                        logo_image = remove_background(logo_image)
                        processed_logo_image = preprocess_image_for_comparison(logo_image)
                        logo_image_path = save_image(processed_logo_image, os.path.splitext(os.path.basename(pdf_path))[0], f"page_{page_num+1}_logo_{i+1}")

                        matched = False
                        for symbol_text, symbol_data in symbols_key.items():
                            similarity = compare_images(processed_logo_image, symbol_data['image'])
                            if similarity > 0.7:  # Adjust the threshold as necessary
                                characteristics.append(symbol_data['meaning'])
                                matched = True

                        if not matched:
                            characteristics.append('Unknown')

                # Append the extracted data to the list
                data.append({
                    'Design Name': design_name,
                    'Type': tile_type_text,
                    'Tile Design Image Path': tile_design_image_path,
                    'Design Preview Image Path': design_preview_image_path,
                    'Size': size,
                    'Tile Class': tile_class,
                    'Characteristics': ', '.join(characteristics),
                })

        except Exception as e:
            print(f"Error processing page {page_num+1} in {pdf_path}: {e}")

# Process each PDF document in the folder
for pdf_path in glob.glob(os.path.join(pdf_folder, "*.pdf")):
    process_pdf(pdf_path)

# Convert the list of dictionaries to a DataFrame
df_tiles = pd.DataFrame(data)

# Save the DataFrame to a CSV file for easier inspection
df_tiles.to_csv("extracted_tile_details.csv", index=False)

# Print DataFrames to terminal
print(df_tiles)