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
            # Extract metadata (author, creator, dates, etc.)
            metadata = pdf.metadata
            
            # Extract text from each page
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)
        
        # Combine extracted text
        return "\n".join(full_text)
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
