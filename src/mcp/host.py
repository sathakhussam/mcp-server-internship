"""
MCP host implementation for managing business intelligence queries.
"""

import os
import logging
from typing import Dict, Any, Optional
from src.vector.chroma_store import ChromaStore
from src.llm.gemini_client import GeminiClient
from src.data.website_scraper import WebsiteScraper
from src.data.whatsapp_importer import WhatsAppImporter

class MCPHost:
    def __init__(self):
        """Initialize MCP host with required components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.vector_store = ChromaStore(os.getenv('CHROMA_DB_PATH'))
        self.llm_client = GeminiClient()
        self.website_scraper = WebsiteScraper()
        self.whatsapp_importer = WhatsAppImporter()

    async def get_business_info(self, query: str) -> Dict[str, Any]:
        """
        Process a business query and return a response with sources.
        
        Args:
            query: The user's question about the business
            
        Returns:
            Dictionary containing answer, sources, and confidence score
        """
        try:
            # Retrieve relevant context from vector store
            context = self.vector_store.query(query)
            
            if not context:
                return {
                    "answer": "I don't have enough information to answer that question. Try ingesting some business data first.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Generate response using LLM
            response = self.llm_client.generate_response(query, context)
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise

    async def ingest_data(self, source_type: str, source_path: str) -> Dict[str, Any]:
        """
        Ingest data from a website or WhatsApp chat.
        
        Args:
            source_type: Type of data source ('website' or 'whatsapp')
            source_path: URL for website or file path for WhatsApp chat
            
        Returns:
            Dictionary containing ingestion status and statistics
        """
        try:
            documents = []
            
            if source_type == 'website':
                documents = self.website_scraper.scrape_website(source_path)
            elif source_type == 'whatsapp':
                documents = self.whatsapp_importer.import_chat(source_path)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            if documents:
                # Prepare data for vector store
                texts = [doc['text'] for doc in documents]
                metadata_list = [doc['metadata'] for doc in documents]
                ids = [doc['id'] for doc in documents]
                
                # Store in vector database
                self.vector_store.add_documents(texts, metadata_list, ids)
                
                return {
                    "status": "success",
                    "documents_processed": len(documents),
                    "total_documents": self.vector_store.get_collection_stats()["total_documents"]
                }
            
            return {
                "status": "error",
                "message": f"No documents were extracted from {source_type} source"
            }
            
        except Exception as e:
            self.logger.error(f"Error ingesting data: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, bool]:
        """Check the health of all components."""
        try:
            vector_store_health = bool(self.vector_store.get_collection_stats())
            llm_health = self.llm_client.health_check()
            
            return {
                "vector_store": vector_store_health,
                "llm": llm_health,
                "overall": vector_store_health and llm_health
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "vector_store": False,
                "llm": False,
                "overall": False
            }