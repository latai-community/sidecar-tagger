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
            
            # 1. Strategy: Extract a representative thumbnail for Vision fallback
            # We scan a few pages to find one that isn't blank (avoiding guard pages)
            thumb_path = None
            temp_dir = tempfile.gettempdir()
            
            pages_to_check = [0, 1, 2, 4, 9] # Pages 1, 2, 3, 5, 10
            for p_idx in pages_to_check:
                if p_idx < total_pages:
                    page = pdf.pages[p_idx]
                    # Render at low res to check for content
                    img = page.to_image(resolution=72).original
                    # Check if it's not all white (255, 255)
                    if img.convert("L").getextrema() != (255, 255):
                        # Save higher res version of the non-blank page
                        img_final = page.to_image(resolution=150).original
                        thumb_path = os.path.join(temp_dir, f"thumb_{p_idx}_{os.path.basename(file_path)}.png")
                        img_final.save(thumb_path)
                        result["thumbnail_path"] = thumb_path
                        break
            
            # Fallback: if all scanned pages are blank but doc has pages, take the first one anyway
            if not thumb_path and total_pages > 0:
                first_page = pdf.pages[0].to_image(resolution=150).original
                thumb_path = os.path.join(temp_dir, f"thumb_0_fallback_{os.path.basename(file_path)}.png")
                first_page.save(thumb_path)
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
