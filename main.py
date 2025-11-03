#!/usr/bin/env python3
"""
Business Intelligence Assistant
A desktop application for answering business queries using MCP and Gemini.
"""

import os
import logging
from dotenv import load_dotenv
from src.gui.app import BusinessIntelligenceApp
from src.utils.logger import setup_logger

def main():
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Validate required environment variables
    required_vars = ['GEMINI_API_KEY', 'CHROMA_DB_PATH', 'DATA_DIR']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set all required environment variables in .env file")
        return
    
    try:
        # Initialize and start the GUI application
        app = BusinessIntelligenceApp()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()