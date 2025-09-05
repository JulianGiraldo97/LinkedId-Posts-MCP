#!/usr/bin/env python3
"""
LinkedIn Posts MCP - Web UI (Alternative Port)

A Flask-based web interface for the LinkedIn Posts MCP application.
Runs on port 5001 to avoid conflicts with other services.
"""

import os
import json
import threading
import time
from typing import Optional, Dict
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# Import our existing modules
from linkedin_mcp import LinkedInMCP

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Global variables for storing state
current_post_data = None
generation_status = "ready"  # ready, generating, success, error
generation_message = "Ready to generate posts"
generation_progress = 0

class WebLinkedInMCP:
    """Web wrapper for LinkedIn MCP functionality."""
    
    def __init__(self):
        self.mcp = LinkedInMCP()
    
    def generate_post_async(self):
        """Generate post in background thread."""
        global current_post_data, generation_status, generation_message, generation_progress
        
        try:
            generation_status = "generating"
            generation_message = "Fetching latest AI news..."
            generation_progress = 25
            
            # Step 1: Fetch news
            articles = self.mcp.news_fetcher.fetch_latest_news()
            if not articles:
                generation_status = "error"
                generation_message = "No articles found. Please try again."
                generation_progress = 0
                return
            
            generation_message = "Generating LinkedIn post..."
            generation_progress = 75
            
            # Step 2: Generate post
            post_data = self.mcp.post_generator.generate_post(articles)
            if not post_data:
                generation_status = "error"
                generation_message = "Failed to generate post. Please try again."
                generation_progress = 0
                return
            
            # Success
            current_post_data = post_data
            generation_status = "success"
            generation_message = "Post generated successfully!"
            generation_progress = 100
            
        except Exception as e:
            generation_status = "error"
            generation_message = f"Error: {str(e)}"
            generation_progress = 0

# Initialize the web MCP
web_mcp = WebLinkedInMCP()

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_post():
    """API endpoint to generate a new post."""
    global generation_status, generation_message, generation_progress
    
    # Check if already generating
    if generation_status == "generating":
        return jsonify({
            'status': 'error',
            'message': 'Generation already in progress'
        }), 400
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        return jsonify({
            'status': 'error',
            'message': 'OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.'
        }), 400
    
    # Reset status
    generation_status = "generating"
    generation_message = "Starting generation..."
    generation_progress = 0
    
    # Start generation in background thread
    thread = threading.Thread(target=web_mcp.generate_post_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': 'Generation started'
    })

@app.route('/api/status')
def get_status():
    """API endpoint to get current generation status."""
    return jsonify({
        'status': generation_status,
        'message': generation_message,
        'progress': generation_progress
    })

@app.route('/api/post')
def get_post():
    """API endpoint to get current post data."""
    if current_post_data:
        return jsonify({
            'status': 'success',
            'data': current_post_data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No post data available'
        })

@app.route('/api/clear', methods=['POST'])
def clear_post():
    """API endpoint to clear current post data."""
    global current_post_data, generation_status, generation_message, generation_progress
    
    current_post_data = None
    generation_status = "ready"
    generation_message = "Ready to generate posts"
    generation_progress = 0
    
    return jsonify({
        'status': 'success',
        'message': 'Post data cleared'
    })

@app.route('/api/copy/<language>', methods=['POST'])
def copy_post(language):
    """API endpoint to copy post to clipboard (simulated)."""
    if not current_post_data:
        return jsonify({
            'status': 'error',
            'message': 'No post data available'
        })
    
    if language == 'en':
        content = current_post_data.get('post_body_en', '')
    elif language == 'es':
        content = current_post_data.get('post_body_es', '')
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid language specified'
        })
    
    # In a real implementation, you'd copy to clipboard
    # For now, we'll just return the content
    return jsonify({
        'status': 'success',
        'message': f'{language.upper()} post copied to clipboard',
        'content': content
    })

