from pypdf import PdfReader
from typing import Dict, List
import logging
import io

logger = logging.getLogger(__name__)

class PDFService:
    """Service for processing PDF files and extracting text."""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[str, any]:
        try:
            pdf_file = io.BytesIO(pdf_bytes)

            # Create PDF reader from bytes
            reader = PdfReader(pdf_file)

            # Get file metadata
            num_pages = len(reader.pages)
            metadata = reader.metadata or {}

            # Extracted text
            extracted_pages = []
            full_text = ""

            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()

                # Remove excessive whitespace
                page_text = " ".join(page_text.split())

                extracted_pages.append({
                    "page_number": page_num,
                    "text": page_text,
                    "char_count": len(page_text)
                })

                full_text += f" {page_text}"

            # Clean full text
            full_text = " ".join(full_text.split())

            return {
                "success": True,
                "num_pages": num_pages,
                "total_chars": len(full_text),
                "title": metadata.get("/Title", "Unknown"),
                "author": metadata.get("/Author", "Unknown"),
                "full_text": full_text,
                "pages": extracted_pages
            }
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "full_text": "",
                "pages": []
            }

pdf_service = PDFService()