import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.pdf_service import pdf_service

def test_chunking():
    """Test the text chunking functionality."""
    print("🧪 Testing Text Chunking")
    print("=" * 50)
    
    # Sample text (simulating extracted PDF text)
    sample_text = """
    Employee Handbook - Vacation Policy
    
    All full-time employees are entitled to 15 days of paid vacation annually. 
    Part-time employees receive vacation days prorated based on hours worked. 
    Vacation days accrue monthly and can be used after 90 days of employment.
    
    Unused vacation days may be carried over to the next calendar year, up to 
    a maximum of 5 days. Days exceeding this limit will be forfeited. Employees 
    are encouraged to use their vacation time to maintain work-life balance.
    
    Vacation requests must be submitted through the HR portal at least 2 weeks 
    in advance. Requests are subject to manager approval based on business needs. 
    Peak season requests may require additional notice.
    """
    
    # Test basic chunking
    print("\n1. Testing basic text chunking...")
    chunks = pdf_service.chunk_text(sample_text, chunk_size=200, overlap=20)
    
    print(f"✅ Created {len(chunks)} chunks from {len(sample_text)} characters")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} ({len(chunk)} chars):")
        print(f"'{chunk[:100]}...'")
    
    # Test page chunking (with metadata)
    print("\n\n2. Testing page-based chunking (with metadata)...")
    
    # Simulate pages from PDF extraction
    mock_pages = [
        {"page_number": 1, "text": sample_text[:300]},
        {"page_number": 2, "text": sample_text[300:]}
    ]
    
    chunks_with_metadata = pdf_service.chunk_pages(mock_pages, chunk_size=200, overlap=20)
    
    print(f"✅ Created {len(chunks_with_metadata)} chunks from {len(mock_pages)} pages")
    
    for chunk in chunks_with_metadata:
        print(f"\nPage {chunk['page']}, Chunk {chunk['chunk_index']}:")
        print(f"  Text: '{chunk['text'][:80]}...'")
        print(f"  Length: {chunk['char_count']} chars")
    
    print("\n🎉 Chunking tests passed!")

if __name__ == "__main__":
    test_chunking()