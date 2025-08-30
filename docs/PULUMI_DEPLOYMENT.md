# Pulumi Deployment Guide for AI Virtual Assistant

This guide explains how to deploy the AI Virtual Assistant using Pulumi for Infrastructure as Code (IaC) deployment, with specific support for **DataRobot Codespaces**.

## 🚀 **Why Pulumi Instead of Helm/Docker Compose?**

### **Advantages of Pulumi:**
- **✅ Infrastructure as Code** - Version controlled, repeatable deployments
- **✅ Multi-Cloud Support** - Deploy to AWS, GCP, Azure, or on-premises
- **✅ State Management** - Track infrastructure changes and dependencies
- **✅ Complex Resource Dependencies** - Handle complex infrastructure relationships
- **✅ Programming Language** - Use Python for logic and configuration
- **✅ CI/CD Integration** - Easy integration with DataRobot pipelines
- **✅ Resource Scaling** - Built-in autoscaling and load balancing

### **What We're Replacing:**
- **❌ Helm Charts** - Limited to Kubernetes, no cloud resources
- **❌ Docker Compose** - Single-node only, no scaling
- **❌ Manual Configuration** - Error-prone, not repeatable

## 🎯 **Deployment Options**

### **1. 🏠 Local/Desktop Deployment**
- Traditional Pulumi installation
- Local Kubernetes cluster
- Full infrastructure control

### **2. 🚀 DataRobot Codespaces Deployment (Recommended)**
- **No local Pulumi installation required**
- **Automatic Pulumi CLI installation**
- **DataRobot-native environment**
- **Integrated with DataRobot services**

---

## 📋 **Prerequisites**

