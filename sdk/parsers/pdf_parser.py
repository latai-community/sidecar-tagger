import pdfplumber
import os

def extract_pdf_content(file_path: str) -> str:
    """
    Extracts text and basic metadata from a PDF file using pdfplumber.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    full_text = []
    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            
            # Sampling strategy: First 3, Middle 3, Last 3
            # Ensures we capture context from the whole document without loading it all.
            pages_to_read = set()
            
            # Start
            for i in range(min(3, total_pages)):
                pages_to_read.add(i)
            
            # Middle
            mid = total_pages // 2
            for i in range(max(0, mid - 1), min(total_pages, mid + 2)):
                pages_to_read.add(i)
                
            # End
            for i in range(max(0, total_pages - 3), total_pages):
                pages_to_read.add(i)
            
            # Extract text from the unique set of sampled pages
            for page_idx in sorted(list(pages_to_read)):
                page = pdf.pages[page_idx]
                text = page.extract_text()
                if text:
                    full_text.append(f"--- Page {page_idx + 1} ---\n{text}")
        
        return "\n\n".join(full_text)
    except Exception as e:
        # Log or handle parsing errors specifically
        return f"Error parsing PDF: {str(e)}"

if __name__ == "__main__":
    # Basic CLI test for the parser
    import sys
    if len(sys.argv) > 1:
        print(extract_pdf_content(sys.argv[1]))
    else:
        print("Usage: python pdf_parser.py <path_to_pdf>")
