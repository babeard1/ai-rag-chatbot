from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings
from services.pdf_service import extract_text_from_pdf, chunk_text_with_page_tracking
from services.embedding_service import embedding_service
from services.vector_service import vector_service
from services.llm_service import llm_service
import logging
from typing import Dict, Any
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Knowledge Base API",
    description="Backend API for RAG based chatbot",
    version="1.0.0"
)

# Adds CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "RAG Knowledge base API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "debug_mode": settings.debug,
        "timestamp": "2024-01-01T00:00:00Z"  # You can add real timestamp later
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.
    Extracts text, creates embeddings, and stores in vector database.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text with page tracking
        pdf_data = extract_text_from_pdf(temp_file_path)
        
        if not pdf_data['full_text'].strip():
            raise HTTPException(
                status_code=400, 
                detail="No text could be extracted from this PDF. It may be image-based or empty."
            )
        
        # Chunk text while preserving page numbers
        chunks = chunk_text_with_page_tracking(pdf_data['pages'])
        
        # Create embeddings for each chunk
        vectors_to_upsert = []
        
        for chunk in chunks:
            # Create embedding
            embedding = embedding_service.create_embedding(chunk['text'])
            
            # Prepare metadata
            metadata = {
                'text': chunk['text'],
                'source': file.filename,
                'page': chunk['page_number'],  # Now properly tracked!
                'chunk_id': chunk['chunk_id']
            }
            
            # Create vector ID
            vector_id = f"{file.filename}_chunk_{chunk['chunk_id']}"
            
            vectors_to_upsert.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Store in Pinecone
        vector_service.upsert_vectors(vectors_to_upsert)
        
        # Clean up temp file
        import os
        os.remove(temp_file_path)
        
        return {
            "message": "Document uploaded and processed successfully",
            "filename": file.filename,
            "total_pages": pdf_data['total_pages'],
            "chunks_created": len(chunks),
            "pages_with_text": len(pdf_data['pages'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/query")
async def query_documents(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query the knowledge base and get an AI-generated answer.
    
    Args:
        request: JSON body with "question" field
        
    Returns:
        AI-generated answer with source citations
    """
    # Extract question from request
    question = request.get("question", "").strip()
    
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question is required"
        )
    
    logger.info(f"Processing query: {question}")
    
    try:
        # STEP 1: Convert question to embedding
        logger.info("Step 1: Creating embedding for question...")
        question_embedding = embedding_service.create_embedding(question)
        
        # STEP 2: Search Pinecone for similar chunks
        logger.info("Step 2: Searching for relevant documents...")
        search_result = vector_service.search_similar(
            query_embedding=question_embedding,
            top_k=5  # Get top 5 most relevant chunks
        )
        
        if not search_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {search_result.get('error', 'Unknown error')}"
            )
        
        # Check if we found any relevant chunks
        if not search_result["results"]:
            return {
                "success": True,
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": [],
                "question": question
            }
        
        logger.info(f"Found {len(search_result['results'])} relevant chunks")
        
        # STEP 3: Prepare context chunks for LLM
        context_chunks = []
        for result in search_result["results"]:
            context_chunks.append({
                "text": result["text"],
                "metadata": result["metadata"]
            })
        
        # STEP 4: Generate answer using LLM
        logger.info("Step 3: Generating answer with LLM...")
        llm_result = llm_service.generate_answer(
            question=question,
            context_chunks=context_chunks
        )
        
        if not llm_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate answer: {llm_result.get('error', 'Unknown error')}"
            )
        
        logger.info("Successfully generated answer")
        
        # Return the complete response
        return {
            "success": True,
            "question": question,
            "answer": llm_result["answer"],
            "sources": llm_result["sources"],
            "model": llm_result["model"],
            "tokens_used": llm_result["usage"]["total_tokens"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/documents")
async def list_documents():
    """
    List all documents currently stored in the vector database.
    Returns unique document names with their metadata.
    """
    try:
        from services.vector_service import vector_service
        
        # Query Pinecone to get all unique document sources

        # Get stats from Pinecone index
        stats = vector_service.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors == 0:
            return {
                "documents": [],
                "total_documents": 0,
                "total_chunks": 0
            }
        
        # Fetch all vectors to get unique sources
        # Note: Pagination for production
        all_vectors = vector_service.index.query(
            vector=[0] * 384,  # Dummy vector
            top_k=min(total_vectors, 10000),  # Limit to prevent timeout
            include_metadata=True
        )
        
        # Extract unique documents
        documents_map = {}
        
        for match in all_vectors.get('matches', []):
            metadata = match.get('metadata', {})
            source = metadata.get('filename') or metadata.get('source', 'Unknown')
            
            if source not in documents_map:
                documents_map[source] = {
                    'filename': source,
                    'chunks': 0,
                    'pages': set()
                }
            
            documents_map[source]['chunks'] += 1
            
            # Track unique pages
            page = metadata.get('page')
            if page is not None:
                documents_map[source]['pages'].add(page)
        
        # Convert to list format
        documents = []
        for source, data in documents_map.items():
            documents.append({
                'filename': data['filename'],
                'total_chunks': data['chunks'],
                'total_pages': len(data['pages']) if data['pages'] else None
            })
        
        # Sort by filename
        documents.sort(key=lambda x: x['filename'])
        
        return {
            "documents": documents,
            "total_documents": len(documents),
            "total_chunks": total_vectors
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to prevent crashes."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )