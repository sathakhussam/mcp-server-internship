"""
WhatsApp chat importer for processing exported chat files.
"""

import re
import uuid
import logging
from typing import List, Dict, Any
from datetime import datetime

class WhatsAppImporter:
    def __init__(self):
        """Initialize the WhatsApp chat importer."""
        self.logger = logging.getLogger(__name__)
        
        # Regular expression for parsing WhatsApp messages
        self.message_pattern = re.compile(
            r'^\[?(\d{1,2}/\d{1,2}/\d{2,4},?\s*\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\]?\s*-\s*([^:]+):\s*(.+)$'
        )

    def import_chat(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Import and process a WhatsApp chat export file.
        
        Args:
            file_path: Path to the WhatsApp chat export file (.txt)
            
        Returns:
            List of dictionaries containing processed messages with metadata
        """
        try:
            self.logger.info(f"Importing WhatsApp chat from {file_path}")
            documents = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                current_message = []
                current_metadata = None
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try to match a new message
                    match = self.message_pattern.match(line)
                    
                    if match:
                        # If we have a previous message, save it
                        if current_message and current_metadata:
                            doc = self._create_document(
                                '\n'.join(current_message),
                                current_metadata
                            )
                            if doc:
                                documents.append(doc)
                        
                        # Start a new message
                        timestamp, sender, message = match.groups()
                        try:
                            parsed_timestamp = self._parse_timestamp(timestamp)
                            current_metadata = {
                                'timestamp': parsed_timestamp.isoformat(),
                                'sender': sender.strip(),
                                'path': file_path
                            }
                            current_message = [message.strip()]
                        except ValueError as e:
                            self.logger.warning(f"Error parsing timestamp {timestamp}: {str(e)}")
                            current_metadata = None
                            current_message = []
                    
                    elif current_message and current_metadata:
                        # Continue previous message
                        current_message.append(line)
                
                # Don't forget the last message
                if current_message and current_metadata:
                    doc = self._create_document(
                        '\n'.join(current_message),
                        current_metadata
                    )
                    if doc:
                        documents.append(doc)
            
            self.logger.info(f"Imported {len(documents)} messages from WhatsApp chat")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error importing WhatsApp chat: {str(e)}")
            raise

    def _create_document(self, text: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        """Create a document from message text and metadata."""
        # Skip short or meaningless messages
        if len(text.split()) < 3:
            return None
            
        return {
            'id': str(uuid.uuid4()),
            'text': text,
            'metadata': {
                'source': 'whatsapp',
                'timestamp': metadata['timestamp'],
                'sender': metadata['sender'],
                'path': metadata['path']
            }
        }

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse various WhatsApp timestamp formats."""
        # Try different common WhatsApp date formats
        formats = [
            '%d/%m/%y, %H:%M',
            '%d/%m/%Y, %H:%M',
            '%m/%d/%y, %H:%M',
            '%m/%d/%Y, %H:%M',
            '%d/%m/%y, %I:%M %p',
            '%d/%m/%Y, %I:%M %p',
            '%m/%d/%y, %I:%M %p',
            '%m/%d/%Y, %I:%M %p'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp.strip('[]'), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse timestamp: {timestamp}")