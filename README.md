# Tiles-Project-for-AR-XTLabs
Automated PDF processing tool that extracts tile design details and symbols from PDF documents using Python, OpenCV, and Tesseract OCR. It dynamically identifies and extracts images, text, and characteristics, then stores the data in CSV files for easy reference.

This project is a Python-based tool that extracts tile design details, symbols, and their corresponding meanings from PDF documents. It utilizes OpenCV, Tesseract OCR, and PyMuPDF to dynamically detect and extract images, symbols, and text from PDFs and store the extracted information in CSV files for easy reference.

Features
Automatically extracts tile design details such as design name, tile type, tile design images, preview images, and characteristics.
Extracts symbols from the 3rd page of each PDF, along with their meanings.
Compares the symbols on subsequent pages with the extracted ones and appends the corresponding meanings to the CSV.
Stores all extracted data into a structured CSV file format for easy accessibility.
Folder Structure
PDF Folder: Contains all the PDF documents from which the tile details and symbols are extracted.
![Screenshot (18)](https://github.com/user-attachments/assets/aa199964-051d-4920-a19d-6cc6f558e5fb)

Extracted Images Folder: Stores the extracted images of tile designs, previews, and symbols for each PDF.
![Screenshot (19)](https://github.com/user-attachments/assets/edbffd44-7747-4c8c-8db8-b31c40c56459)
![Screenshot (20)](https://github.com/user-attachments/assets/3b4ba4e0-f47e-43f1-9e53-5a366ee506ee)


CSV Files
extracted_tile_details.csv: Contains the extracted tile details for each design, including design name, tile type, tile size, tile class, design image paths, and characteristics.


Design Name: The name of the tile design.
Type: The type of tile (e.g., wall, floor).
Tile Design Image Path: The path to the extracted image of the tile design.
Design Preview Image Path: The path to the extracted image of the tile preview.
Size: The size of the tile.
Tile Class: The class of the tile.
Characteristics: Characteristics of the tile, derived from comparing the symbols with the extracted ones.
extracted_symbols.csv: Contains the extracted symbols from the 3rd page of each PDF along with their meanings.
![Screenshot (21)](https://github.com/user-attachments/assets/a32bb08a-3a10-48fc-adbe-45e37001819d)


Symbol: The path to the extracted symbol image.
Meaning: The corresponding meaning of the symbol.
![Screenshot (22)](https://github.com/user-attachments/assets/8ebfb39d-65cb-4094-b9a1-ae9432d97079)


How It Works
Preprocessing: The tool preprocesses the PDF by converting pages into images, applying edge detection, and dynamically extracting relevant regions such as tile design details and symbols.
OCR (Optical Character Recognition): Text data like tile name, type, size, and characteristics are extracted using Tesseract OCR from specific regions of the page.
Image Comparison: The extracted symbols from the 3rd page of each PDF are used to compare with the symbols on subsequent pages, and their corresponding meanings are appended to the tile characteristics.
CSV Output: All extracted data are saved in CSV files for easy reference and analysis.

Prerequisites
To run this project, you'll need the following Python libraries installed:

bash
Copy code
pip install pytesseract opencv-python pymupdf numpy pillow pandas scikit-image
Additionally, make sure you have Tesseract OCR installed on your machine and configure the path to tesseract.exe in the code.

Usage
Place all PDF documents in the designated PDF Folder.
Run the script to extract the tile design details and symbols.
The results will be saved in the Extracted Images Folder and CSV Files as described above.

Future Improvements
Improve accuracy of symbol comparison using advanced image processing techniques.
Add support for multi-language text extraction with OCR.
