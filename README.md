# RAG Knowledge Base Chatbot Demo

A full-stack AI application for search and question-answering user uploaded PDFs.

## Tech Stack

### Backend

-   **Framework**: FastAPI
-   **Language**: Python 3.10+
-   **PDF Processing**: pypdf
-   **AI/ML**: LangChain, HuggingFace Embeddings
-   **Vector Database**: Pinecone
-   **LLM Provider**: Groq (Llama 3.1 70B)
-   **Deployment**: Railway

### Frontend

-   **Framework**: React 18 + Vite
-   **UI Library**: Material UI (MUI v5)
-   **HTTP Client**: Axios
-   **File Upload**: react-dropzone
-   **Deployment**: Vercel

### Infrastructure

-   **Version Control**: Git/GitHub
-   **Development**: GitHub Codespaces
-   **Domain**: Cloudflare DNS

## Architecture
User uploads PDF → Backend extracts text → Text chunked intelligently → 
Chunks converted to embeddings → Stored in Pinecone with metadata → 
User asks question → Question converted to embedding → Semantic search finds relevant chunks → 
LLM generates answer with source citations
```

## Workflow

### Document Upload
1. User uploads PDF through drag-and-drop interface
2. Backend extracts text using pypdf
3. LangChain splits text into semantic chunks
4. HuggingFace model creates embeddings (vectors)
5. Vectors stored in Pinecone with metadata (filename, page number)

### Query Process
1. User submits question in chat interface
2. Question converted to embedding
3. Pinecone performs semantic search for similar vectors
4. Top matching chunks retrieved with metadata
5. Context + question sent to Groq LLM
6. Answer returned with source citations
```

## Project Structure

ai-rag-chatbot/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   ├── config/
│   │   └── settings.py          # Environment configuration
│   └── services/
│       ├── pdf_service.py       # PDF text extraction
│       ├── embedding_service.py # Vector creation
│       ├── vector_service.py    # Pinecone operations
│       └── llm_service.py       # Groq LLM integration
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main application
│   │   ├── components/          # React components
│   │   └── services/
│   │       └── api.js           # API client
│   └── package.json
└── README.md

## API Endpoints

-   `GET /health` - Health check
-   `POST /upload` - Upload and process PDF
-   `POST /query` - Ask questions about uploaded documents