### **For Local/Desktop Deployment:**
1. **Pulumi CLI**: Install from [pulumi.com](https://www.pulumi.com/docs/get-started/install/)
2. **Kubernetes Cluster**: Accessible via kubectl
3. **DataRobot Account**: With API access and deployments
4. **Python 3.8+**: For Pulumi Python runtime

### **For DataRobot Codespaces Deployment:**
1. **DataRobot Codespaces Environment**: Active Codespace
2. **DataRobot Account**: With API access and deployments
3. **Python 3.8+**: Available in Codespaces
4. **kubectl**: Available in Codespaces (usually pre-installed)

---

## 🔧 **Installation & Setup**

### **Option 1: DataRobot Codespaces (Recommended)**

#### **Quick Start (Automated)**
```bash
# From project root
chmod +x deploy/pulumi-codespaces-quickstart.sh
./deploy/pulumi-codespaces-quickstart.sh
```

#### **Manual Setup**
```bash
# 1. Set environment variables
export DATAROBOT_API_TOKEN="your_token"
export DATAROBOT_ENDPOINT="https://app.datarobot.com"
export DATAROBOT_PROJECT_ID="your_project_id"  # Optional
export DATAROBOT_LLM_DEPLOYMENT_ID="your_llm_id"
export DATAROBOT_EMBEDDING_DEPLOYMENT_ID="your_embedding_id"
export DATAROBOT_RERANK_DEPLOYMENT_ID="your_rerank_id"

# 2. Deploy using Pulumi
cd deploy/pulumi
chmod +x deploy-codespaces.sh
./deploy-codespaces.sh
```

### **Option 2: Local/Desktop Installation**

#### **Install Pulumi CLI**
```bash
# macOS
brew install pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows
winget install Pulumi.Pulumi
```

#### **Verify Installation**
```bash
pulumi version
pulumi plugin ls
```

---

## 🏗️ **Project Structure**

### **DataRobot Codespaces Structure**
```
deploy/pulumi/
├── Pulumi.yaml                    # Project configuration
├── codespaces_main.py             # Codespaces infrastructure code
├── Pulumi.codespaces.yaml         # Codespaces configuration
├── requirements-codespaces.txt     # Codespaces dependencies
├── deploy-codespaces.sh           # Codespaces deployment script
└── deploy.sh                      # Local deployment script
```

### **Local/Desktop Structure**
```
deploy/pulumi/
├── Pulumi.yaml                    # Project configuration
├── __main__.py                    # Local infrastructure code
├── Pulumi.prod.yaml              # Production configuration
├── requirements.txt               # Local dependencies
└── deploy.sh                     # Local deployment script
```

---

## 🚀 **Quick Start**

### **DataRobot Codespaces (Recommended)**
```bash
# 1. Quick start (interactive)
./deploy/pulumi-codespaces-quickstart.sh

# 2. Or manual deployment
cd deploy/pulumi
./deploy-codespaces.sh
```

### **Local/Desktop Deployment**
```bash
cd deploy/pulumi

# Install dependencies
pip install -r requirements.txt

# Initialize project
pulumi stack init dev

# Configure DataRobot settings
pulumi config set datarobot:api_token "your_token"
pulumi config set datarobot:endpoint "https://app.datarobot.com"
pulumi config set datarobot:deployments:llm/id "your_llm_id"
pulumi config set datarobot:deployments:embedding/id "your_embedding_id"
pulumi config set datarobot:deployments:rerank/id "your_rerank_id"

# Deploy
pulumi up --yes
```

---

## ⚙️ **Configuration**

### **DataRobot Codespaces Configuration**
```yaml
# Pulumi.codespaces.yaml
config:
  ai-virtual-assistant-datarobot:datarobot:
    api_token: "${DATAROBOT_API_TOKEN}"
    endpoint: "${DATAROBOT_ENDPOINT}"
    deployments:
      llm:
        id: "${DATAROBOT_LLM_DEPLOYMENT_ID}"
        model_name: "${DATAROBOT_LLM_MODEL_NAME}"
      embedding:
        id: "${DATAROBOT_EMBEDDING_DEPLOYMENT_ID}"
        model_name: "${DATAROBOT_EMBEDDING_MODEL_NAME}"
      rerank:
        id: "${DATAROBOT_RERANK_DEPLOYMENT_ID}"
        model_name: "${DATAROBOT_RERANK_MODEL_NAME}"
  
  # Codespaces specific configuration
  ai-virtual-assistant-datarobot:codespaces:
    enabled: true
    environment: "codespaces"
    region: "${DATAROBOT_REGION:-us-east-1}"
    project_id: "${DATAROBOT_PROJECT_ID}"
    
  # Infrastructure configuration for Codespaces
  ai-virtual-assistant-datarobot:infrastructure:
    use_managed_postgres: false  # Use local in Codespaces
    use_managed_redis: false    # Use local in Codespaces
    postgres_storage: "5Gi"     # Smaller for development
    agent_replicas: 1           # Single instance for development
```

### **Environment Variables for Codespaces**
```bash
# Required
export DATAROBOT_API_TOKEN="your_token"
export DATAROBOT_ENDPOINT="https://app.datarobot.com"

# Optional
export DATAROBOT_PROJECT_ID="your_project_id"
export DATAROBOT_LLM_DEPLOYMENT_ID="your_llm_id"
export DATAROBOT_EMBEDDING_DEPLOYMENT_ID="your_embedding_id"
export DATAROBOT_RERANK_DEPLOYMENT_ID="your_rerank_id"
export DATAROBOT_REGION="us-east-1"
```

---

## 🏗️ **Infrastructure Components**

### **DataRobot Codespaces Components**
1. **Namespace**: Isolated Kubernetes namespace for Codespaces
2. **DataRobot Secrets**: Secure storage of API tokens and deployment IDs
3. **Local Services**: PostgreSQL, Redis, Milvus (optimized for development)
4. **Application Services**: Agent, Analytics, Retriever services
5. **DataRobot Ingress**: Integration with DataRobot's ingress controller

### **Local/Desktop Components**
1. **Namespace**: Production-ready Kubernetes namespace
2. **DataRobot Secrets**: Secure storage of credentials
3. **Database Layer**: PostgreSQL with persistent storage
4. **Vector Database**: Milvus for embeddings
5. **Application Services**: Scalable agent services
6. **Networking**: Ingress with TLS termination
7. **Autoscaling**: Horizontal Pod Autoscaler

---

## 🔄 **Deployment Workflow**

### **DataRobot Codespaces Workflow**
```bash
# 1. Set environment variables
export DATAROBOT_API_TOKEN="your_token"
export DATAROBOT_ENDPOINT="https://app.datarobot.com"

# 2. Quick start (recommended)
./deploy/pulumi-codespaces-quickstart.sh

# 3. Or manual deployment
cd deploy/pulumi
./deploy-codespaces.sh
```

### **Local/Desktop Workflow**
```bash
# 1. Install Pulumi CLI
brew install pulumi  # macOS

# 2. Deploy infrastructure
cd deploy/pulumi
./deploy.sh
```

---

## 📊 **Monitoring and Management**

### **Check Deployment Status**
```bash
# Codespaces
kubectl get all -n ai-virtual-assistant-codespaces

# Local
kubectl get all -n ai-virtual-assistant
```

### **View Logs**
```bash
# Application logs
kubectl logs -f deployment/agent-services -n ai-virtual-assistant-codespaces

# Infrastructure logs
pulumi logs --follow
```

### **Scale Services**
```bash
# Manual scaling
kubectl scale deployment agent-services --replicas=2 -n ai-virtual-assistant-codespaces

# Or update Pulumi config
pulumi config set infrastructure:agent_replicas 2
pulumi up --yes
```

---

## 🔒 **Security Features**

### **DataRobot Codespaces Security**
- **Secrets Management**: Kubernetes secrets for sensitive data
- **Environment Isolation**: Dedicated namespace for Codespaces
- **DataRobot Integration**: Secure API token handling
- **Resource Limits**: Controlled resource usage for development

### **Local/Desktop Security**
- **Secrets Management**: Kubernetes secrets for sensitive data
- **Network Policies**: Pod-to-pod communication control
- **RBAC**: Service account permissions
- **TLS Termination**: Secure ingress configuration

---

## 🚀 **Advanced Features**

### **Multi-Environment Deployment**
```bash
# Deploy to multiple environments
for env in dev staging prod; do
    pulumi stack select $env
    pulumi up --yes
done
```

### **CI/CD Integration**
```yaml
# GitHub Actions example for Codespaces
- name: Deploy with Pulumi
  run: |
    cd deploy/pulumi
    export DATAROBOT_API_TOKEN=${{ secrets.DATAROBOT_API_TOKEN }}
    export DATAROBOT_ENDPOINT=${{ secrets.DATAROBOT_ENDPOINT }}
    ./deploy-codespaces.sh
```

---

## 🔧 **Troubleshooting**

### **DataRobot Codespaces Issues**

1. **Pulumi Not Installed**
   ```bash
   # The script automatically installs Pulumi
   # If manual installation needed:
   curl -fsSL https://get.pulumi.com | sh
   export PATH="$HOME/.pulumi/bin:$PATH"
   ```

2. **Environment Variables Missing**
   ```bash
   # Check required variables
   echo $DATAROBOT_API_TOKEN
   echo $DATAROBOT_ENDPOINT
   
   # Set if missing
   export DATAROBOT_API_TOKEN="your_token"
   export DATAROBOT_ENDPOINT="https://app.datarobot.com"
   ```

3. **Kubernetes Not Accessible**
   ```bash
   # Check kubectl
   kubectl cluster-info
   
   # This might be expected in some Codespaces environments
   ```

### **Local/Desktop Issues**

1. **Pulumi Not Installed**
   ```bash
   # Install Pulumi
   curl -fsSL https://get.pulumi.com | sh
   ```

2. **Kubernetes Not Accessible**
   ```bash
   # Check cluster access
   kubectl cluster-info
   kubectl config current-context
   ```

---

## 📚 **Additional Resources**

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi Kubernetes Provider](https://www.pulumi.com/registry/packages/kubernetes/)
- [DataRobot API Documentation](https://docs.datarobot.com/en/docs/api/)
- [DataRobot Codespaces Documentation](https://docs.datarobot.com/en/docs/codespaces/)

---

## 🆘 **Getting Help**

- **Pulumi Community**: [Community Slack](https://slack.pulumi.com/)
- **DataRobot Support**: Contact DataRobot support for API issues
- **Kubernetes Issues**: Check [Kubernetes documentation](https://kubernetes.io/docs/)

---

## 🎯 **Next Steps**

After successful deployment:

### **DataRobot Codespaces:**
1. **Test Services**: Use the provided URLs to access your assistant
2. **Monitor Performance**: Check service logs and metrics
3. **Scale Resources**: Adjust based on usage patterns
4. **Integrate**: Use with DataRobot workflows and pipelines

### **Local/Desktop:**
1. **Monitor Performance**: Use built-in metrics and logging
2. **Scale Resources**: Adjust based on usage patterns
3. **Add Monitoring**: Integrate with your monitoring stack
4. **Automate Updates**: Set up CI/CD for infrastructure changes

---

## 🎉 **You're Ready to Deploy!**

### **For DataRobot Codespaces (Recommended):**
```bash
./deploy/pulumi-codespaces-quickstart.sh
```

### **For Local/Desktop:**
```bash
cd deploy/pulumi
./deploy.sh
```

This gives you the **DataRobot-native approach** you're used to, with proper Infrastructure as Code, while maintaining all the other deployment options for different use cases! 🚀
