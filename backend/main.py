from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings
from services.pdf_service import pdf_service
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

    # Extract text 
    result = pdf_service.extract_text_from_pdf(file_bytes)

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {result.get('error', 'Unknown error')}"
        ) 
    
    return {
        "filename": file.filename,
        "message": "PDF processed",
        **result
    }

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