# 🤖 AI Virtual Assistant - Interaction Guide

Once your services are running, here are all the ways you can interact with your AI Virtual Assistant!

## 🚀 **Quick Start - Choose Your Method**

### **1. 🌐 Web Interface (API Gateway)**
### **2. 📱 Direct API Calls**
### **3. 🐍 Python Client**
### **4. 📚 Jupyter Notebooks**
### **5. 🔧 Command Line Interface**

---

## 🌐 **Method 1: Web Interface (API Gateway)**

### **Access the Web UI**
```bash
# If using Docker Compose
http://localhost:8000

# If using Pulumi/Kubernetes
http://your-domain.com
```

### **Available Endpoints**
- **`/`** - Main chat interface
- **`/chat`** - Chat API endpoint
- **`/health`** - Health check
- **`/status`** - System status
- **`/models`** - Available models

---

## 📱 **Method 2: Direct API Calls**

### **Using curl**
```bash
# Health check
curl http://localhost:8000/health

# Chat with the assistant
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! How are you?"}'

# Get system status
curl http://localhost:8000/status

# Get available models
curl http://localhost:8000/models
```

### **Using Python requests**
```python
import requests

# Chat with the assistant
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is machine learning?"}
)
print(response.json())
```

---

## 🐍 **Method 3: Python Client (Recommended)**

### **Install the Client**
```bash
# The client is already included in your project
# Just import it from src/common/assistant_client.py
```

### **Basic Usage**
```python
from src.common.assistant_client import AssistantClient, AssistantConfig

# Create client
config = AssistantConfig(base_url="http://localhost:8000")
client = AssistantClient(config)

# Check health
health = client.health_check()
print(f"Service healthy: {health}")

# Chat with assistant
response = client.chat("Hello! What can you help me with?")
print(f"Assistant: {response['response']}")

# Ask a question
response = client.ask_question("What is the weather like?")
print(f"Answer: {response['response']}")
```

### **Advanced Usage**
```python
# Chat with context
context = {
    "user_role": "data scientist",
    "experience_level": "intermediate",
    "project_type": "machine learning"
}

response = client.chat(
    "What are the best practices for model deployment?",
    context=context
)

# Analyze documents
analysis = client.analyze_document(
    "This is a sample document text.",
    analysis_type="summary"
)

# Get recommendations
recommendations = client.get_recommendations(
    "machine learning",
    limit=5
)
```

---

## 📚 **Method 4: Jupyter Notebooks**

### **Start Jupyter**
```bash
cd notebooks
jupyter notebook
```

### **Open the Interactive Notebook**
1. Open `interact_with_assistant.ipynb`
2. Update `BASE_URL` if needed
3. Run cells to start interacting

### **Example Notebook Usage**
```python
# In a notebook cell
from src.common.assistant_client import AssistantClient, AssistantConfig

# Initialize client
client = AssistantClient(AssistantConfig(base_url="http://localhost:8000"))

# Start chatting
response = client.chat("Hello! Tell me about yourself.")
print(response['response'])
```

---

## 🔧 **Method 5: Command Line Interface**

### **Using the CLI Tool**
```bash
# Navigate to tools directory
cd tools

# Start interactive chat
python assistant_cli.py chat

# Ask a single question
python assistant_cli.py ask "What is artificial intelligence?"

# Check service health
python assistant_cli.py health

# Get system status
python assistant_cli.py status

# Analyze a document
python assistant_cli.py analyze "This is sample text to analyze."

# Get recommendations
python assistant_cli.py recommend "data science"

# View conversation history
python assistant_cli.py history --limit 10

# Clear conversation history
python assistant_cli.py clear
```

### **CLI with Custom URL**
```bash
# Connect to different service
python assistant_cli.py --url http://your-service:8000 chat

# Custom timeout
python assistant_cli.py --timeout 60 chat
```

---

## 💬 **Interactive Chat Commands**

When using interactive chat (CLI or notebook), you have these commands:

- **`help`** - Show available commands
- **`status`** - Check system status
- **`models`** - List available models
- **`clear`** - Clear conversation history
- **`quit`** or **`exit`** - End session

---

## 🎯 **Common Use Cases**

### **1. General Questions**
```python
response = client.chat("What is the capital of France?")
```

### **2. Technical Help**
```python
response = client.chat(
    "How do I implement a binary search algorithm?",
    context={"language": "python", "difficulty": "beginner"}
)
```

### **3. Document Analysis**
```python
text = "This is a long document that needs analysis..."
analysis = client.analyze_document(text, "summary")
```

### **4. Code Review**
```python
code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""

response = client.chat(
    f"Please review this Python code and suggest improvements:\n{code}",
    context={"review_type": "code_quality"}
)
```

### **5. Learning Assistance**
```python
response = client.chat(
    "Explain machine learning concepts for a beginner",
    context={"audience": "beginner", "topic": "machine_learning"}
)
```

---

## 🔍 **Troubleshooting**

### **Service Not Responding**
```bash
# Check if service is running
curl http://localhost:8000/health

# Check Docker containers
docker ps

# Check Kubernetes pods
kubectl get pods -n ai-virtual-assistant
```

### **Connection Errors**
```python
# Test connection
try:
    client.health_check()
    print("✅ Service is accessible")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("💡 Check if service is running and URL is correct")
```

### **Authentication Issues**
```bash
# Check DataRobot configuration
echo $DATAROBOT_API_TOKEN
echo $DATAROBOT_ENDPOINT

# Verify in .env file
cat .env | grep DATAROBOT
```

---

## 📊 **Monitoring and Debugging**

### **Check Service Logs**
```bash
# Docker Compose
docker compose logs agent-services

# Kubernetes
kubectl logs -f deployment/agent-services -n ai-virtual-assistant

# Pulumi
pulumi logs --follow
```

### **Performance Monitoring**
```python
# Get system metrics
status = client.get_system_status()
print(f"Response time: {status.get('response_time', 'N/A')}")
print(f"Active connections: {status.get('active_connections', 'N/A')}")
```

---

## 🚀 **Production Usage**

### **Load Balancing**
```python
# Multiple service instances
urls = [
    "http://service1:8000",
    "http://service2:8000",
    "http://service3:8000"
]

# Round-robin load balancing
import random
url = random.choice(urls)
client = AssistantClient(AssistantConfig(base_url=url))
```

### **Error Handling**
```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# Use with client methods
@retry_on_failure(max_attempts=3, delay=2)
def reliable_chat(client, message):
    return client.chat(message)
```

---

## 🎉 **You're Ready to Chat!**

### **Quick Test**
```python
# Test your setup
from src.common.assistant_client import quick_chat

response = quick_chat("Hello! Are you working?")
print(response)
```

### **Next Steps**
1. **Explore**: Try different types of questions
2. **Customize**: Modify the client for your needs
3. **Scale**: Deploy to production with Pulumi
4. **Integrate**: Use in your applications

### **Need Help?**
- Check the troubleshooting section above
- Review service logs for errors
- Verify DataRobot configuration
- Use the health check endpoints

Happy chatting with your AI Virtual Assistant! 🤖✨
