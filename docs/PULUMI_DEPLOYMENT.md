# Pulumi Deployment Guide for AI Virtual Assistant

This guide explains how to deploy the AI Virtual Assistant using Pulumi for Infrastructure as Code (IaC) deployment.

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

## 📋 **Prerequisites**

1. **Pulumi CLI**: Install from [pulumi.com](https://www.pulumi.com/docs/get-started/install/)
2. **Kubernetes Cluster**: Accessible via kubectl
3. **DataRobot Account**: With API access and deployments
4. **Python 3.8+**: For Pulumi Python runtime

## 🔧 **Installation**

### **1. Install Pulumi CLI**
```bash
# macOS
brew install pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows
winget install Pulumi.Pulumi
```

### **2. Verify Installation**
```bash
pulumi version
pulumi plugin ls
```

## 🏗️ **Project Structure**

```
deploy/pulumi/
├── Pulumi.yaml              # Project configuration
├── __main__.py              # Main infrastructure code
├── Pulumi.prod.yaml         # Production configuration
├── requirements.txt          # Python dependencies
└── deploy.sh                # Deployment script
```

## 🚀 **Quick Start**

### **Option 1: Automated Deployment (Recommended)**
```bash
cd deploy/pulumi
./deploy.sh
```

### **Option 2: Manual Deployment**
```bash
cd deploy/pulumi

# Install dependencies
pip install -r requirements.txt

# Initialize project
pulumi stack init dev

# Configure DataRobot settings
pulumi config set datarobot:api_token "your_token"
pulumi config set datarobot:endpoint "https://app.datarobot.com"
pulumi config set datarobot:deployments:llm:id "your_llm_id"
pulumi config set datarobot:deployments:embedding/id "your_embedding_id"
pulumi config set datarobot:deployments:rerank/id "your_rerank_id"

# Deploy
pulumi up --yes
```

## ⚙️ **Configuration**

### **DataRobot Configuration**
```yaml
# Pulumi.prod.yaml
config:
  ai-virtual-assistant-datarobot:datarobot:
    api_token: "your_datarobot_api_token"
    endpoint: "https://app.datarobot.com"
    deployments:
      llm:
        id: "your_llm_deployment_id"
        model_name: "your_llm_model_name"
      embedding:
        id: "your_embedding_deployment_id"
        model_name: "your_embedding_model_name"
      rerank:
        id: "your_rerank_deployment_id"
        model_name: "your_rerank_model_name"
```

### **Environment-Specific Configs**
```bash
# Development
pulumi stack init dev
pulumi config set datarobot:endpoint "https://dev.datarobot.com"

# Staging
pulumi stack init staging
pulumi config set datarobot:endpoint "https://staging.datarobot.com"

# Production
pulumi stack init prod
pulumi config set datarobot:endpoint "https://app.datarobot.com"
```

## 🏗️ **Infrastructure Components**

### **1. Namespace**
- Isolated Kubernetes namespace for the application
- Resource quotas and limits
- Network policies

### **2. DataRobot Secrets**
- Secure storage of API tokens
- Deployment IDs
- Encrypted at rest

### **3. Database Layer**
- PostgreSQL with persistent storage
- Redis for caching
- Automatic password generation

### **4. Vector Database**
- Milvus for embeddings
- Persistent storage
- Optimized for AI workloads

### **5. Application Services**
- Agent services (scalable)
- Analytics services
- Retriever services
- Health checks and monitoring

### **6. Networking**
- Ingress with TLS termination
- Load balancing
- Service mesh ready

### **7. Autoscaling**
- Horizontal Pod Autoscaler
- CPU-based scaling
- Configurable min/max replicas

## 🔄 **Deployment Workflow**

### **1. Preview Changes**
```bash
pulumi preview
```

### **2. Deploy Infrastructure**
```bash
pulumi up --yes
```

### **3. Monitor Deployment**
```bash
kubectl get all -n ai-virtual-assistant
kubectl logs -f deployment/agent-services -n ai-virtual-assistant
```

### **4. Update Configuration**
```bash
pulumi config set datarobot:api_token "new_token"
pulumi up --yes
```

### **5. Destroy Infrastructure**
```bash
pulumi destroy --yes
```

## 📊 **Monitoring and Management**

### **Check Deployment Status**
```bash
# Pulumi stack status
pulumi stack

# Kubernetes resources
kubectl get all -n ai-virtual-assistant

# Service endpoints
kubectl get endpoints -n ai-virtual-assistant
```

### **View Logs**
```bash
# Application logs
kubectl logs -f deployment/agent-services -n ai-virtual-assistant

# Infrastructure logs
pulumi logs --follow
```

### **Scale Services**
```bash
# Manual scaling
kubectl scale deployment agent-services --replicas=5 -n ai-virtual-assistant

# Or update Pulumi config
pulumi config set agent:min_replicas 5
pulumi up --yes
```

## 🔒 **Security Features**

### **1. Secrets Management**
- Kubernetes secrets for sensitive data
- No hardcoded credentials
- Encrypted storage

### **2. Network Policies**
- Pod-to-pod communication control
- Ingress/egress rules
- Service mesh integration ready

### **3. RBAC**
- Service account permissions
- Role-based access control
- Least privilege principle

## 🚀 **Advanced Features**

### **1. Multi-Environment Deployment**
```bash
# Deploy to multiple environments
for env in dev staging prod; do
    pulumi stack select $env
    pulumi up --yes
done
```

### **2. CI/CD Integration**
```yaml
# GitHub Actions example
- name: Deploy with Pulumi
  run: |
    cd deploy/pulumi
    pulumi stack select ${{ github.ref_name }}
    pulumi up --yes
```

### **3. Custom Resource Definitions**
```python
# Add custom monitoring
monitoring = k8s.apiextensions.v1.CustomResourceDefinition(
    "ai-monitoring",
    spec=k8s.apiextensions.v1.CustomResourceDefinitionSpecArgs(
        # ... monitoring configuration
    )
)
```

## 🔧 **Troubleshooting**

### **Common Issues**

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

3. **Python Dependencies Missing**
   ```bash
   # Install requirements
   pip install -r requirements.txt
   ```

4. **Configuration Errors**
   ```bash
   # View current config
   pulumi config
   
   # Set missing values
   pulumi config set datarobot:api_token "your_token"
   ```

### **Debug Mode**
```bash
# Enable debug logging
export PULUMI_DEBUG=1
pulumi up --yes
```

## 📚 **Additional Resources**

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi Kubernetes Provider](https://www.pulumi.com/registry/packages/kubernetes/)
- [Pulumi Python Examples](https://github.com/pulumi/examples)
- [DataRobot API Documentation](https://docs.datarobot.com/en/docs/api/)

## 🆘 **Getting Help**

- **Pulumi Community**: [Community Slack](https://slack.pulumi.com/)
- **DataRobot Support**: Contact DataRobot support for API issues
- **Kubernetes Issues**: Check [Kubernetes documentation](https://kubernetes.io/docs/)

## 🎯 **Next Steps**

After successful deployment:
1. **Monitor Performance** - Use built-in metrics and logging
2. **Scale Resources** - Adjust based on usage patterns
3. **Add Monitoring** - Integrate with DataRobot monitoring
4. **Automate Updates** - Set up CI/CD for infrastructure changes
5. **Backup Strategy** - Implement data backup and recovery
