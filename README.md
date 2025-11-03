# Business Intelligence Assistant

A Python-based desktop application implementing Model Context Protocol (MCP) to allow Gemini to answer questions about a business using ingested website data and WhatsApp messages.

## Features

- 🌐 Website content scraping and ingestion
- 💬 WhatsApp chat message import
- 🧠 Semantic search using ChromaDB vector store
- 🤖 Context-aware responses using Gemini Pro
- 🖥️ User-friendly Tkinter GUI interface

## Requirements

- Python 3.10 or higher
- Gemini API key
- ChromaDB for vector storage
- Required Python packages (see Installation)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd business-intelligence-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

3. Install required packages:
```bash
pip install google-generativeai chromadb beautifulsoup4 requests tiktoken python-dotenv uuid pandas
```

4. Create a `.env` file with your configuration:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
CHROMA_DB_PATH=./data/chromadb
DATA_DIR=./data
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Use the GUI to:
   - Ingest website content using the "Ingest Website" button
   - Import WhatsApp chat exports using the "Import WhatsApp" button
   - Ask questions about your business in the query input field

## Data Sources

### Website Ingestion
- Enters a URL to scrape
- Automatically extracts and processes relevant content
- Stores text chunks with source metadata

### WhatsApp Import
- Select a WhatsApp chat export file (.txt)
- Processes messages and sender information
- Maintains message context and timestamps

## Development

The project structure follows a modular design:

```
business-intelligence-assistant/
├── main.py              # Application entry point
├── .env                 # Environment configuration
├── src/
│   ├── mcp/            # MCP protocol implementation
│   │   └── host.py
│   ├── llm/            # LLM integration
│   │   └── gemini_client.py
│   ├── vector/         # Vector store
│   │   └── chroma_store.py
│   ├── data/           # Data ingestion
│   │   ├── website_scraper.py
│   │   └── whatsapp_importer.py
│   ├── gui/            # User interface
│   │   └── app.py
│   └── utils/          # Utilities
│       └── logger.py
└── logs/               # Application logs
```

## Logging

The application maintains detailed logs in the `logs` directory:
- `app.log`: Main application log file
- Rotating logs with 1MB size limit
- Includes timestamps, log levels, and component information

## Error Handling

The application implements comprehensive error handling:
- Component health checks
- Graceful failure recovery
- User-friendly error messages
- Detailed logging for troubleshooting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Insert your chosen license here]

## Support

[Insert support contact information]