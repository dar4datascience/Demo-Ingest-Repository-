from pypdf import PdfReader

# Define the input PDF file path and output text file path
pdf_path = "Knowledge Base/Diplomado Procuracion de Fondos para ONGs/CLASE 1: ASPECTOS ADMINISTRATIVOS PARA GANAR CONVOCATORIAS/document.pdf"
txt_path = "output.txt"

# Create a PDF reader object
reader = PdfReader(pdf_path)

# Extract text from all pages
all_text = "".join(page.extract_text() or "" for page in reader.pages)

# Save the extracted text to a file
with open(txt_path, "w", encoding="utf-8") as txt_file:
    txt_file.write(all_text)

print(f"Extracted text saved to {txt_path}")
