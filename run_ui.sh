#!/bin/bash

# LinkedIn Posts MCP - UI Launcher
# This script launches the simple local UI for the LinkedIn Posts MCP application

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

# Function to launch the UI
launch_ui() {
    print_status "Launching LinkedIn Posts MCP UI..."
    print_status "This will open a local GUI application"
    
    # Launch the UI
    python linkedin_ui.py
    
    if [ $? -eq 0 ]; then
        print_success "UI closed successfully"
    else
        print_error "UI encountered an error"
        exit 1
    fi
}

# Main script logic
main() {
    echo "=========================================="
    echo "LinkedIn Posts MCP - UI Launcher"
    echo "=========================================="
    echo ""
    
    # Check if virtual environment exists and activate it
    check_venv
    setup_venv
    
    # Check environment configuration
    check_env
    check_required_vars
    
    # Launch the UI
    launch_ui
}

# Run main function
main "$@"
