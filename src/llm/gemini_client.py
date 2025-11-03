"""
Gemini LLM client implementation for generating responses.
"""

import os
import logging
from typing import Dict, List
import google.generativeai as genai

class GeminiClient:
    def __init__(self):
        """Initialize Gemini client with API key."""
        self.logger = logging.getLogger(__name__)
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.logger.info("Gemini client initialized")

    def generate_response(self, query: str, context: List[Dict[str, str]]) -> Dict[str, any]:
        """Generate a response using the Gemini model with business context."""
        try:
            # Format context for the prompt
            context_str = "\n".join([
                f"Source ({doc['metadata']['source']}): {doc['text']}"
                for doc in context
            ])
            
            # Construct the prompt
            prompt = f"""You are a helpful assistant that answers only using verified data from the provided business dataset.

Question: {query}

Context:
{context_str}

Respond with factual, concise information in conversational form. Include only information that is directly supported by the context."""

            # Generate response
            response = self.model.generate_content(prompt)
            
            # Calculate confidence based on context relevance
            confidence = sum(1 / (1 + doc.get('distance', 0)) for doc in context) / len(context)
            
            # Format sources
            sources = [
                f"{doc['metadata']['source']}: {doc['metadata'].get('path', 'N/A')}"
                for doc in context
            ]
            
            return {
                "answer": response.text if hasattr(response, 'text') else str(response),
                "sources": sources,
                "confidence": round(confidence, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise

    def health_check(self) -> bool:
        """Check if the Gemini service is accessible."""
        try:
            # Try a simple generation to verify API access
            response = self.model.generate_content("Hello")
            return bool(response and response.text)
        except Exception as e:
            self.logger.error(f"Gemini health check failed: {str(e)}")
            return False