import pdfplumber
import os
import tempfile
from PIL import Image

def extract_pdf_content(file_path: str) -> dict:
    """
    Extracts text and optionally a thumbnail from a PDF file.
    Returns a dict with 'text' and 'thumbnail_path'.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    result = {"text": "", "thumbnail_path": None}
    full_text = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            
            # 1. Strategy: Extract first page as thumbnail for Vision fallback
            if total_pages > 0:
                first_page = pdf.pages[0]
                # Render as image
                img = first_page.to_image(resolution=150).original
                
                # Save to a temporary file
                temp_dir = tempfile.gettempdir()
                thumb_path = os.path.join(temp_dir, f"thumb_{os.path.basename(file_path)}.png")
                img.save(thumb_path)
                result["thumbnail_path"] = thumb_path

            # 2. Sampling strategy for text
            pages_to_read = set()
            for i in range(min(3, total_pages)): pages_to_read.add(i)
            mid = total_pages // 2
            for i in range(max(0, mid - 1), min(total_pages, mid + 2)): pages_to_read.add(i)
            for i in range(max(0, total_pages - 3), total_pages): pages_to_read.add(i)
            
            for page_idx in sorted(list(pages_to_read)):
                page = pdf.pages[page_idx]
                text = page.extract_text()
                if text:
                    full_text.append(f"--- Page {page_idx + 1} ---\n{text}")
        
        result["text"] = "\n\n".join(full_text)
        return result
        
    except Exception as e:
        return {"text": f"Error parsing PDF: {str(e)}", "thumbnail_path": None}

if __name__ == "__main__":
    # Basic CLI test for the parser
    import sys
    if len(sys.argv) > 1:
        print(extract_pdf_content(sys.argv[1]))
    else:
        print("Usage: python pdf_parser.py <path_to_pdf>")
