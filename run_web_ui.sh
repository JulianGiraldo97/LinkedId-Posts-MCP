#!/bin/bash

# LinkedIn Posts MCP - Main Launcher
# This script launches the web-based UI for the LinkedIn Posts MCP application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found!"
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Function to activate virtual environment and install dependencies
setup_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    print_status "Installing/updating dependencies..."
    pip install -q -r requirements.txt
    
    print_success "Dependencies installed"
}

# Function to check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your API keys before running again"
        exit 1
    fi
}

# Function to check required environment variables
check_required_vars() {
    print_status "Checking environment variables..."
    
    if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
        print_error "OPENAI_API_KEY not configured in .env file"
        print_status "Please edit .env file and add your OpenAI API key"
        exit 1
    fi
    
    print_success "Environment variables configured"
}

# Function to launch the web UI
launch_web_ui() {
    print_status "Launching LinkedIn Posts MCP Web UI..."
    print_status "The web interface will open in your browser at: http://localhost:5000"
    print_status "Press Ctrl+C to stop the server"
    
    # Launch the web UI
    python linkedin_web_ui.py
    
    if [ $? -eq 0 ]; then
        print_success "Web UI closed successfully"
    else
        print_error "Web UI encountered an error"
        exit 1
    fi
}

# Function to open browser
open_browser() {
    if command -v open >/dev/null 2>&1; then
        # macOS
        open http://localhost:5000
    elif command -v xdg-open >/dev/null 2>&1; then
        # Linux
        xdg-open http://localhost:5000
    elif command -v start >/dev/null 2>&1; then
        # Windows
        start http://localhost:5000
    else
        print_warning "Could not automatically open browser. Please go to: http://localhost:5000"
    fi
}

# Main script logic
main() {
    echo "=========================================="
    echo "LinkedIn Posts MCP - Main Launcher"
    echo "=========================================="
    echo ""
    
    # Check if virtual environment exists and activate it
    check_venv
    setup_venv
    
    # Check environment configuration
    check_env
    check_required_vars
    
    # Open browser in background (will work after server starts)
    (sleep 3 && open_browser) &
    
    # Launch the web UI
    launch_web_ui
}

# Run main function
main "$@"
