from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for making the vector embeddings
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Init the embedding service.

        Args: 
            model_name: get from HuggingFace
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384

    def _load_model(self):
        """ Lazy Load model """
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")

    def create_embedding(self, text:str) -> List[float]:
        """ 
        Make an embedding for a single piece of text

        Args:
            text: Text to convert

        Returns:
            the values for that text
        """
        if not text or text.strip() == "":
            logger.warning("Empty text list provided for batch embedding")
            return [0.0] * self.dimension
        
        self._load_model()

        # Createing Embedding and convert to list
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings
        Args:
            texts: List of texts to convert to embeddings
            
        Returns:
            List of embeddings
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding")
            return []
        
        logger.info(f"Creating embeddings for {len(texts)} texts")


        embeddings = []
        for text in texts:
            embedding = self.create_embedding(text)  # Handles all validation!
            embeddings.append(embedding)
        
        logger.info(f"Successfully created {len(embeddings)} embeddings")
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1 (1 = identical, 0 = unrelated, -1 = opposite)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

# Create global instance
embedding_service = EmbeddingService()
        
        
        

        
