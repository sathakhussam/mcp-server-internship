"""
Website scraper for fetching and processing business website content.
"""

import logging
import uuid
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebsiteScraper:
    def __init__(self):
        """Initialize the website scraper."""
        self.logger = logging.getLogger(__name__)
        self.visited_urls = set()

    def scrape_website(self, base_url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape website content and return processed text chunks with metadata.
        
        Args:
            base_url: The main URL of the website to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of dictionaries containing text chunks and metadata
        """
        self.visited_urls.clear()
        documents = []
        
        try:
            # Start with the base URL
            urls_to_visit = [base_url]
            
            while urls_to_visit and len(self.visited_urls) < max_pages:
                url = urls_to_visit.pop(0)
                
                if url in self.visited_urls:
                    continue
                    
                self.logger.info(f"Scraping URL: {url}")
                
                # Fetch and process the page
                try:
                    page_docs = self._process_page(url)
                    documents.extend(page_docs)
                    
                    # Add new URLs to visit
                    if page_docs:  # Only look for more links if page was successfully processed
                        new_urls = self._extract_links(url, page_docs[0]['html'])
                        urls_to_visit.extend(
                            url for url in new_urls
                            if url not in self.visited_urls
                            and urlparse(url).netloc == urlparse(base_url).netloc
                        )
                    
                    self.visited_urls.add(url)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {url}: {str(e)}")
                    continue
            
            self.logger.info(f"Finished scraping {len(self.visited_urls)} pages")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error during website scraping: {str(e)}")
            raise

    def _process_page(self, url: str) -> List[Dict[str, Any]]:
        """Process a single page and return text chunks with metadata."""
        try:
            # Fetch page content
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer']):
                element.decompose()
            
            # Extract main content
            content = soup.get_text(separator=' ', strip=True)
            
            # Split into chunks (simple paragraph-based splitting)
            chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            
            # Create documents with metadata
            documents = []
            for chunk in chunks:
                if len(chunk.split()) >= 10:  # Only keep chunks with at least 10 words
                    doc = {
                        'id': str(uuid.uuid4()),
                        'text': chunk,
                        'metadata': {
                            'source': 'website',
                            'path': url
                        },
                        'html': response.text  # Include HTML for link extraction
                    }
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Error processing page {url}: {str(e)}")
            return []

    def _extract_links(self, base_url: str, html: str) -> List[str]:
        """Extract valid internal links from the page."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            
            # Only include internal links
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)
        
        return links