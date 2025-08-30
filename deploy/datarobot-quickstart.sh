#!/bin/bash

# DataRobot Quick Start Script for AI Virtual Assistant
# This script helps you quickly configure and deploy the system with DataRobot

set -e

echo "🚀 DataRobot Quick Start for AI Virtual Assistant"
echo "=================================================="

# Check if required tools are installed
check_requirements() {
    echo "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Requirements check passed"
}

# Get DataRobot configuration from user
get_config() {
    echo ""
    echo "Please provide your DataRobot configuration:"
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
    echo "Creating .env file..."
    
    cat > .env << EOF
# DataRobot Configuration
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
EOF

    echo "✅ Created .env file"
}

# Test DataRobot connectivity
test_connection() {
    echo ""
    echo "Testing DataRobot connectivity..."
    
    if curl -s -H "Authorization: Token ${DATAROBOT_API_TOKEN}" \
        "${DATAROBOT_ENDPOINT}/api/v2/users/me/" > /dev/null; then
        echo "✅ DataRobot connection successful"
    else
        echo "❌ DataRobot connection failed. Please check your API token and endpoint."
        exit 1
    fi
}

# Deploy with Docker Compose
deploy_docker() {
    echo ""
    echo "Deploying with Docker Compose..."
    
    # Stop any existing services
    docker compose -f deploy/compose/docker-compose.yaml down 2>/dev/null || true
    
    # Start with DataRobot configuration
    docker compose -f deploy/compose/docker-compose.yaml \
        -f deploy/compose/docker-compose-datarobot.yaml \
        --env-file .env up -d
    
    echo "✅ Deployment started"
}

# Show status
show_status() {
    echo ""
    echo "Checking service status..."
    
    sleep 10
    
    docker compose -f deploy/compose/docker-compose.yaml \
        -f deploy/compose/docker-compose-datarobot.yaml ps
    
    echo ""
    echo "🎉 Deployment complete!"
    echo ""
    echo "Next steps:"
    echo "1. Check service logs: docker compose -f deploy/compose/docker-compose.yaml -f deploy/compose/docker-compose-datarobot.yaml logs -f"
    echo "2. Access the API Gateway (check logs for port)"
    echo "3. Test with a sample query"
    echo ""
    echo "To stop services: docker compose -f deploy/compose/docker-compose.yaml -f deploy/compose/docker-compose-datarobot.yaml down"
}

# Main execution
main() {
    check_requirements
    get_config
    create_env_file
    test_connection
    deploy_docker
    show_status
}

# Run main function
main "$@"
