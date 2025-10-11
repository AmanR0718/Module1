#!/bin/bash

set -e

echo "🚀 Zambian Farmer Support System - Deployment Script"
echo "======================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if environment is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Environment not specified${NC}"
    echo "Usage: ./deploy.sh [development|production] [platform]"
    echo "Example: ./deploy.sh production aws"
    exit 1
fi

ENV=$1
PLATFORM=${2:-"local"}

echo -e "${YELLOW}Environment: $ENV${NC}"
echo -e "${YELLOW}Platform: $PLATFORM${NC}"
echo ""

# Validate environment
if [ "$ENV" != "development" ] && [ "$ENV" != "production" ]; then
    echo -e "${RED}Error: Invalid environment. Use 'development' or 'production'${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit .env file with your configuration before continuing${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Development deployment
if [ "$ENV" == "development" ]; then
    echo -e "${GREEN}Starting development environment...${NC}"
    
    # Build images
    echo "Building Docker images..."
    docker-compose build
    
    # Start services
    echo "Starting services..."
    docker-compose up -d
    
    # Wait for MongoDB to be ready
    echo "Waiting for MongoDB to be ready..."
    sleep 10
    
    # Initialize database
    echo "Initializing database..."
    docker-compose exec -T mongodb mongosh -u admin -p password123 \
        --authenticationDatabase admin zambian_farmers \
        /docker-entrypoint-initdb.d/init.js || true
    
    echo ""
    echo -e "${GREEN}✅ Development environment started successfully!${NC}"
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - MongoDB: localhost:27017"
    echo ""
    echo "Default login:"
    echo "  - Email: admin@zambian-farmers.zm"
    echo "  - Password: admin123"
    echo ""
    echo "View logs: docker-compose logs -f"
fi

# Production deployment
if [ "$ENV" == "production" ]; then
    echo -e "${YELLOW}⚠️  Production Deployment${NC}"
    echo ""
    
    # Validate production .env
    if grep -q "CHANGE-THIS" .env; then
        echo -e "${RED}Error: Please update .env with production values${NC}"
        echo "Search for 'CHANGE-THIS' and replace with secure values"
        exit 1
    fi
    
    # Platform-specific deployment
    case $PLATFORM in
        aws)
            echo "Deploying to AWS..."
            ./scripts/deploy-aws.sh
            ;;
        digitalocean)
            echo "Deploying to Digital Ocean..."
            ./scripts/deploy-digitalocean.sh
            ;;
        heroku)
            echo "Deploying to Heroku..."
            ./scripts/deploy-heroku.sh
            ;;
        local)
            echo "Deploying locally (production mode)..."
            docker-compose -f docker-compose.prod.yml build
            docker-compose -f docker-compose.prod.yml up -d
            ;;
        *)
            echo -e "${RED}Unknown platform: $PLATFORM${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ Production deployment complete!${NC}"
fi
