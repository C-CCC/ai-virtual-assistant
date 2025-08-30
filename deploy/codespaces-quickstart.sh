#!/bin/bash

# DataRobot Codespaces Docker Quick Start Script
# This script uses Docker Compose to run services - requires Docker and jq
# For Python-only deployment (no Docker required), use: deploy/codespaces-python-quickstart.sh

set -e

echo "🚀 DataRobot Codespaces Docker Quick Start"
echo "=========================================="
echo -e "${YELLOW}Note: This script requires Docker and jq${NC}"
echo -e "${YELLOW}For Python-only deployment, use: ./deploy/codespaces-python-quickstart.sh${NC}"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in a Codespaces environment
check_codespaces() {
    echo -e "${BLUE}Checking Codespaces environment...${NC}"
    
    if [[ -n "$CODESPACES" ]]; then
        echo -e "${GREEN}✅ Running in DataRobot Codespaces${NC}"
    else
        echo -e "${YELLOW}⚠️  Not running in Codespaces - some features may not work optimally${NC}"
    fi
}

# Check requirements
check_requirements() {
    echo -e "${BLUE}Checking requirements...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Requirements check passed${NC}"
}

# Get DataRobot configuration
get_config() {
    echo ""
    echo -e "${BLUE}Please provide your DataRobot configuration:${NC}"
    echo ""
    
    read -p "DataRobot API Token: " DATAROBOT_API_TOKEN
    read -p "DataRobot Endpoint [https://app.datarobot.com]: " DATAROBOT_ENDPOINT
    DATAROBOT_ENDPOINT=${DATAROBOT_ENDPOINT:-https://app.datarobot.com}
    
    read -p "LLM Deployment ID: " DATAROBOT_LLM_DEPLOYMENT_ID
    read -p "Embedding Deployment ID: " DATAROBOT_EMBEDDING_DEPLOYMENT_ID
    read -p "Rerank Deployment ID: " DATAROBOT_RERANK_DEPLOYMENT_ID
    
    read -p "LLM Model Name [datarobot-llm]: " LLM_MODEL_NAME
    LLM_MODEL_NAME=${LLM_MODEL_NAME:-datarobot-llm}
    
    read -p "Embedding Model Name [datarobot-embedding]: " EMBEDDING_MODEL_NAME
    EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME:-datarobot-embedding}
    
    read -p "Rerank Model Name [datarobot-rerank]: " RERANK_MODEL_NAME
    RERANK_MODEL_NAME=${RERANK_MODEL_NAME:-datarobot-rerank}
}

# Create environment file
create_env_file() {
    echo ""
    echo -e "${BLUE}Creating .env file...${NC}"
    
    cat > .env << EOF
# DataRobot Configuration for Codespaces
DATAROBOT_API_TOKEN=${DATAROBOT_API_TOKEN}
DATAROBOT_ENDPOINT=${DATAROBOT_ENDPOINT}
DATAROBOT_LLM_DEPLOYMENT_ID=${DATAROBOT_LLM_DEPLOYMENT_ID}
DATAROBOT_EMBEDDING_DEPLOYMENT_ID=${DATAROBOT_EMBEDDING_DEPLOYMENT_ID}
DATAROBOT_RERANK_DEPLOYMENT_ID=${DATAROBOT_RERANK_DEPLOYMENT_ID}

# Model Names
LLM_MODEL_NAME=${LLM_MODEL_NAME}
EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME}
RERANK_MODEL_NAME=${RERANK_MODEL_NAME}

# Engine Configuration
LLM_MODEL_ENGINE=datarobot
EMBEDDING_MODEL_ENGINE=datarobot
RANKING_MODEL_ENGINE=datarobot

# Codespaces specific settings
LOGLEVEL=INFO
EOF

    echo -e "${GREEN}✅ Created .env file${NC}"
}

# Test DataRobot connectivity
test_connection() {
    echo ""
    echo -e "${BLUE}Testing DataRobot connectivity...${NC}"
    
    if curl -s -H "Authorization: Token ${DATAROBOT_API_TOKEN}" \
        "${DATAROBOT_ENDPOINT}/api/v2/users/me/" > /dev/null; then
        echo -e "${GREEN}✅ DataRobot connection successful${NC}"
    else
        echo -e "${RED}❌ DataRobot connection failed. Please check your API token and endpoint.${NC}"
        exit 1
    fi
}

