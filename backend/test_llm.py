import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service

def test_simple_chat():
    """Test basic LLM functionality."""
    print("\n🧪 Testing Simple Chat (No RAG)...")
    
    question = "What is 6+2? Answer in one sentence."
    print(f"Question: {question}")
    
    answer = llm_service.simple_chat(question)
    print(f"Answer: {answer}")
    print("✅ Simple chat works!\n")

def test_rag_answer():
    """Test RAG-style answer generation."""
    print("🧪 Testing RAG Answer Generation...")
    
    # Simulate context chunks from Pinecone search
    mock_chunks = [
        {
            "text": "Employees receive 15 vacation days per year. Unused days can be carried over up to 5 days maximum.",
            "metadata": {
                "filename": "employee_handbook.pdf",
                "page": 12
            }
        },
        {
            "text": "Vacation requests must be submitted at least 2 weeks in advance through the HR portal.",
            "metadata": {
                "filename": "employee_handbook.pdf",
                "page": 13
            }
        }
    ]
    
    question = "How many vacation days do employees get?"
    
    print(f"Question: {question}")
    print("Context: 2 document chunks about vacation policy")
    
    result = llm_service.generate_answer(question, mock_chunks)
    
    if result["success"]:
        print(f"\n✅ Answer: {result['answer']}")
        print(f"\n📚 Sources:")
        for source in result["sources"]:
            print(f"  - {source['filename']}, Page {source['page']}")
        print(f"\n📊 Tokens used: {result['usage']['total_tokens']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    print("🚀 Testing Groq LLM Service")
    print("=" * 50)
    
    try:
        test_simple_chat()
        test_rag_answer()
        print("\n🎉 All LLM tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("\n💡 Make sure you added GROQ_API_KEY to your .env file")