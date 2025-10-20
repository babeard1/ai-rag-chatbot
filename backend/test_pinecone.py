import sys
import os
from dotenv import load_dotenv
# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.embedding_service import embedding_service
from services.vector_service import vector_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_service():
    """Test the embedding service."""
    print("\n🧪 Testing Embedding Service...")
    
    # Test single embedding
    test_text = "This is a test document about vacation policies."
    embedding = embedding_service.create_embedding(test_text)
    
    print(f"✅ Created embedding for: '{test_text}'")
    print(f"✅ Embedding dimension: {len(embedding)}")
    print(f"✅ First 5 values: {embedding[:5]}")
    
    # Test batch embeddings
    test_texts = [
        "Employee vacation policy allows 15 days per year.",
        "Health insurance covers medical and dental.",
        "Remote work is available on Fridays."
    ]
    
    embeddings = embedding_service.create_embeddings_batch(test_texts)
    print(f"✅ Created {len(embeddings)} embeddings in batch")
    
    return embeddings, test_texts

def test_vector_service():
    """Test the vector service (Pinecone connection)."""
    print("\n🧪 Testing Vector Service (Pinecone)...")
    
    # Test connection and get stats
    stats = vector_service.get_index_stats()
    if stats["success"]:
        print(f"✅ Connected to Pinecone successfully")
        print(f"✅ Current vectors in index: {stats['total_vectors']}")
    else:
        print(f"❌ Pinecone connection failed: {stats['error']}")
        return False
    
    return True

def test_full_pipeline():
    """Test the complete pipeline: text → embeddings → Pinecone storage → search."""
    print("\n🧪 Testing Full Pipeline...")
    
    # Step 1: Create test data
    test_texts = [
        "Employees get 15 vacation days annually and can carry over 5 days.",
        "Health insurance includes medical, dental, and vision coverage.",
        "Remote work policy allows working from home on Fridays.",
        "The company offers 401k matching up to 6% of salary.",
        "Sick leave policy provides 10 days per year for illness."
    ]
    
    # Step 2: Create embeddings
    print("📝 Creating embeddings...")
    embeddings = embedding_service.create_embeddings_batch(test_texts)
    
    # Step 3: Prepare metadata
    metadata_list = []
    for i, text in enumerate(test_texts):
        metadata = {
            "filename": "test_handbook.pdf",
            "page": i + 1,
            "chunk_type": "test",
            "source": "test_pipeline"
        }
        metadata_list.append(metadata)
    
    # Step 4: Store in Pinecone
    print("💾 Storing vectors in Pinecone...")
    store_result = vector_service.store_vectors(test_texts, embeddings, metadata_list)
    
    if not store_result["success"]:
        print(f"❌ Failed to store vectors: {store_result['error']}")
        return False
    
    print(f"✅ Stored {store_result['upserted_count']} vectors")
    
    # Step 5: Test search
    print("🔍 Testing semantic search...")
    query_text = "How many vacation days do I get?"
    query_embedding = embedding_service.create_embedding(query_text)
    
    search_result = vector_service.search_similar(query_embedding, top_k=3)
    
    if not search_result["success"]:
        print(f"❌ Search failed: {search_result['error']}")
        return False
    
    print(f"✅ Found {search_result['total_found']} similar results")
    print(f"\n📋 Search Results for: '{query_text}'")
    
    for i, result in enumerate(search_result["results"], 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Text: {result['text'][:100]}...")
        print(f"   Source: {result['metadata']['filename']} (page {result['metadata']['page']})")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting AI Services Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Embedding Service
        embeddings, texts = test_embedding_service()
        
        # Test 2: Vector Service (Pinecone)
        if not test_vector_service():
            print("❌ Vector service test failed - check your .env file")
            exit(1)
        
        # Test 3: Full Pipeline
        if not test_full_pipeline():
            print("❌ Full pipeline test failed")
            exit(1)
        
        print("\n🎉 All tests passed! Your AI services are working correctly.")
        print("✅ Ready to proceed to updating the main API endpoints.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print("💡 Check your .env file and make sure your Pinecone API key is correct.")
        exit(1)