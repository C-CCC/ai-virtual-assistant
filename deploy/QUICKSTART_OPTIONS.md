# 🚀 Quick Start Options for DataRobot Codespaces

This guide explains the different quickstart options available for deploying your AI Virtual Assistant in DataRobot Codespaces.

## 📋 **Available Quick Start Options**

### **1. 🐍 Python-Only Quick Start (Recommended for Codespaces)**
**File**: `deploy/codespaces-python-quickstart.sh`

**What it does**:
- ✅ Runs services directly in Python (no Docker required)
- ✅ Installs Python dependencies automatically
- ✅ Creates service management scripts
- ✅ Perfect for development and testing
- ✅ No external dependencies like `jq`

**Requirements**:
- Python 3.8+
- pip3
- DataRobot API credentials

**Usage**:
```bash
./deploy/codespaces-python-quickstart.sh
```

---

### **2. 🐳 Docker Compose Quick Start**
**File**: `deploy/codespaces-quickstart.sh`

**What it does**:
- ✅ Runs services in Docker containers
- ✅ Full container orchestration
- ✅ Production-like environment
- ✅ Requires Docker and `jq`

**Requirements**:
- Docker and Docker Compose
- `jq` (JSON processor)
- DataRobot API credentials

**Usage**:
```bash
./deploy/codespaces-quickstart.sh
```

---

### **3. 🏗️ Pulumi Infrastructure as Code (Advanced)**
**File**: `deploy/pulumi-codespaces-quickstart.sh`

**What it does**:
- ✅ Deploys infrastructure using Pulumi
- ✅ Kubernetes-native deployment
- ✅ Infrastructure versioning and state management
- ✅ Professional-grade deployment

**Requirements**:
- kubectl access
- DataRobot API credentials
- Python 3.8+

**Usage**:
```bash
./deploy/pulumi-codespaces-quickstart.sh
```

---

## 🎯 **Which Option Should You Choose?**

### **🚀 For Quick Development & Testing**
```bash
./deploy/codespaces-python-quickstart.sh
```
- **Best for**: Getting started quickly, development, testing
- **Pros**: Fast, simple, no Docker dependencies
- **Cons**: Less production-like

### **🐳 For Production-Like Environment**
```bash
./deploy/codespaces-quickstart.sh
```
- **Best for**: Testing production-like setup, Docker workflows
- **Pros**: Production-like environment, container isolation
- **Cons**: Requires Docker and `jq`

### **🏗️ For Professional Deployment**
```bash
./deploy/pulumi-codespaces-quickstart.sh
```
- **Best for**: Production deployment, infrastructure management
- **Pros**: Professional-grade, version controlled, scalable
- **Cons**: More complex, requires kubectl access

---

## 🔧 **Troubleshooting Common Issues**

### **Issue: "jq not found" Error**
**Cause**: You're running the Docker-based script without `jq` installed.

**Solutions**:
1. **Install jq manually**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install jq
   
   # CentOS/RHEL
   sudo yum install jq
   
   # macOS
   brew install jq
   
   # Alpine
   sudo apk add jq
   ```

2. **Use Python-only quickstart instead**:
   ```bash
   ./deploy/codespaces-python-quickstart.sh
   ```

### **Issue: "Docker command not found"**
**Cause**: Docker is not available in your Codespace.

**Solution**: Use the Python-only quickstart:
```bash
./deploy/codespaces-python-quickstart.sh
```

### **Issue: "kubectl not accessible"**
**Cause**: Kubernetes cluster access is limited.

**Solution**: Use Python-only or Docker Compose quickstart:
```bash
# Option 1: Python-only
./deploy/codespaces-python-quickstart.sh

# Option 2: Docker Compose
./deploy/codespaces-quickstart.sh
```

---

## 📚 **Quick Start Comparison**

| Feature | Python-Only | Docker Compose | Pulumi |
|---------|-------------|----------------|---------|
| **Speed** | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡ Slow |
| **Complexity** | 🟢 Simple | 🟡 Medium | 🔴 Complex |
| **Production-like** | 🟡 Basic | 🟢 Good | 🟢 Excellent |
| **Dependencies** | 🟢 Minimal | 🟡 Docker + jq | 🟡 kubectl |
| **Scalability** | 🟡 Limited | 🟢 Good | 🟢 Excellent |
| **State Management** | ❌ None | ❌ None | ✅ Full |

---

## 🎉 **Recommendation**

### **For Most Users in DataRobot Codespaces:**
```bash
./deploy/codespaces-python-quickstart.sh
```

**Why this is recommended**:
- ✅ **Fastest setup** - Get running in minutes
- ✅ **No dependencies** - Works in any Codespace
- ✅ **Simple management** - Easy to start/stop services
- ✅ **Perfect for development** - Ideal for testing and iteration

### **For Advanced Users:**
```bash
./deploy/pulumi-codespaces-quickstart.sh
```

**When to use this**:
- 🎯 You need infrastructure versioning
- 🎯 You're deploying to production
- 🎯 You want professional-grade deployment
- 🎯 You have kubectl access

---

## 🚀 **Get Started Now!**

1. **Choose your quickstart option** from above
2. **Run the script** with your DataRobot credentials
3. **Follow the prompts** to configure everything
4. **Start using your AI Virtual Assistant!**

Need help? Check the main documentation or run the Python-only quickstart for the simplest experience! 🎯
