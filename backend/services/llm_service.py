from groq import Groq
from typing import List, Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMService: 
    """
    Service for interacting with Groq LLM API
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the LLM service.
        
        Args:
            model: The Groq model to use (default is Llama 3.1 70B)
        """
        self.model = model
        
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize Groq client with workaround for Codespaces proxy issue
        import httpx
        self.client = Groq(
            api_key=api_key,
            http_client=httpx.Client()  # This bypasses the proxy issue
        )
        logger.info(f"Initialized Groq LLM service with model: {self.model}")

    def generate_answer(self,
                        question: str,
                        context_chunks: List[Dict[str, Any]],
                        max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate an answer to a question using provided context chunks

        Args:
            question: The user's question
            context_chunks: List of relevant text chunks from vector search
            max_tokens: Maximum length of response
            
        Returns:
            Dictionary with answer and metadata
        """

        try:
            # Build the context from chunks
            context_text = self._format_context(context_chunks)

            #Build the prompt
            prompt = self._build_rag_prompt(question, context_text)

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context. Always cite which document and page your answer comes from."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower = more focused, higher = more creative
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )

            # Get the answer
            answer = response.choices[0].message.content

            # Get token usage for monitoring
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            logger.info(f"Generated answer successfully. Tokens used: {usage['total_tokens']}")
            
            return {
                "success": True,
                "answer": answer,
                "model": self.model,
                "usage": usage,
                "sources": self._extract_sources(context_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "answer": ""
            }

    def _format_context(self, chunks: List[ Dict[str, Any]] ) -> str:
        """
        Format context chunks into a readable string for the prompt.
        
        Args:
            chunks: List of document chunks with text and metadata
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            filename = metadata.get("filename", "Unknown")
            page = metadata.get("page", "Unknown")

           # Format each chunk with source info
            context_parts.append(
                f"[Source {i}: {filename}, Page {page}]\n{text}\n"
            )

        return "\n".join(context_parts)

    def _build_rag_prompt(self, question: str, context: str) -> str:
        """
        Build the RAG prompt that combines question and context.

        Args:
            question: User's question
            context: Formatted context chunks
            
        Returns:
            Complete prompt string
        """
        prompt = f"""You are answering questions based on document content. Use the context below to answer the question.
                CONTEXT:
                {context}

                QUESTION: {question}

                INSTRUCTIONS:
                - Answer the question using ONLY the information from the context above
                - Cite which source (filename and page) you got the information from
                - If the context doesn't contain the answer, say "I don't have enough information to answer this question."
                - Be concise but complete
                - Format your answer clearly

                ANSWER:"""
        
        return prompt
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source citations from context chunks.
        
        Args:
            chunks: List of context chunks
            
        Returns:
            List of source citations
        """
        sources = []
        seen = set()  # Avoid duplicate sources
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            filename = metadata.get("filename", "Unknown")
            page = metadata.get("page", "Unknown")
            
            # Create unique key to avoid duplicates
            source_key = f"{filename}:{page}"
            
            if source_key not in seen:
                sources.append({
                    "filename": filename,
                    "page": page,
                    "text_preview": chunk.get("text", "")[:150] + "..."
                })
                seen.add(source_key)
        
        return sources

    def simple_chat(self, message: str, max_tokens: int = 200) -> str:
        """
        Simple chat function for testing (no RAG, just pure LLM).
        
        Args:
            message: Message to send to LLM
            max_tokens: Maximum response length
            
        Returns:
            LLM response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": message}],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in simple chat: {str(e)}")
            return f"Error: {str(e)}"


# Create global instance
llm_service = LLMService()