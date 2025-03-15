#!/usr/bin/env python3

from pypdf import PdfReader

def extract_text_from_pdf(pdf_path, start_page=0, end_page=None):
    """Extract text from PDF file."""
    reader = PdfReader(pdf_path)
    
    if end_page is None or end_page > len(reader.pages):
        end_page = len(reader.pages)
    
    text = ""
    for page_num in range(start_page, end_page):
        try:
            page = reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        except Exception as e:
            print(f"Error extracting text from page {page_num}: {e}")
    
    return text

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_path> [start_page] [end_page]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end_page = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    text = extract_text_from_pdf(pdf_path, start_page, end_page)
    print(text)