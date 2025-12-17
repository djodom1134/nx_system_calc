#!/bin/bash
# =============================================================================
# AWS Deployment Script for Nx System Calculator
# =============================================================================
# This script helps deploy the application to AWS EC2 or ECS
# Usage: ./scripts/deploy-aws.sh [command]
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker installed: $(docker --version)"
    else
        print_error "Docker not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose installed: $(docker-compose --version)"
    else
        print_error "Docker Compose not installed"
        exit 1
    fi
    
    # Check for .env file
    if [ -f ".env" ]; then
        print_success ".env file exists"
    else
        print_warning ".env file not found - copying from .env.example"
        cp .env.example .env
        print_warning "Please edit .env with your production settings!"
    fi
    
    # Check for config directory
    if [ -d "config" ]; then
        print_success "Config directory exists"
        # Validate JSON files
        for file in config/*.json; do
            if python3 -m json.tool "$file" > /dev/null 2>&1; then
                print_success "Valid JSON: $file"
            else
                print_error "Invalid JSON: $file"
                exit 1
            fi
        done
    else
        print_error "Config directory not found!"
        exit 1
    fi
}

# Build images
build_images() {
    print_header "Building Docker Images"
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    print_success "Images built successfully"
}

# Start services
start_services() {
    print_header "Starting Services"
    
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Services started"
    
    # Wait for services to be healthy
    print_header "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    docker-compose -f docker-compose.prod.yml ps
}

# Stop services
stop_services() {
    print_header "Stopping Services"
    
    docker-compose -f docker-compose.prod.yml down
    
    print_success "Services stopped"
}

# View logs
view_logs() {
    print_header "Viewing Logs"
    docker-compose -f docker-compose.prod.yml logs -f
}

# Run database migrations
run_migrations() {
    print_header "Running Database Migrations"
    
    docker-compose -f docker-compose.prod.yml exec backend \
        python3 -c "from app.models.base import init_db; init_db()"
    
    print_success "Database initialized"
}

# Verify deployment
verify_deployment() {
    print_header "Verifying Deployment"
    
    # Check backend health
    if curl -sf http://localhost:8000/health > /dev/null; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
    fi
    
    # Check frontend
    if curl -sf http://localhost/health > /dev/null; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend health check failed"
    fi
    
    # Check API endpoints
    if curl -sf http://localhost:8000/api/v1/config/raid-types > /dev/null; then
        print_success "API config endpoints working"
    else
        print_error "API config endpoints failed - check CONFIG_DIR"
    fi
    
    print_header "Deployment Status"
    docker-compose -f docker-compose.prod.yml ps
}

# Show help
show_help() {
    echo "AWS Deployment Script for Nx System Calculator"
    echo ""
    echo "Usage: ./scripts/deploy-aws.sh [command]"
    echo ""
    echo "Commands:"
    echo "  check      - Check prerequisites"
    echo "  build      - Build Docker images"
    echo "  start      - Start all services"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  logs       - View logs"
    echo "  migrate    - Run database migrations"
    echo "  verify     - Verify deployment"
    echo "  deploy     - Full deployment (check, build, start, verify)"
    echo "  help       - Show this help message"
}

# Main
case "${1:-help}" in
    check)
        check_prerequisites
        ;;
    build)
        build_images
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    logs)
        view_logs
        ;;
    migrate)
        run_migrations
        ;;
    verify)
        verify_deployment
        ;;
    deploy)
        check_prerequisites
        build_images
        start_services
        sleep 15
        run_migrations
        verify_deployment
        print_header "Deployment Complete!"
        echo "Frontend: http://localhost (or your domain)"
        echo "API Docs: http://localhost:8000/docs"
        ;;
    help|*)
        show_help
        ;;
esac

