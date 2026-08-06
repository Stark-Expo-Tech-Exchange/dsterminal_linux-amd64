# quick_protect.py
import os
from pypdf import PdfReader, PdfWriter
import io

def protect_pdf_simple(input_file):
    """Simple protection using PyMuPDF if available"""
    try:
        import fitz
        from PIL import Image
        
        doc = fitz.open(input_file)
        writer = PdfWriter()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(200/72, 200/72)
            pix = page.get_pixmap(matrix=mat)
            
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            img_pdf = PdfReader(img_byte_arr)
            writer.add_page(img_pdf.pages[0])
        
        doc.close()
        
        output_file = input_file.replace('.pdf', '_protected.pdf')
        with open(output_file, "wb") as f:
            writer.write(f)
        
        return output_file
    except ImportError:
        print("âŒ Install: pip install PyMuPDF pillow")
        return None
    except Exception as e:
        print(f"âŒ Error: {e}")
        return None

if __name__ == "__main__":
    file = input("Enter PDF path: ").strip().strip('"')
    result = protect_pdf_simple(file)
    if result:
        print(f"âœ… Protected: {result}")
    else:
        print("âŒ Failed")