#!/bin/bash

# DataRobot Codespaces Python-Only Quick Start Script
# This script runs services directly without Docker - perfect for Codespaces

set -e

echo "🚀 DataRobot Codespaces Python-Only Quick Start"
echo "================================================"

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

# Check Python requirements
check_python() {
    echo -e "${BLUE}Checking Python environment...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 is not installed. Please install Python 3.8+ first.${NC}"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 is not installed. Please install pip first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python environment check passed${NC}"
    echo -e "  Python version: $(python3 --version)"
    echo -e "  Pip version: $(pip3 --version)"
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
# DataRobot Configuration for Codespaces (Python-only)
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

# Install dependencies
install_dependencies() {
    echo ""
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    echo -e "${YELLOW}Installing agent service dependencies...${NC}"
    pip3 install --user -r src/agent/requirements.txt
    
    echo -e "${YELLOW}Installing analytics service dependencies...${NC}"
    pip3 install --user -r src/analytics/requirements.txt
    
    echo -e "${YELLOW}Installing retriever dependencies...${NC}"
    pip3 install --user -r src/retrievers/unstructured_data/requirements.txt
    pip3 install --user -r src/retrievers/structured_data/requirements.txt
    
    echo -e "${GREEN}✅ All dependencies installed${NC}"
}

# Create startup script
create_startup_script() {
    echo ""
    echo -e "${BLUE}Creating startup script...${NC}"
    
    cat > start-services.sh << 'EOF'
#!/bin/bash

# Startup script for DataRobot Codespaces
# This script starts all services in the background

echo "🚀 Starting AI Virtual Assistant services..."

# Load environment variables
source .env

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local service_file=$3
    local port=$4
    
    echo "Starting $service_name on port $port..."
    cd "$service_dir"
    nohup python3 "$service_file" > "../logs/${service_name}.log" 2>&1 &
    echo $! > "../logs/${service_name}.pid"
    cd ..
    echo "✅ $service_name started (PID: $(cat logs/${service_name}.pid))"
}

# Create logs directory
mkdir -p logs

# Start services
start_service "agent-services" "src/agent" "main.py" "8000"
sleep 2

start_service "analytics-services" "src/analytics" "main.py" "8001"
sleep 2

start_service "retriever-canonical" "src/retrievers" "server.py" "8003"
sleep 2

start_service "retriever-structured" "src/retrievers" "server.py" "8004"
sleep 2

echo ""
echo "🎉 All services started!"
echo ""
echo "Service URLs:"
echo "  • Agent Services: http://localhost:8000"
echo "  • Analytics Services: http://localhost:8001"
echo "  • Retriever Canonical: http://localhost:8003"
echo "  • Retriever Structured: http://localhost:8004"
echo ""
echo "To check service status: ./check-services.sh"
echo "To stop all services: ./stop-services.sh"
echo "To view logs: tail -f logs/[service-name].log"
EOF

    chmod +x start-services.sh
    echo -e "${GREEN}✅ Created start-services.sh script${NC}"
}

# Create service management scripts
create_management_scripts() {
    echo ""
    echo -e "${BLUE}Creating service management scripts...${NC}"
    
    # Check services script
    cat > check-services.sh << 'EOF'
#!/bin/bash

echo "🔍 Checking service status..."
echo ""

for service in agent-services analytics-services retriever-canonical retriever-structured; do
    if [ -f "logs/${service}.pid" ]; then
        pid=$(cat "logs/${service}.pid")
        if ps -p $pid > /dev/null 2>&1; then
            echo "✅ $service: Running (PID: $pid)"
        else
            echo "❌ $service: Not running (stale PID file)"
            rm -f "logs/${service}.pid"
        fi
    else
        echo "❌ $service: Not started"
    fi
done

echo ""
echo "Service URLs:"
echo "  • Agent Services: http://localhost:8000"
echo "  • Analytics Services: http://localhost:8001"
echo "  • Retriever Canonical: http://localhost:8003"
echo "  • Retriever Structured: http://localhost:8004"
EOF

    # Stop services script
    cat > stop-services.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping all services..."
echo ""

for service in agent-services analytics-services retriever-canonical retriever-structured; do
    if [ -f "logs/${service}.pid" ]; then
        pid=$(cat "logs/${service}.pid")
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping $service (PID: $pid)..."
            kill $pid
            rm -f "logs/${service}.pid"
            echo "✅ $service stopped"
        else
            echo "⚠️  $service not running (stale PID file)"
            rm -f "logs/${service}.pid"
        fi
    else
        echo "⚠️  $service not started"
    fi
done

echo ""
echo "🎉 All services stopped!"
EOF

    chmod +x check-services.sh stop-services.sh
    echo -e "${GREEN}✅ Created service management scripts${NC}"
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Setup complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Start all services: ${YELLOW}./start-services.sh${NC}"
    echo -e "2. Check service status: ${YELLOW}./check-services.sh${NC}"
    echo -e "3. Stop all services: ${YELLOW}./stop-services.sh${NC}"
    echo -e "4. View service logs: ${YELLOW}tail -f logs/[service-name].log${NC}"
    echo ""
    echo -e "${BLUE}Service URLs (after starting):${NC}"
    echo -e "  • Agent Services: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • Analytics Services: ${GREEN}http://localhost:8001${NC}"
    echo -e "  • Retriever Canonical: ${GREEN}http://localhost:8003${NC}"
    echo -e "  • Retriever Structured: ${GREEN}http://localhost:8004${NC}"
    echo ""
    echo -e "${BLUE}Files created:${NC}"
    echo -e "  • ${GREEN}.env${NC} - Your DataRobot configuration"
    echo -e "  • ${GREEN}start-services.sh${NC} - Start all services"
    echo -e "  • ${GREEN}check-services.sh${NC} - Check service status"
    echo -e "  • ${GREEN}stop-services.sh${NC} - Stop all services"
    echo ""
    echo -e "${YELLOW}Ready to start services? Run: ./start-services.sh${NC}"
}

# Main execution
main() {
    check_codespaces
    check_python
    get_config
    create_env_file
    test_connection
    install_dependencies
    create_startup_script
    create_management_scripts
    show_next_steps
}

# Run main function
main "$@"
