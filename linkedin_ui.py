#!/usr/bin/env python3
"""
LinkedIn Posts MCP - Simple Local UI

A simple tkinter-based UI for the LinkedIn Posts MCP application.
Allows users to generate AI news posts and view results in a local interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
import sys
from typing import Optional, Dict
from dotenv import load_dotenv

# Import our existing modules
from linkedin_mcp import LinkedInMCP

# Load environment variables
load_dotenv()

class LinkedInPostsUI:
    """Main UI class for LinkedIn Posts MCP application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Posts MCP - AI News Generator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set up the UI
        self.setup_ui()
        
        # Initialize the MCP backend
        self.mcp = LinkedInMCP()
        
        # Current post data
        self.current_post_data = None
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn Posts MCP", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Generate button
        self.generate_btn = ttk.Button(button_frame, text="🚀 Generate AI News Post", 
                                      command=self.generate_post, style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Clear Results", 
                                   command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="Ready to generate posts", 
                                     foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Generated Posts", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # English post section
        en_frame = ttk.Frame(results_frame)
        en_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        en_frame.columnconfigure(0, weight=1)
        en_frame.rowconfigure(1, weight=1)
        
        ttk.Label(en_frame, text="🇺🇸 English Version", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 5))
        
        self.en_text = scrolledtext.ScrolledText(en_frame, height=15, width=40, 
                                                wrap=tk.WORD, state=tk.DISABLED)
        self.en_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Copy English button
        self.copy_en_btn = ttk.Button(en_frame, text="📋 Copy English", 
                                     command=self.copy_english, state=tk.DISABLED)
        self.copy_en_btn.grid(row=2, column=0, pady=(5, 0))
        
        # Spanish post section
        es_frame = ttk.Frame(results_frame)
        es_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        es_frame.columnconfigure(0, weight=1)
        es_frame.rowconfigure(1, weight=1)
        
        ttk.Label(es_frame, text="🇪🇸 Spanish Version", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 5))
        
        self.es_text = scrolledtext.ScrolledText(es_frame, height=15, width=40, 
                                                wrap=tk.WORD, state=tk.DISABLED)
        self.es_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Copy Spanish button
        self.copy_es_btn = ttk.Button(es_frame, text="📋 Copy Spanish", 
                                     command=self.copy_spanish, state=tk.DISABLED)
        self.copy_es_btn.grid(row=2, column=0, pady=(5, 0))
        
        # Bottom frame for additional info
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Post info
        self.info_label = ttk.Label(bottom_frame, text="No post generated yet", 
                                   foreground="gray")
        self.info_label.pack(side=tk.LEFT)
        
        # Open LinkedIn button
        self.linkedin_btn = ttk.Button(bottom_frame, text="🌐 Open LinkedIn", 
                                      command=self.open_linkedin, state=tk.DISABLED)
        self.linkedin_btn.pack(side=tk.RIGHT)
        
    def generate_post(self):
        """Generate a new AI news post in a separate thread."""
        # Check if API key is configured
        if not os.getenv('OPENAI_API_KEY'):
            messagebox.showerror("Configuration Error", 
                               "OpenAI API key not found!\n\nPlease set OPENAI_API_KEY in your .env file.")
            return
        
        # Disable button and start progress
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Generating AI news post...", foreground="orange")
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._generate_post_thread)
        thread.daemon = True
        thread.start()
        
    def _generate_post_thread(self):
        """Generate post in background thread."""
        try:
            # Generate the post
            result = self.mcp.run()
            
            # Update UI in main thread
            self.root.after(0, self._on_generation_complete, result)
            
        except Exception as e:
            # Handle errors in main thread
            self.root.after(0, self._on_generation_error, str(e))
    
    def _on_generation_complete(self, result):
        """Handle successful post generation."""
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        
        if result:
            self.current_post_data = result
            self.display_post(result)
            self.status_label.config(text="Post generated successfully!", foreground="green")
        else:
            self.status_label.config(text="Failed to generate post", foreground="red")
            messagebox.showerror("Generation Error", "Failed to generate post. Please try again.")
    
    def _on_generation_error(self, error_msg):
        """Handle post generation errors."""
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Error occurred", foreground="red")
        messagebox.showerror("Error", f"An error occurred while generating the post:\n\n{error_msg}")
    
    def display_post(self, post_data: Dict):
        """Display the generated post in the text areas."""
        # Enable text areas
        self.en_text.config(state=tk.NORMAL)
        self.es_text.config(state=tk.NORMAL)
        
        # Clear existing content
        self.en_text.delete(1.0, tk.END)
        self.es_text.delete(1.0, tk.END)
        
        # Display English version
        en_content = post_data.get('post_body_en', 'No English content available')
        self.en_text.insert(1.0, en_content)
        
        # Display Spanish version
        es_content = post_data.get('post_body_es', 'No Spanish content available')
        self.es_text.insert(1.0, es_content)
        
        # Disable text areas for read-only
        self.en_text.config(state=tk.DISABLED)
        self.es_text.config(state=tk.DISABLED)
        
        # Enable copy buttons
        self.copy_en_btn.config(state=tk.NORMAL)
        self.copy_es_btn.config(state=tk.NORMAL)
        self.linkedin_btn.config(state=tk.NORMAL)
        
        # Update info
        title = post_data.get('title', 'Untitled')
        link = post_data.get('link', 'No link available')
        self.info_label.config(text=f"Title: {title} | Link: {link[:50]}..." if len(link) > 50 else f"Title: {title} | Link: {link}")
    
    def clear_results(self):
        """Clear all results and reset UI."""
        # Clear text areas
        self.en_text.config(state=tk.NORMAL)
        self.es_text.config(state=tk.NORMAL)
        self.en_text.delete(1.0, tk.END)
        self.es_text.delete(1.0, tk.END)
        self.en_text.config(state=tk.DISABLED)
        self.es_text.config(state=tk.DISABLED)
        
        # Disable buttons
        self.copy_en_btn.config(state=tk.DISABLED)
        self.copy_es_btn.config(state=tk.DISABLED)
        self.linkedin_btn.config(state=tk.DISABLED)
        
        # Reset info
        self.info_label.config(text="No post generated yet", foreground="gray")
        self.status_label.config(text="Ready to generate posts", foreground="blue")
        
        # Clear current data
        self.current_post_data = None
    
    def copy_english(self):
        """Copy English post to clipboard."""
        if self.current_post_data:
            content = self.current_post_data.get('post_body_en', '')
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_label.config(text="English post copied to clipboard!", foreground="green")
    
    def copy_spanish(self):
        """Copy Spanish post to clipboard."""
        if self.current_post_data:
            content = self.current_post_data.get('post_body_es', '')
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_label.config(text="Spanish post copied to clipboard!", foreground="green")
    
    def open_linkedin(self):
        """Open LinkedIn in the default browser."""
        import webbrowser
        try:
            webbrowser.open('https://www.linkedin.com/feed/')
            self.status_label.config(text="LinkedIn opened in browser", foreground="blue")
        except Exception as e:
            messagebox.showerror("Browser Error", f"Could not open browser: {e}")


def main():
    """Main entry point for the UI application."""
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found. Please create one with your OpenAI API key.")
        print("You can copy env.example to .env and add your API key.")
    
    # Create and run the UI
    root = tk.Tk()
    app = LinkedInPostsUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the UI
    root.mainloop()


if __name__ == "__main__":
    main()
