import fitz  # PyMuPDF
import os

pdf_path = 'input\L&T page 8.pdf'
pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

# Open the PDF
doc = fitz.open(pdf_path)

# Convert each page to JPG
for page_number in range(len(doc)):
    page = doc.load_page(page_number)  # 0-based indexing
    pix = page.get_pixmap(dpi=300)
    output_file = f"input/{pdf_name}_page_{page_number + 1}.jpg"
    pix.save(output_file)

print("Conversion complete!")
