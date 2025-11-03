"""
ChromaDB vector store implementation for storing and retrieving business data.
"""

import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

class ChromaStore:
    def __init__(self, db_path: str):
        """Initialize ChromaDB client with persistent storage."""
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        # Ensure database directory exists
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=db_path,
            anonymized_telemetry=False
        ))
        
        # Create or get the collection for business data
        self.collection = self.client.get_or_create_collection(
            name="business_data",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info(f"ChromaDB initialized at {db_path}")

    def add_documents(self, texts: List[str], metadata_list: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the vector store."""
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadata_list,
                ids=ids
            )
            self.logger.info(f"Added {len(texts)} documents to ChromaDB")
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the vector store for relevant documents."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results
            documents = []
            for idx, doc in enumerate(results['documents'][0]):
                documents.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][idx],
                    'distance': results['distances'][0][idx]
                })
            
            return documents
        except Exception as e:
            self.logger.error(f"Error querying documents: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            raise