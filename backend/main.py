from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings
from services.pdf_service import pdf_service
from services.embedding_service import embedding_service
from services.vector_service import vector_service
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
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected PDF, got {file.content_type}"
        )
    
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB in bytes
        raise HTTPException(
            status_code=400,
            detail="File too big. Max size is 10MB."
        )
    
    logger.info(f"Processing PDF: {file.filename} ({len(file_bytes)} bytes)")

    try:
        # STEP 1: Extract text from PDF
        logger.info("Step 1: Extracting text from PDF...")
        extraction_result = pdf_service.extract_text_from_pdf(file_bytes)

        if not extraction_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from PDF: {extraction_result.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Extracted {extraction_result['total_chars']} characters from {extraction_result['num_pages']} pages")

        # STEP 2: Chunk the text
        logger.info("Step 2: Chunking text...")
        chunks = pdf_service.chunk_pages(
            extraction_result["pages"],
            chunk_size=500,  # ~500 characters per chunk
            overlap=50       # 50 character overlap
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from PDF"
            )
        
        logger.info(f"Created {len(chunks)} text chunks")

        # STEP3: Create embeddings for each chunk
        logger.info("Step 3: Creating embeddings...")
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.create_embeddings_batch(chunk_texts)
        
        logger.info(f"Created {len(embeddings)} embeddings")

        # STEP 4: Prepare metadata for Pinecone DB
        logger.info("Step 4: Preparing metadata...")
        metadata_list = []
        for chunk in chunks:
            metadata = {
                "filename": file.filename,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "total_pages": extraction_result["num_pages"]
            }
            metadata_list.append(metadata)

        # STEP 5: Store in Pinecone
        logger.info("Step 5: Storing vectors in Pinecone...")
        store_result = vector_service.store_vector(
            texts=chunk_texts,
            embeddings=embeddings,
            metadata_list=metadata_list
        )
        
        if not store_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store vectors: {store_result.get('error', 'Unknown error')}"
            )
        
        logger.info(f"Successfully stored {store_result['upserted_count']} vectors")
        
        # Return success response
        return {
            "success": True,
            "filename": file.filename,
            "message": "PDF processed and indexed successfully",
            "stats": {
                "pages": extraction_result["num_pages"],
                "total_chars": extraction_result["total_chars"],
                "chunks_created": len(chunks),
                "vectors_stored": store_result["upserted_count"]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

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