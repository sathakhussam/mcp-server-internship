"""
Tkinter GUI implementation for the Business Intelligence Assistant.
"""

import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import asyncio
import logging
from typing import Optional
from threading import Thread
from queue import Queue
from src.mcp.host import MCPHost

class BusinessIntelligenceApp(tk.Tk):
    def __init__(self):
        """Initialize the Tkinter application."""
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.title("Business Intelligence Assistant")
        self.geometry("800x600")
        
        # Initialize MCP host
        self.mcp_host = MCPHost()
        
        # Message queue for async operations
        self.message_queue = Queue()
        
        # Setup UI components
        self._setup_ui()
        
        # Start message processing
        self._process_message_queue()
        
        # Perform initial health check
        self._schedule_async(self._check_health())

    def _setup_ui(self):
        """Set up the user interface components."""
        # Main container with padding
        main_container = ttk.Frame(self, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Initializing...")
        status_bar = ttk.Label(
            main_container,
            textvariable=self.status_var,
            padding="5"
        )
        status_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Action buttons
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(
            button_frame,
            text="Ingest Website",
            command=self._ingest_website
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Import WhatsApp",
            command=self._import_whatsapp
        ).pack(side=tk.LEFT, padx=5)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            main_container,
            wrap=tk.WORD,
            height=20
        )
        self.chat_history.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_history.config(state=tk.DISABLED)
        
        # Query input
        self.query_var = tk.StringVar()
        query_frame = ttk.Frame(main_container)
        query_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.query_entry = ttk.Entry(
            query_frame,
            textvariable=self.query_var
        )
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(
            query_frame,
            text="Ask",
            command=self._send_query
        ).pack(side=tk.RIGHT)
        
        # Configure grid weights
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        
        # Bind return key to send query
        self.query_entry.bind('<Return>', lambda e: self._send_query())

    def _schedule_async(self, coroutine):
        """Schedule an async coroutine to run in a separate thread."""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(coroutine)
                self.message_queue.put(("async_result", result))
            except Exception as e:
                self.logger.error(f"Async operation error: {str(e)}")
                self.message_queue.put(("error", str(e)))
            finally:
                loop.close()
        
        Thread(target=run_async, daemon=True).start()

    def _process_message_queue(self):
        """Process messages from the async operations queue."""
        try:
            while True:
                # Check for messages without blocking
                try:
                    message_type, content = self.message_queue.get_nowait()
                    
                    if message_type == "status":
                        self.status_var.set(content)
                    elif message_type == "chat":
                        self._append_to_chat(content)
                    elif message_type == "error":
                        messagebox.showerror("Error", content)
                    elif message_type == "health":
                        self._update_health_status(content)
                    
                    self.message_queue.task_done()
                except Exception:
                    break
        finally:
            # Schedule next check
            self.after(100, self._process_message_queue)

    async def _check_health(self):
        """Perform a health check of the system components."""
        try:
            health = await self.mcp_host.health_check()
            
            if health["overall"]:
                self.message_queue.put(("status", "System ready"))
            else:
                failed_components = [
                    comp for comp, status in health.items()
                    if comp != "overall" and not status
                ]
                self.message_queue.put((
                    "status",
                    f"System issues detected: {', '.join(failed_components)}"
                ))
        except Exception as e:
            self.message_queue.put(("error", f"Health check failed: {str(e)}"))

    def _send_query(self):
        """Send a query to the MCP host."""
        query = self.query_var.get().strip()
        if not query:
            return
        
        # Clear input
        self.query_var.set("")
        
        # Show user query in chat
        self._append_to_chat(f"You: {query}")
        
        # Process query
        self._schedule_async(self._process_query(query))

    async def _process_query(self, query: str):
        """Process a user query and display the response."""
        try:
            response = await self.mcp_host.get_business_info(query)
            
            # Format and display response
            message = f"Assistant: {response['answer']}\n\n"
            message += f"Confidence: {response['confidence']}\n"
            if response['sources']:
                message += "Sources:\n" + "\n".join(f"- {src}" for src in response['sources'])
            
            self.message_queue.put(("chat", message))
            
        except Exception as e:
            self.message_queue.put(("error", f"Error processing query: {str(e)}"))

    def _ingest_website(self):
        """Prompt for and ingest website content."""
        url = tk.simpledialog.askstring(
            "Ingest Website",
            "Enter the website URL:"
        )
        
        if url:
            self.message_queue.put(("status", f"Ingesting website: {url}"))
            self._schedule_async(self._process_ingestion("website", url))

    def _import_whatsapp(self):
        """Prompt for and import WhatsApp chat file."""
        file_path = filedialog.askopenfilename(
            title="Select WhatsApp Chat Export",
            filetypes=[("Text files", "*.txt")]
        )
        
        if file_path:
            self.message_queue.put(("status", "Importing WhatsApp chat..."))
            self._schedule_async(self._process_ingestion("whatsapp", file_path))

    async def _process_ingestion(self, source_type: str, source_path: str):
        """Process data ingestion from a source."""
        try:
            result = await self.mcp_host.ingest_data(source_type, source_path)
            
            if result["status"] == "success":
                self.message_queue.put((
                    "status",
                    f"Successfully processed {result['documents_processed']} documents. "
                    f"Total documents: {result['total_documents']}"
                ))
            else:
                self.message_queue.put(("error", result["message"]))
                
        except Exception as e:
            self.message_queue.put(("error", f"Ingestion error: {str(e)}"))

    def _append_to_chat(self, message: str):
        """Append a message to the chat history."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{message}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)