from pinecone import Pinecone, PineconeException
from config.settings import settings
from typing import List, Dict, Any, Optional
import logging
import uuid
import time

logger = logging.getLogger(__name__)

class VectorService:
    """
    Service for managing vector storage and retrieval using Pinecone.
    
    This service handles:
    - Storing text chunks as vectors with metadata
    - Searching for similar vectors (semantic search)
    - Managing the Pinecone index
    """

    def __init__(self):
        """Initialize Pinecone connection."""
        self.pc = None
        self.index = None
        self._connect()

    def _connect(self):
        """Connect to Pinecone and get the index."""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=settings.pinecone_api_key)

            # Get Index
            self.index = self.pc.Index(settings.pinecone_index_name)

            # Test connection
            stats = self.index.describe_index_stats()
            logger.info(f"Connected to Pinecone index '{settings.pinecone_index_name}'")
            logger.info(f"Index stats: {stats.get('total_vector_count', 0)} vectors stored")

        except PineconeException as e:
            logger.error(f"Failed to connect to Pinecone: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Pinecone: {str(e)}")
            raise

    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone.
        This method expects vectors in the format used by main.py.
        
        Args:
            vectors: List of dicts with 'id', 'values', and 'metadata'
            
        Returns:
            Dictionary with success status and upserted count
        """
        try:
            if not vectors:
                return {"success": False, "error": "No vectors provided"}
            
            logger.info(f"Upserting {len(vectors)} vectors to Pinecone")
            
            # Pinecone expects this format
            formatted_vectors = []
            for v in vectors:
                formatted_vectors.append({
                    "id": v['id'],
                    "values": v['values'],
                    "metadata": v['metadata']
                })
            
            # Upsert to Pinecone
            response = self.index.upsert(vectors=formatted_vectors)
            
            logger.info(f"Successfully upserted {response.upserted_count} vectors")
            
            return {
                "success": True,
                "upserted_count": response.upserted_count
            }
            
        except PineconeException as e:
            logger.error(f"Pinecone error upserting vectors: {str(e)}")
            return {"success": False, "error": f"Pinecone error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error upserting vectors: {str(e)}")
            return {"success": False, "error": f"Upsert error: {str(e)}"}

    def store_vector(self, 
                     texts: List[str],
                     embeddings: List[List[float]],
                     metadata_list: List[Dict[str, Any]]
                     ) -> Dict[str, Any]:
        """
        Store text chunks and their embeddings in Pinecone.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors (one per text chunk)
            metadata_list: List of metadata dicts (filename, page, etc.)
            
        Returns:
            Dictionary with results (success status, vector IDs, etc.)
        """

        if len(texts) != len(embeddings) != len(metadata_list):
            raise ValueError("texts, embeddings, and metadata_list gotta have the same length")
        
        if not texts:
            return {"success": False, "error": "No texts provided"}
        
        try:
            # Prepare vectors for Pinecone
            vectors_to_upsert = []
            vector_ids = []

            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadata_list)):
                # Make unique ID for vector
                vector_id = str(uuid.uuid4())
                vector_ids.append(vector_id)

                # Add text to metadata for retrieval
                full_metadata = {
                    **metadata,
                    "text": text,
                    "chunk_index": i,
                    "created_at": time.time()
                }

                # Prep vector for pinecone
                vector_data = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": full_metadata
                }
                vectors_to_upsert.append(vector_data)

            logger.info(f"Storing {len(vectors_to_upsert)} vectors in Pinecone")
            upsert_response = self.index.upsert(vectors=vectors_to_upsert)

            logger.info(f"Successfully stored {upsert_response.upserted_count} vectors")

            return {
                "success": True,
                "upserted_count": upsert_response.upserted_count,
                "vector_ids": vector_ids,
                "message": f"Stored {len(vectors_to_upsert)} text chunks as vectors"
            }
        
        except PineconeException as e:
            logger.error(f"Pinecone error storing vectors: {str(e)}")
            return {"success": False, "error": f"Pinecone error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error storing vectors: {str(e)}")
            return {"success": False, "error": f"Storage error: {str(e)}"}

    def search_similar(self,
                       query_embedding: List[float],
                       top_k: int = 5,
                       filter_dict: Optional[Dict[str, Any]] = None
                       ) -> Dict[str, Any]:
        """
        Search for vectors similar to the query embedding.
        
        Args:
            query_embedding: The embedding vector to search for
            top_k: Number of similar results to return
            filter_dict: Optional metadata filters (e.g., {"filename": "handbook.pdf"})
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            logger.info(f"Searching for {top_k} similar vectors")

            # Do similarity search
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )

            # Process results
            results = []
            for match in search_response.matches:
                result = {
                    "id": match.id,
                    "score": float(match.score),
                    "text": match.metadata.get("text", ""),
                    "metadata": {
                        key: value for key, value in match.metadata.items()
                        if key not in ["text"] # Don't duplicate text in metadata
                    }
                }
                results.append(result)

            logger.info(f"Found {len(results)} similar vectors")

            return {
                "success": True,
                "results": results,
                "total_found": len(results)
            }
        
        except PineconeException as e:
            logger.error(f"Pinecone error during search: {str(e)}")
            return {"success": False, "error": f"Search error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            return {"success": False, "error": f"Search error: {str(e)}"}
        
    def get_index_stats(self) -> Dict[str, Any]:
        """Get stats about the Pinecone index."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "success": True,
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0),
                "namespaces": stats.get("namespaces", {})
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"success": False, "error": str(e)}
        
    def delete_vectors(self, vector_ids: List[str]) -> Dict[str, Any]:
        """Delete specific vectors by their IDs."""
        try:
            delete_response = self.index.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} vectors")
            return {
                "success": True,
                "deleted_count": len(vector_ids),
                "message": f"Deleted {len(vector_ids)} vectors"
            }
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            return {"success": False, "error": str(e)}
        
# Create global instance
vector_service = VectorService()