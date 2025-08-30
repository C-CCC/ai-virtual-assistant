#!/bin/bash

# DataRobot Codespaces Pulumi Deployment Script
# This script deploys the AI Virtual Assistant using Pulumi within DataRobot Codespaces

set -e

echo "🚀 DataRobot Codespaces Pulumi Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in DataRobot Codespaces
check_codespaces_environment() {
    echo -e "${BLUE}Checking DataRobot Codespaces environment...${NC}"
    
    # Check for DataRobot environment variables
    if [ -z "$DATAROBOT_API_TOKEN" ]; then
        echo -e "${RED}❌ DATAROBOT_API_TOKEN environment variable is not set${NC}"
        echo -e "${YELLOW}Please set your DataRobot API token:${NC}"
        echo -e "  export DATAROBOT_API_TOKEN='your_token_here'"
        exit 1
    fi
    
    if [ -z "$DATAROBOT_ENDPOINT" ]; then
        echo -e "${RED}❌ DATAROBOT_ENDPOINT environment variable is not set${NC}"
        echo -e "${YELLOW}Please set your DataRobot endpoint:${NC}"
        echo -e "  export DATAROBOT_ENDPOINT='https://app.datarobot.com'"
        exit 1
    fi
    
    echo -e "${GREEN}✅ DataRobot environment variables are set${NC}"
    echo -e "  Endpoint: $DATAROBOT_ENDPOINT"
    echo -e "  Project ID: ${DATAROBOT_PROJECT_ID:-'Not set (will use default)'}"
}

# Check if kubectl is available (should be in Codespaces)
check_kubectl() {
    echo -e "${BLUE}Checking kubectl availability...${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not available in this Codespace${NC}"
        echo -e "${YELLOW}Please ensure kubectl is installed in your Codespace${NC}"
        exit 1
    fi
    
    # Check if we can access a cluster
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${YELLOW}⚠️  kubectl is available but cluster is not accessible${NC}"
        echo -e "${YELLOW}This might be expected in some Codespaces environments${NC}"
    else
        echo -e "${GREEN}✅ Kubernetes cluster is accessible${NC}"
        echo -e "  Cluster: $(kubectl config current-context 2>/dev/null || echo 'Unknown')"
    fi
}

# Install Python dependencies
install_dependencies() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    # Check if we're in a virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}Using existing virtual environment: $VIRTUAL_ENV${NC}"
        PIP_FLAGS=""
    else
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        PIP_FLAGS=""
    fi
    
    echo -e "${YELLOW}Installing Pulumi dependencies...${NC}"
    pip install $PIP_FLAGS -r requirements.txt
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Install Pulumi CLI in Codespaces
install_pulumi() {
    echo -e "${BLUE}Installing Pulumi CLI...${NC}"
    
    if command -v pulumi &> /dev/null; then
        echo -e "${GREEN}✅ Pulumi is already installed${NC}"
        echo -e "  Pulumi version: $(pulumi version)"
        return
    fi
    
    echo -e "${YELLOW}Installing Pulumi CLI...${NC}"
    
    # Download and install Pulumi
    curl -fsSL https://get.pulumi.com | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.pulumi/bin:$PATH"
    
    # Verify installation
    if command -v pulumi &> /dev/null; then
        echo -e "${GREEN}✅ Pulumi installed successfully${NC}"
        echo -e "  Pulumi version: $(pulumi version)"
    else
        echo -e "${RED}❌ Pulumi installation failed${NC}"
        exit 1
    fi
}

