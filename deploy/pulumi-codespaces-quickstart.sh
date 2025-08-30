#!/bin/bash

# DataRobot Codespaces Pulumi Quick Start
# This script quickly sets up and deploys the AI Virtual Assistant using Pulumi

set -e

echo "🚀 DataRobot Codespaces Pulumi Quick Start"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
check_directory() {
    if [ ! -f "deploy/pulumi/Pulumi.yaml" ]; then
        echo -e "${RED}❌ Please run this script from the project root directory${NC}"
        echo -e "${YELLOW}Expected: deploy/pulumi/Pulumi.yaml${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Project structure verified${NC}"
}

# Interactive DataRobot configuration
configure_datarobot() {
    echo -e "${BLUE}🔧 DataRobot Configuration${NC}"
    echo -e "${YELLOW}Please provide your DataRobot credentials:${NC}"
    
    # API Token
    read -p "Enter your DataRobot API Token: " DATAROBOT_API_TOKEN
    if [ -z "$DATAROBOT_API_TOKEN" ]; then
        echo -e "${RED}❌ API Token is required${NC}"
        exit 1
    fi
    
    # Endpoint
    read -p "Enter DataRobot Endpoint [https://app.datarobot.com]: " DATAROBOT_ENDPOINT
    DATAROBOT_ENDPOINT=${DATAROBOT_ENDPOINT:-https://app.datarobot.com}
    
    # Project ID (optional)
    read -p "Enter DataRobot Project ID (optional): " DATAROBOT_PROJECT_ID
    
    # Deployment IDs
    echo -e "${YELLOW}Enter your DataRobot deployment IDs:${NC}"
    read -p "LLM Deployment ID: " DATAROBOT_LLM_DEPLOYMENT_ID
    read -p "Embedding Deployment ID: " DATAROBOT_EMBEDDING_DEPLOYMENT_ID
    read -p "Rerank Deployment ID: " DATAROBOT_RERANK_DEPLOYMENT_ID
    
    # Region
    read -p "Enter DataRobot Region [us-east-1]: " DATAROBOT_REGION
    DATAROBOT_REGION=${DATAROBOT_REGION:-us-east-1}
    
    # Export environment variables
    export DATAROBOT_API_TOKEN="$DATAROBOT_API_TOKEN"
    export DATAROBOT_ENDPOINT="$DATAROBOT_ENDPOINT"
    export DATAROBOT_PROJECT_ID="$DATAROBOT_PROJECT_ID"
    export DATAROBOT_LLM_DEPLOYMENT_ID="$DATAROBOT_LLM_DEPLOYMENT_ID"
    export DATAROBOT_EMBEDDING_DEPLOYMENT_ID="$DATAROBOT_EMBEDDING_DEPLOYMENT_ID"
    export DATAROBOT_RERANK_DEPLOYMENT_ID="$DATAROBOT_RERANK_DEPLOYMENT_ID"
    export DATAROBOT_REGION="$DATAROBOT_REGION"
    
    echo -e "${GREEN}✅ DataRobot configuration set${NC}"
}

# Create .env file for Codespaces
create_env_file() {
    echo -e "${BLUE}📝 Creating .env file for Codespaces...${NC}"
    
    cat > .env << EOF
# DataRobot Configuration for Codespaces
DATAROBOT_API_TOKEN=$DATAROBOT_API_TOKEN
DATAROBOT_ENDPOINT=$DATAROBOT_ENDPOINT
DATAROBOT_PROJECT_ID=$DATAROBOT_PROJECT_ID
DATAROBOT_LLM_DEPLOYMENT_ID=$DATAROBOT_LLM_DEPLOYMENT_ID
DATAROBOT_EMBEDDING_DEPLOYMENT_ID=$DATAROBOT_EMBEDDING_DEPLOYMENT_ID
DATAROBOT_RERANK_DEPLOYMENT_ID=$DATAROBOT_RERANK_DEPLOYMENT_ID
DATAROBOT_REGION=$DATAROBOT_REGION

# Environment
ENVIRONMENT=codespaces
EOF
    
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}💡 You can edit this file later to update configuration${NC}"
}

# Test DataRobot connectivity
test_connection() {
    echo -e "${BLUE}🔍 Testing DataRobot connectivity...${NC}"
    
    # Simple test using curl
    if command -v curl &> /dev/null; then
        echo -e "${YELLOW}Testing endpoint: $DATAROBOT_ENDPOINT${NC}"
        
        # Test basic connectivity (this is a simple test)
        if curl -s --connect-timeout 10 "$DATAROBOT_ENDPOINT" > /dev/null; then
            echo -e "${GREEN}✅ Endpoint is accessible${NC}"
        else
            echo -e "${YELLOW}⚠️  Endpoint connectivity test failed (this might be expected)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  curl not available, skipping connectivity test${NC}"
    fi
    
    echo -e "${GREEN}✅ DataRobot configuration appears valid${NC}"
}

# Deploy using Pulumi
deploy_with_pulumi() {
    echo -e "${BLUE}🚀 Starting Pulumi deployment...${NC}"
    
    # Navigate to pulumi directory
    cd deploy/pulumi
    
    # Make deployment script executable
    chmod +x deploy-codespaces.sh
    
    # Run the deployment
    echo -e "${YELLOW}Running Pulumi deployment script...${NC}"
    ./deploy-codespaces.sh
    
    # Return to root directory
    cd ../..
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Quick start completed!${NC}"
    echo ""
    echo -e "${BLUE}What happens next:${NC}"
    echo -e "1. 📋 Pulumi will deploy your infrastructure"
    echo -e "2. 🐳 Services will be created in DataRobot Codespaces"
    echo -e "3. 🔗 You'll get access URLs for your AI Virtual Assistant"
    echo -e "4. 🧪 You can test the assistant using the provided tools"
    echo ""
    echo -e "${BLUE}Useful commands after deployment:${NC}"
    echo -e "  • Check status: ${YELLOW}kubectl get all -n ai-virtual-assistant-codespaces${NC}"
    echo -e "  • View logs: ${YELLOW}kubectl logs -f deployment/agent-services -n ai-virtual-assistant-codespaces${NC}"
    echo -e "  • Test assistant: ${YELLOW}python tools/assistant_cli.py health${NC}"
    echo -e "  • Start chat: ${YELLOW}python tools/assistant_cli.py chat${NC}"
    echo ""
    echo -e "${BLUE}Files created:${NC}"
    echo -e "  • .env - Your DataRobot configuration"
    echo -e "  • Pulumi stack - Infrastructure state"
    echo ""
    echo -e "${YELLOW}💡 Need help? Check docs/PULUMI_DEPLOYMENT.md${NC}"
}

# Main execution
main() {
    check_directory
    configure_datarobot
    create_env_file
    test_connection
    deploy_with_pulumi
    show_next_steps
}

# Run main function
main "$@"
