from pypdf import PdfReader
from typing import Dict, List
import logging
import io

logger = logging.getLogger(__name__)

class PDFService:
    """Service for processing PDF files and extracting text."""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[str, any]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """

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


    @staticmethod
    def chunk_text(text: str, 
                   chunk_size: int = 500, 
                   overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split into chunks
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) == 0:
            return []
        
        # If text is smaller than chunk size, return as single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = start + chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word
            if end < len(text):
                # Look for sentence ending (. ! ?) in the last 100 chars
                last_portion = text[end-100:end]
                sentence_end = max(
                    last_portion.rfind('. '),
                    last_portion.rfind('! '),
                    last_portion.rfind('? ')
                )
                
                if sentence_end != -1:
                    # Break at sentence
                    end = end - 100 + sentence_end + 1
                else:
                    # No sentence found, try to break at word boundary
                    last_portion = text[end-50:end]
                    word_break = last_portion.rfind(' ')
                    if word_break != -1:
                        end = end - 50 + word_break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position (with overlap)
            start = end - overlap
            
            # Prevent infinite loop
            if start <= end - chunk_size:
                start = end
        
        logger.info(f"Split text ({len(text)} chars) into {len(chunks)} chunks")
        return chunks

    @staticmethod
    def chunk_pages(pages: List[Dict[str, any]], 
                    chunk_size: int = 500, 
                    overlap: int = 50) -> List[Dict[str, any]]:
        """
        Chunk text from multiple pages while preserving page metadata.
        
        Args:
            pages: List of page dictionaries from extract_text_from_pdf
            chunk_size: Target size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunks with metadata (text, page_number, chunk_index)
        """
        all_chunks = []
        chunk_index = 0
        
        for page in pages:
            page_num = page["page_number"]
            page_text = page["text"]
            
            if not page_text:
                continue
            
            # Chunk this page's text
            page_chunks = PDFService.chunk_text(page_text, chunk_size, overlap)
            
            # Add metadata to each chunk
            for chunk_text in page_chunks:
                all_chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "char_count": len(chunk_text)
                })
                chunk_index += 1
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
        return all_chunks

# Create global instance
pdf_service = PDFService()