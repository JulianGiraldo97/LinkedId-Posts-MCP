#!/bin/bash

# LinkedIn Posts MCP - Complete Project Runner
# This script runs the entire workflow: generate AI news post and post to LinkedIn

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
        exit 1
    fi
    
    # LinkedIn API credentials no longer required for manual posting
    
    print_success "Environment variables configured"
}

# LinkedIn API functionality removed - using manual posting instead

# Function to run the main project
run_project() {
    print_status "Starting LinkedIn Posts MCP project..."
    print_status "This will generate AI news and prepare for manual LinkedIn posting"
    
    # Generate the post
    python linkedin_mcp.py
    
    if [ $? -eq 0 ]; then
        print_success "Post generated successfully!"
        print_status "Opening manual posting interface..."
        python linkedin_manual_poster.py
    else
        print_error "Post generation failed"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "LinkedIn Posts MCP - Project Runner"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  run, -r, --run     Run the complete project (default)"
    echo "  gen, -g, --gen     Generate post only"
    echo "  manual, -m, --manual Post manually (copy/paste to LinkedIn)"
    echo "  setup, -s, --setup Setup project (install dependencies, check config)"
    echo "  help, -h, --help   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Run complete project"
    echo "  $0 run             # Run complete project"
    echo "  $0 gen             # Generate post only"
    echo "  $0 manual          # Post manually (copy/paste to LinkedIn)"
    echo "  $0 setup           # Setup project"
}

# Function to generate post only
run_generate() {
    print_status "Generating AI news post..."
    python linkedin_mcp.py
}

# Function to run manual posting
run_manual_post() {
    if [ ! -f "linkedin_post.json" ]; then
        print_error "linkedin_post.json not found!"
        print_status "Please run 'python linkedin_mcp.py' first to generate a post"
        exit 1
    fi
    
    print_status "Opening manual LinkedIn posting interface..."
    python linkedin_manual_poster.py
}

# Function to setup project
run_setup() {
    print_status "Setting up LinkedIn Posts MCP project..."
    check_venv
    setup_venv
    check_env
    check_required_vars
    print_success "Project setup completed!"
    print_status "You can now run: $0 auth (to authenticate with LinkedIn)"
}

# Main script logic
main() {
    echo "=========================================="
    echo "LinkedIn Posts MCP - Project Runner"
    echo "=========================================="
    echo ""
    
    # Check if virtual environment exists and activate it
    check_venv
    setup_venv
    
    # Parse command line arguments
    case "${1:-run}" in
        "run"|"-r"|"--run")
            check_env
            check_required_vars
            run_project
            ;;
        "gen"|"-g"|"--gen")
            check_env
            check_required_vars
            run_generate
            ;;
        "manual"|"-m"|"--manual")
            check_env
            check_required_vars
            run_manual_post
            ;;
        "setup"|"-s"|"--setup")
            run_setup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