def create_templates():
    """Create HTML templates if they don't exist."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LinkedIn Posts MCP{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .post-container {
            min-height: 300px;
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            padding: 1rem;
            background-color: #f8f9fa;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-ready { background-color: #6c757d; }
        .status-generating { background-color: #ffc107; animation: pulse 1s infinite; }
        .status-success { background-color: #198754; }
        .status-error { background-color: #dc3545; }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .copy-btn {
            position: relative;
        }
        .copy-btn.copied::after {
            content: "Copied!";
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            background: #000;
            color: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_template)
    
    # Create main page template
    index_template = '''{% extends "base.html" %}

{% block title %}LinkedIn Posts MCP - AI News Generator{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h2">
                <i class="fas fa-linkedin text-primary"></i>
                LinkedIn Posts MCP
            </h1>
            <div class="d-flex gap-2">
                <button id="generateBtn" class="btn btn-primary btn-lg">
                    <i class="fas fa-rocket"></i> Generate AI News Post
                </button>
                <button id="clearBtn" class="btn btn-outline-secondary">
                    <i class="fas fa-trash"></i> Clear
                </button>
            </div>
        </div>
        
        <!-- Status Section -->
        <div class="card mb-4">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <span id="statusIndicator" class="status-indicator status-ready"></span>
                    <span id="statusMessage" class="me-3">Ready to generate posts</span>
                    <div id="progressContainer" class="flex-grow-1" style="display: none;">
                        <div class="progress" style="height: 8px;">
                            <div id="progressBar" class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Results Section -->
        <div class="row" id="resultsSection" style="display: none;">
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-flag-usa"></i> English Version
                        </h5>
                        <button id="copyEnBtn" class="btn btn-sm btn-outline-primary copy-btn">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="enPost" class="post-container"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-flag"></i> Spanish Version
                        </h5>
                        <button id="copyEsBtn" class="btn btn-sm btn-outline-primary copy-btn">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="esPost" class="post-container"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Post Info Section -->
        <div class="card mt-4" id="postInfoSection" style="display: none;">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6 class="card-title">Post Information</h6>
                        <p id="postTitle" class="card-text"></p>
                        <p id="postLink" class="card-text">
                            <small class="text-muted">Source: <a href="#" target="_blank" id="postLinkUrl"></a></small>
                        </p>
                    </div>
                    <div class="col-md-4 text-end">
                        <a id="linkedinBtn" href="https://www.linkedin.com/feed/" target="_blank" class="btn btn-primary">
                            <i class="fab fa-linkedin"></i> Open LinkedIn
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let statusCheckInterval;

// DOM elements
const generateBtn = document.getElementById('generateBtn');
const clearBtn = document.getElementById('clearBtn');
const statusIndicator = document.getElementById('statusIndicator');
const statusMessage = document.getElementById('statusMessage');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const resultsSection = document.getElementById('resultsSection');
const postInfoSection = document.getElementById('postInfoSection');
const enPost = document.getElementById('enPost');
const esPost = document.getElementById('esPost');
const copyEnBtn = document.getElementById('copyEnBtn');
const copyEsBtn = document.getElementById('copyEsBtn');
const postTitle = document.getElementById('postTitle');
const postLinkUrl = document.getElementById('postLinkUrl');
const linkedinBtn = document.getElementById('linkedinBtn');

// Generate post
generateBtn.addEventListener('click', async () => {
    try {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'started') {
            startStatusCheck();
        } else {
            showError(data.message);
            resetGenerateButton();
        }
    } catch (error) {
        showError('Network error: ' + error.message);
        resetGenerateButton();
    }
});

// Clear results
clearBtn.addEventListener('click', async () => {
    try {
        await fetch('/api/clear', { method: 'POST' });
        clearResults();
    } catch (error) {
        showError('Error clearing results: ' + error.message);
    }
});

// Copy functions
copyEnBtn.addEventListener('click', () => copyPost('en'));
copyEsBtn.addEventListener('click', () => copyPost('es'));

// Start status checking
function startStatusCheck() {
    statusCheckInterval = setInterval(checkStatus, 1000);
}

// Check generation status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        updateStatus(data.status, data.message, data.progress);
        
        if (data.status === 'success') {
            clearInterval(statusCheckInterval);
            loadPostData();
            resetGenerateButton();
        } else if (data.status === 'error') {
            clearInterval(statusCheckInterval);
            showError(data.message);
            resetGenerateButton();
        }
    } catch (error) {
        clearInterval(statusCheckInterval);
        showError('Status check error: ' + error.message);
        resetGenerateButton();
    }
}

// Update status display
function updateStatus(status, message, progress) {
    statusIndicator.className = `status-indicator status-${status}`;
    statusMessage.textContent = message;
    
    if (status === 'generating') {
        progressContainer.style.display = 'block';
        progressBar.style.width = `${progress}%`;
    } else {
        progressContainer.style.display = 'none';
    }
}

// Load post data
async function loadPostData() {
    try {
        const response = await fetch('/api/post');
        const data = await response.json();
        
        if (data.status === 'success') {
            displayPost(data.data);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Error loading post: ' + error.message);
    }
}

// Display post
function displayPost(postData) {
    enPost.textContent = postData.post_body_en || 'No English content available';
    esPost.textContent = postData.post_body_es || 'No Spanish content available';
    postTitle.textContent = postData.title || 'Untitled';
    postLinkUrl.href = postData.link || '#';
    postLinkUrl.textContent = postData.link || 'No link available';
    
    resultsSection.style.display = 'block';
    postInfoSection.style.display = 'block';
}

// Clear results
function clearResults() {
    enPost.textContent = '';
    esPost.textContent = '';
    postTitle.textContent = '';
    postLinkUrl.href = '#';
    postLinkUrl.textContent = '';
    
    resultsSection.style.display = 'none';
    postInfoSection.style.display = 'none';
    
    updateStatus('ready', 'Ready to generate posts', 0);
}

// Copy post to clipboard
async function copyPost(language) {
    try {
        const response = await fetch(`/api/copy/${language}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            // Copy to clipboard
            await navigator.clipboard.writeText(data.content);
            
            // Show copied feedback
            const btn = language === 'en' ? copyEnBtn : copyEsBtn;
            btn.classList.add('copied');
            setTimeout(() => btn.classList.remove('copied'), 2000);
            
            showSuccess(data.message);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Copy error: ' + error.message);
    }
}

// Reset generate button
function resetGenerateButton() {
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-rocket"></i> Generate AI News Post';
}

// Show error message
function showError(message) {
    statusIndicator.className = 'status-indicator status-error';
    statusMessage.textContent = message;
    statusMessage.className = 'me-3 text-danger';
}

// Show success message
function showSuccess(message) {
    statusIndicator.className = 'status-indicator status-success';
    statusMessage.textContent = message;
    statusMessage.className = 'me-3 text-success';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateStatus('ready', 'Ready to generate posts', 0);
});
</script>
{% endblock %}'''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_template)

def main():
    """Main entry point for the web UI."""
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found. Please create one with your OpenAI API key.")
        print("You can copy env.example to .env and add your API key.")
    
    # Create templates if they don't exist
    create_templates()
    
    print("=" * 50)
    print("LinkedIn Posts MCP - Web UI (Port 5001)")
    print("=" * 50)
    print("Starting web server...")
    print("The UI will be available at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the Flask app on port 5001
        app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Trying alternative configuration...")
        # Fallback to localhost only
        app.run(host='127.0.0.1', port=5001, debug=True, threaded=True)

if __name__ == "__main__":
    main()
