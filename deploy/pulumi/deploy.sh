#!/bin/bash

# Pulumi Deployment Script for AI Virtual Assistant
# This script deploys the infrastructure using Pulumi

set -e

echo "🚀 Pulumi Deployment for AI Virtual Assistant"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Pulumi is installed
check_pulumi() {
    echo -e "${BLUE}Checking Pulumi installation...${NC}"
    
    if ! command -v pulumi &> /dev/null; then
        echo -e "${RED}❌ Pulumi is not installed. Please install Pulumi first.${NC}"
        echo -e "${YELLOW}Install from: https://www.pulumi.com/docs/get-started/install/${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Pulumi is installed${NC}"
    echo -e "  Pulumi version: $(pulumi version)"
}

# Check if kubectl is configured
check_kubectl() {
    echo -e "${BLUE}Checking Kubernetes configuration...${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed. Please install kubectl first.${NC}"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ kubectl is not configured or cluster is not accessible.${NC}"
        echo -e "${YELLOW}Please configure kubectl to point to your target cluster.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Kubernetes cluster is accessible${NC}"
    echo -e "  Cluster: $(kubectl config current-context)"
}

# Install Python dependencies
install_dependencies() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Activating existing virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    echo -e "${YELLOW}Installing Pulumi dependencies...${NC}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${BLUE}Deploying infrastructure with Pulumi...${NC}"
    
    # Initialize Pulumi project if needed
    if [ ! -f "Pulumi.yaml" ]; then
        echo -e "${RED}❌ Pulumi.yaml not found. Please run this script from the pulumi directory.${NC}"
        exit 1
    fi
    
    # Stack selection
    echo -e "${YELLOW}Available stacks:${NC}"
    pulumi stack ls
    
    read -p "Enter stack name (or press Enter for 'dev'): " STACK_NAME
    STACK_NAME=${STACK_NAME:-dev}
    
    # Create stack if it doesn't exist
    if ! pulumi stack ls | grep -q "$STACK_NAME"; then
        echo -e "${YELLOW}Creating new stack: $STACK_NAME${NC}"
        pulumi stack init "$STACK_NAME"
    fi
    
    # Select the stack
    pulumi stack select "$STACK_NAME"
    
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
    else
        echo -e "${YELLOW}Deployment cancelled.${NC}"
        exit 0
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Infrastructure deployed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Check deployment status: ${YELLOW}kubectl get all -n ai-virtual-assistant${NC}"
    echo -e "2. View service logs: ${YELLOW}kubectl logs -f deployment/agent-services -n ai-virtual-assistant${NC}"
    echo -e "3. Access the service: ${YELLOW}kubectl port-forward svc/agent-services 8000:8000 -n ai-virtual-assistant${NC}"
    echo -e "4. Update configuration: ${YELLOW}pulumi config set datarobot:api_token new_token${NC}"
    echo -e "5. Destroy infrastructure: ${YELLOW}pulumi destroy${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo -e "  • Check stack: ${YELLOW}pulumi stack${NC}"
    echo -e "  • View resources: ${YELLOW}pulumi stack --show-urns${NC}"
    echo -e "  • Update config: ${YELLOW}pulumi config${NC}"
}

# Main execution
main() {
    check_pulumi
    check_kubectl
    install_dependencies
    deploy_infrastructure
    show_next_steps
}

# Run main function
main "$@"
