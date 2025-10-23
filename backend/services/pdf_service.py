import pypdf
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> Dict[str, any]:
    """
    Extract text from PDF file with page tracking.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing:
        - full_text: Complete text from all pages
        - pages: List of dicts with page number and text
        - total_pages: Total number of pages
    """
    try:
        reader = pypdf.PdfReader(file_path)
        total_pages = len(reader.pages)
        
        pages = []
        full_text_parts = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            
            if page_text.strip():  # Only include pages with actual text
                pages.append({
                    'page_number': page_num,
                    'text': page_text
                })
                full_text_parts.append(page_text)
        
        full_text = "\n\n".join(full_text_parts)
        
        logger.info(f"Extracted text from {total_pages} pages, {len(pages)} pages contain text")
        
        return {
            'full_text': full_text,
            'pages': pages,
            'total_pages': total_pages
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def chunk_text_with_page_tracking(pages: List[Dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """
    Split text into chunks while preserving page number information.
    
    Args:
        pages: List of dictionaries with 'page_number' and 'text'
        chunk_size: Target size for each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of dictionaries with 'text', 'page_number', and 'chunk_id'
    """
    chunks = []
    chunk_id = 0
    
    for page_info in pages:
        page_num = page_info['page_number']
        page_text = page_info['text']
        
        # If page is smaller than chunk_size, keep it as one chunk
        if len(page_text) <= chunk_size:
            chunks.append({
                'text': page_text,
                'page_number': page_num,
                'chunk_id': chunk_id
            })
            chunk_id += 1
        else:
            # Split long pages into multiple chunks
            start = 0
            while start < len(page_text):
                end = start + chunk_size
                chunk_text = page_text[start:end]
                
                chunks.append({
                    'text': chunk_text,
                    'page_number': page_num,
                    'chunk_id': chunk_id
                })
                
                chunk_id += 1
                start = end - chunk_overlap  # Overlap for context
    
    logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks