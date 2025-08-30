# DataRobot Codespaces Guide

This guide explains how to use DataRobot Codespaces to build, develop, and deploy the AI Virtual Assistant.

## 🚀 **What is DataRobot Codespaces?**

DataRobot Codespaces provides a cloud-based development environment that includes:
- **Pre-configured development containers** with all necessary tools
- **Integrated DataRobot services** and authentication
- **Collaborative development** capabilities
- **Built-in CI/CD** pipelines
- **Managed infrastructure** for development and testing

## 📋 **Prerequisites**

1. **DataRobot Account**: Active DataRobot account with Codespaces access
2. **DataRobot Deployments**: Three deployments created in DataRobot:
   - LLM deployment for text generation
   - Embedding deployment for vector embeddings
   - Rerank deployment for document reranking
3. **API Token**: DataRobot API token for authentication

## 🔧 **Setting Up DataRobot Codespaces**

### **1. Access Codespaces**

1. Log into your DataRobot account
2. Navigate to the Codespaces section
3. Create a new Codespace or open an existing one

### **2. Clone the Repository**

```bash
# In your Codespace terminal
git clone https://github.com/your-username/ai-virtual-assistant.git
cd ai-virtual-assistant
```

### **3. Configure DataRobot Integration**

The Codespace environment automatically detects DataRobot services and provides:
- **Integrated authentication** with your DataRobot account
- **Direct access** to DataRobot deployments
- **Pre-configured** environment variables

## 🐳 **Deployment Options in Codespaces**

### **Option 1: Quick Start (Recommended)**

Use the automated setup script:

```bash
# Run the Codespaces quick start script
./deploy/codespaces-quickstart.sh
```

This script will:
- ✅ Check Codespaces environment
- ✅ Prompt for DataRobot configuration
- ✅ Create environment files
- ✅ Test DataRobot connectivity
- ✅ Build and deploy all services
- ✅ Wait for services to be healthy
- ✅ Provide service URLs and next steps

### **Option 2: Manual Docker Compose**

```bash
# Create environment file
cp deploy/datarobot-config.yaml .env
# Edit .env with your DataRobot values

# Deploy with Codespaces-optimized compose file
docker compose -f deploy/compose/docker-compose-codespaces.yaml \
  --env-file .env up -d
```

### **Option 3: Direct Python Development**

```bash
# Install dependencies
pip install -r src/agent/requirements.txt
pip install -r src/analytics/requirements.txt
pip install -r src/retrievers/unstructured_data/requirements.txt
pip install -r src/retrievers/structured_data/requirements.txt

# Set environment variables
export APP_LLM_MODELENGINE=datarobot
export DATAROBOT_API_TOKEN=your_token
export DATAROBOT_ENDPOINT=https://app.datarobot.com
export DATAROBOT_LLM_DEPLOYMENT_ID=your_llm_id
export DATAROBOT_EMBEDDING_DEPLOYMENT_ID=your_embedding_id
export DATAROBOT_RERANK_DEPLOYMENT_ID=your_rerank_id

# Run services directly
cd src/agent && python main.py &
cd src/analytics && python main.py &
cd src/retrievers && python server.py &
```

## 🌐 **Accessing Services in Codespaces**

### **Port Forwarding**

Codespaces automatically forwards these ports:
- **8000**: Agent Services
- **8001**: Analytics Services  
- **8002**: API Gateway
- **8003**: Retriever Canonical
- **8004**: Retriever Structured

### **Service URLs**

Once deployed, access services at:
- **Agent Services**: `http://localhost:8000`
- **Analytics Services**: `http://localhost:8001`
- **API Gateway**: `http://localhost:8002`
- **Retriever Canonical**: `http://localhost:8003`
- **Retriever Structured**: `http://localhost:8004`

### **API Documentation**

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔍 **Development Workflow in Codespaces**

### **1. Code Changes**

```bash
# Make changes to your code
vim src/agent/server.py

# Test changes
docker compose -f deploy/compose/docker-compose-codespaces.yaml restart agent-services
```

### **2. Testing**

```bash
# Run tests
python -m pytest tests/

# Check service health
curl http://localhost:8000/health
```

