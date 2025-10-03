#!/bin/bash

# Nx System Calculator - Development Runner Script
# This script helps you quickly start the development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.11+ is required but not found"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js 20+ is required but not found"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is required but not found"
        exit 1
    fi
    
    echo ""
}

# Setup backend
setup_backend() {
    print_header "Setting Up Backend"
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "Python dependencies installed"
    
    cd ..
    echo ""
}

# Setup frontend
setup_frontend() {
    print_header "Setting Up Frontend"
    
    cd frontend
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        print_info "Installing Node.js dependencies..."
        npm install
        print_success "Node.js dependencies installed"
    else
        print_info "Node.js dependencies already installed"
    fi
    
    cd ..
    echo ""
}

# Run tests
run_tests() {
    print_header "Running Tests"
    
    # Backend tests
    print_info "Running backend tests..."
    cd backend
    source venv/bin/activate
    pytest --cov=app --cov-report=term-missing -v
    cd ..
    
    print_success "All tests passed!"
    echo ""
}

# Start development servers
start_dev() {
    print_header "Starting Development Servers"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found, creating from .env.example..."
        cp .env.example .env
        print_success ".env file created"
    fi
    
    print_info "Starting backend server on http://localhost:8000"
    print_info "Starting frontend server on http://localhost:5173"
    echo ""
    print_info "Press Ctrl+C to stop all servers"
    echo ""
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 2
    
    # Start frontend in background
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for user to stop
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    
    # Show URLs
    echo ""
    print_success "Backend API: http://localhost:8000"
    print_success "API Docs: http://localhost:8000/docs"
    print_success "Frontend: http://localhost:5173"
    echo ""
    
    wait
}

# Docker commands
docker_up() {
    print_header "Starting Docker Containers"
    docker-compose up -d
    print_success "Containers started"
    print_info "Backend API: http://localhost:8000"
    print_info "Frontend: http://localhost:5173"
}

docker_down() {
    print_header "Stopping Docker Containers"
    docker-compose down
    print_success "Containers stopped"
}

docker_logs() {
    print_header "Docker Logs"
    docker-compose logs -f
}

# Show help
show_help() {
    echo "Nx System Calculator - Development Runner"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Install all dependencies (backend + frontend)"
    echo "  dev         - Start development servers"
    echo "  test        - Run all tests"
    echo "  docker-up   - Start Docker containers"
    echo "  docker-down - Stop Docker containers"
    echo "  docker-logs - View Docker logs"
    echo "  check       - Check prerequisites"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh setup    # First time setup"
    echo "  ./run.sh dev      # Start development"
    echo "  ./run.sh test     # Run tests"
    echo ""
}

# Main script
main() {
    case "${1:-help}" in
        setup)
            check_prerequisites
            setup_backend
            setup_frontend
            print_success "Setup complete! Run './run.sh dev' to start development servers."
            ;;
        dev)
            start_dev
            ;;
        test)
            run_tests
            ;;
        docker-up)
            docker_up
            ;;
        docker-down)
            docker_down
            ;;
        docker-logs)
            docker_logs
            ;;
        check)
            check_prerequisites
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"

