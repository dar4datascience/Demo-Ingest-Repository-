import os
from pypdf import PdfReader

# Define the source folder where PDFs are located
source_folder = "Knowledge Base/Diplomado Procuracion de Fondos para ONGs"

# Walk through all the subdirectories and files in the source folder
for root, dirs, files in os.walk(source_folder):
    for file in files:
        if file.endswith(".pdf"):  # Process only PDF files
            pdf_path = os.path.join(root, file)
            
            # Generate the text file path in the same folder as the PDF
            txt_path = os.path.join(root, file.replace(".pdf", ".txt"))
            
            # Create a PDF reader object
            reader = PdfReader(pdf_path)

            # Extract text from all pages
            all_text = "".join(page.extract_text() or "" for page in reader.pages)

            # Save the extracted text to a .txt file
            with open(txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(all_text)

            print(f"Extracted text from {pdf_path} saved to {txt_path}")