# Deploy infrastructure using Pulumi
deploy_infrastructure() {
    echo -e "${BLUE}Deploying infrastructure with Pulumi...${NC}"
    
    # Ensure Pulumi is in PATH
    export PATH="$HOME/.pulumi/bin:$PATH"
    
    # Initialize Pulumi project if needed
    if [ ! -f "Pulumi.yaml" ]; then
        echo -e "${RED}❌ Pulumi.yaml not found. Please run this script from the pulumi directory.${NC}"
        exit 1
    fi
    
    # Create codespaces stack if it doesn't exist
    if ! pulumi stack ls 2>/dev/null | grep -q "codespaces"; then
        echo -e "${YELLOW}Creating codespaces stack...${NC}"
        pulumi stack init codespaces
    fi
    
    # Select the codespaces stack
    pulumi stack select codespaces
    
    # Set configuration from environment variables
    echo -e "${YELLOW}Setting Pulumi configuration...${NC}"
    
    # DataRobot configuration
    pulumi config set datarobot:api_token "$DATAROBOT_API_TOKEN"
    pulumi config set datarobot:endpoint "$DATAROBOT_ENDPOINT"
    
    # Set deployment IDs if available
    if [ -n "$DATAROBOT_LLM_DEPLOYMENT_ID" ]; then
        pulumi config set datarobot:deployments:llm:id "$DATAROBOT_LLM_DEPLOYMENT_ID"
    fi
    
    if [ -n "$DATAROBOT_EMBEDDING_DEPLOYMENT_ID" ]; then
        pulumi config set datarobot:deployments:embedding/id "$DATAROBOT_EMBEDDING_DEPLOYMENT_ID"
    fi
    
    if [ -n "$DATAROBOT_RERANK_DEPLOYMENT_ID" ]; then
        pulumi config set datarobot:deployments:rerank/id "$DATAROBOT_RERANK_DEPLOYMENT_ID"
    fi
    
    # Codespaces configuration
    pulumi config set codespaces:enabled "true"
    pulumi config set codespaces:environment "codespaces"
    pulumi config set codespaces:region "${DATAROBOT_REGION:-us-east-1}"
    
    if [ -n "$DATAROBOT_PROJECT_ID" ]; then
        pulumi config set codespaces:project_id "$DATAROBOT_PROJECT_ID"
    fi
    
    # Infrastructure configuration
    pulumi config set infrastructure:use_managed_postgres "false"  # Use local in Codespaces
    pulumi config set infrastructure:use_managed_redis "false"    # Use local in Codespaces
    pulumi config set infrastructure:postgres_storage "5Gi"
    pulumi config set infrastructure:agent_replicas "1"
    pulumi config set infrastructure:analytics_replicas "1"
    pulumi config set infrastructure:retriever_replicas "1"
    
    # Preview the deployment
    echo -e "${YELLOW}Previewing deployment...${NC}"
    pulumi preview
    
    read -p "Do you want to proceed with the deployment? (y/N): " CONFIRM
    if [[ $CONFIRM =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deploying infrastructure...${NC}"
        pulumi up --yes
        
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        
        # Show outputs
        echo -e "${BLUE}Deployment outputs:${NC}"
        pulumi stack output
        
        # Show next steps
        show_next_steps
        
    else
        echo -e "${YELLOW}Deployment cancelled.${NC}"
        exit 0
    fi
}

# Show next steps after deployment
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Infrastructure deployed successfully in DataRobot Codespaces!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Check deployment status: ${YELLOW}kubectl get all -n ai-virtual-assistant-codespaces${NC}"
    echo -e "2. View service logs: ${YELLOW}kubectl logs -f deployment/agent-services -n ai-virtual-assistant-codespaces${NC}"
    echo -e "3. Access the service: ${YELLOW}kubectl port-forward svc/agent-services 8000:8000 -n ai-virtual-assistant-codespaces${NC}"
    echo -e "4. Test the assistant: ${YELLOW}curl http://localhost:8000/health${NC}"
    echo -e "5. Update configuration: ${YELLOW}pulumi config set datarobot:api_token new_token${NC}"
    echo -e "6. Destroy infrastructure: ${YELLOW}pulumi destroy${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo -e "  • Check stack: ${YELLOW}pulumi stack${NC}"
    echo -e "  • View resources: ${YELLOW}pulumi stack --show-urns${NC}"
    echo -e "  • Update config: ${YELLOW}pulumi config${NC}"
    echo ""
    echo -e "${BLUE}DataRobot Codespaces specific:${NC}"
    echo -e "  • Your services are now running in the DataRobot environment"
    echo -e "  • Use the provided URLs to access your AI Virtual Assistant"
    echo -e "  • All infrastructure is managed by Pulumi and tracked in your Codespace"
}

# Main execution
main() {
    check_codespaces_environment
    check_kubectl
    install_dependencies
    install_pulumi
    deploy_infrastructure
}

# Run main function
main "$@"
