import PyPDF2

def run_document_ingestion(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    """
    text = ""

    try:
        reader = PyPDF2.PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "

        return text.strip() if text else "No readable text found."

    except Exception as e:
        return f"Error extracting text: {str(e)}"