# Build and deploy with Docker Compose
deploy_docker() {
    echo ""
    echo -e "${BLUE}Building and deploying with Docker Compose...${NC}"
    
    # Stop any existing services
    docker compose -f deploy/compose/docker-compose-codespaces.yaml down 2>/dev/null || true
    
    # Build and start services
    echo -e "${YELLOW}Building services (this may take a few minutes)...${NC}"
    docker compose -f deploy/compose/docker-compose-codespaces.yaml \
        --env-file .env build
    
    echo -e "${YELLOW}Starting services...${NC}"
    docker compose -f deploy/compose/docker-compose-codespaces.yaml \
        --env-file .env up -d
    
    echo -e "${GREEN}✅ Deployment started${NC}"
}

# Wait for services to be ready
wait_for_services() {
    echo ""
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}Attempt $attempt/$max_attempts - Checking service health...${NC}"
        
        # Check if all services are healthy
        local healthy_count=$(docker compose -f deploy/compose/docker-compose-codespaces.yaml ps --format json | jq -r '.[] | select(.Health == "healthy") | .Name' | wc -l)
        local total_count=$(docker compose -f deploy/compose/docker-compose-codespaces.yaml ps --format json | jq -r '.[] | .Name' | wc -l)
        
        if [ "$healthy_count" -eq "$total_count" ]; then
            echo -e "${GREEN}✅ All services are healthy!${NC}"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            echo -e "${RED}❌ Timeout waiting for services to be ready${NC}"
            echo -e "${YELLOW}Check service logs for more details${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}Waiting 10 seconds before next check...${NC}"
        sleep 10
        attempt=$((attempt + 1))
    done
}

# Show status and next steps
show_status() {
    echo ""
    echo -e "${BLUE}Checking service status...${NC}"
    
    docker compose -f deploy/compose/docker-compose-codespaces.yaml ps
    
    echo ""
    echo -e "${GREEN}🎉 Deployment complete!${NC}"
    echo ""
    echo -e "${BLUE}Service URLs (accessible from Codespaces):${NC}"
    echo -e "  • Agent Services: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • Analytics Services: ${GREEN}http://localhost:8001${NC}"
    echo -e "  • API Gateway: ${GREEN}http://localhost:8002${NC}"
    echo -e "  • Retriever Canonical: ${GREEN}http://localhost:8003${NC}"
    echo -e "  • Retriever Structured: ${GREEN}http://localhost:8004${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Check service logs: ${YELLOW}docker compose -f deploy/compose/docker-compose-codespaces.yaml logs -f${NC}"
    echo -e "2. Test the API Gateway at ${GREEN}http://localhost:8002${NC}"
    echo -e "3. Access service documentation at ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${BLUE}To stop services:${NC}"
    echo -e "  ${YELLOW}docker compose -f deploy/compose/docker-compose-codespaces.yaml down${NC}"
    echo ""
    echo -e "${BLUE}To restart services:${NC}"
    echo -e "  ${YELLOW}docker compose -f deploy/compose/docker-compose-codespaces.yaml restart${NC}"
}

# Main execution
main() {
    check_codespaces
    check_requirements
    get_config
    create_env_file
    test_connection
    deploy_docker
    wait_for_services
    show_status
}

# Check if jq is installed for JSON parsing
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq not found. Installing...${NC}"
    
    # Try different package managers
    if command -v apt-get &> /dev/null; then
        echo -e "${BLUE}Trying apt-get...${NC}"
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v yum &> /dev/null; then
        echo -e "${BLUE}Trying yum...${NC}"
        sudo yum install -y jq
    elif command -v brew &> /dev/null; then
        echo -e "${BLUE}Trying brew...${NC}"
        brew install jq
    elif command -v apk &> /dev/null; then
        echo -e "${BLUE}Trying apk...${NC}"
        sudo apk add jq
    else
        echo -e "${RED}❌ Cannot install jq automatically.${NC}"
        echo -e "${YELLOW}Please install jq manually using one of these methods:${NC}"
        echo -e "  • Ubuntu/Debian: ${BLUE}sudo apt-get install jq${NC}"
        echo -e "  • CentOS/RHEL: ${BLUE}sudo yum install jq${NC}"
        echo -e "  • macOS: ${BLUE}brew install jq${NC}"
        echo -e "  • Alpine: ${BLUE}sudo apk add jq${NC}"
        echo -e "  • Or download from: ${BLUE}https://stedolan.github.io/jq/download/${NC}"
        echo ""
        echo -e "${YELLOW}Alternatively, use the Python-only quickstart:${NC}"
        echo -e "  ${BLUE}./deploy/codespaces-python-quickstart.sh${NC}"
        exit 1
    fi
    
    # Verify installation
    if command -v jq &> /dev/null; then
        echo -e "${GREEN}✅ jq installed successfully${NC}"
    else
        echo -e "${RED}❌ jq installation failed${NC}"
        exit 1
    fi
fi

# Run main function
main "$@"