### **3. Debugging**

```bash
# View logs
docker compose -f deploy/compose/docker-compose-codespaces.yaml logs -f

# Debug specific service
docker compose -f deploy/compose/docker-compose-codespaces.yaml logs agent-services
```

## 🚀 **Advanced Codespaces Features**

### **1. Multi-Service Development**

```bash
# Start only specific services
docker compose -f deploy/compose/docker-compose-codespaces.yaml up -d agent-services analytics-services

# Scale services
docker compose -f deploy/compose/docker-compose-codespaces.yaml up -d --scale agent-services=3
```

### **2. Data Management**

```bash
# Access data directory
ls -la data/

# Import new data
cp new_data.csv data/
docker compose -f deploy/compose/docker-compose-codespaces.yaml restart retriever-structured
```

### **3. Model Updates**

```bash
# Update DataRobot deployment IDs
export DATAROBOT_LLM_DEPLOYMENT_ID=new_deployment_id

# Restart services to pick up new configuration
docker compose -f deploy/compose/docker-compose-codespaces.yaml restart
```

## 📊 **Monitoring and Logging**

### **Service Health**

```bash
# Check all service statuses
docker compose -f deploy/compose/docker-compose-codespaces.yaml ps

# Monitor service health
watch -n 5 'docker compose -f deploy/compose/docker-compose-codespaces.yaml ps'
```

### **Logs and Debugging**

```bash
# Follow all logs
docker compose -f deploy/compose/docker-compose-codespaces.yaml logs -f

# Filter logs by service
docker compose -f deploy/compose/docker-compose-codespaces.yaml logs -f agent-services

# Search logs
docker compose -f deploy/compose/docker-compose-codespaces.yaml logs | grep "ERROR"
```

## 🔧 **Troubleshooting in Codespaces**

### **Common Issues**

1. **Port Conflicts**
   ```bash
   # Check what's using a port
   lsof -i :8000
   
   # Kill process using port
   kill -9 $(lsof -t -i:8000)
   ```

2. **Service Not Starting**
   ```bash
   # Check service logs
   docker compose -f deploy/compose/docker-compose-codespaces.yaml logs service-name
   
   # Check service health
   docker compose -f deploy/compose/docker-compose-codespaces.yaml ps
   ```

3. **DataRobot Connection Issues**
   ```bash
   # Test API token
   curl -H "Authorization: Token $DATAROBOT_API_TOKEN" \
     "$DATAROBOT_ENDPOINT/api/v2/users/me/"
   
   # Verify deployment IDs
   curl -H "Authorization: Token $DATAROBOT_API_TOKEN" \
     "$DATAROBOT_ENDPOINT/api/v2/deployments/$DATAROBOT_LLM_DEPLOYMENT_ID/"
   ```

### **Reset Environment**

```bash
# Stop all services
docker compose -f deploy/compose/docker-compose-codespaces.yaml down

# Remove volumes (WARNING: This will delete all data)
docker compose -f deploy/compose/docker-compose-codespaces.yaml down -v

# Rebuild and restart
./deploy/codespaces-quickstart.sh
```

## 🚀 **Next Steps**

### **1. Customize the System**
- Modify prompts in `prompt.yaml` files
- Add new data sources to the `data/` directory
- Customize service configurations

### **2. Integrate with DataRobot Pipeline**
- Connect to DataRobot model registry
- Set up automated model updates
- Implement monitoring and alerting

### **3. Scale and Deploy**
- Use DataRobot's managed services for production
- Set up CI/CD pipelines
- Implement monitoring and logging

## 📚 **Additional Resources**

- [DataRobot API Documentation](https://docs.datarobot.com/en/docs/api/)
- [DataRobot Codespaces Documentation](https://docs.datarobot.com/en/docs/codespaces/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [AI Virtual Assistant Architecture](docs/ARCHITECTURE.md)

## 🆘 **Getting Help**

- **DataRobot Support**: Contact DataRobot support for Codespaces issues
- **Code Issues**: Check service logs and health checks
- **Configuration**: Verify environment variables and DataRobot settings
- **Community**: Join DataRobot community forums for help
