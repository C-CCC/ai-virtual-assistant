#!/bin/bash

# Startup script for DataRobot Codespaces
# This script starts all services in the background

echo "🚀 Starting AI Virtual Assistant services..."

# Load environment variables
source .env

# Set Python path correctly - add the src directory to Python path
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

echo "Python path set to: $PYTHONPATH"

# Store the project root directory
PROJECT_ROOT="$(pwd)"
echo "Project root: $PROJECT_ROOT"

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local service_file=$3
    local port=$4
    
    echo "Starting $service_name on port $port..."
    
    # Always work from project root
    cd "$PROJECT_ROOT"
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start the service from the project root with correct Python path
    nohup python3 -m "$service_dir.$service_file" > "logs/${service_name}.log" 2>&1 &
    local pid=$!
    echo $pid > "logs/${service_name}.pid"
    
    echo "✅ $service_name started (PID: $pid)"
    
    # Wait a moment for the service to start
    sleep 5
    
    # Check if the service is actually running
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $service_name is running (PID: $pid)"
        
        # Check if the port is actually listening
        if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
            echo "✅ $service_name is listening on port $port"
        else
            echo "⚠️  $service_name is running but not listening on port $port yet"
        fi
    else
        echo "❌ $service_name failed to start"
        echo "Check logs/${service_name}.log for errors"
    fi
}

# Create logs directory
mkdir -p logs

# Stop any existing services first
echo "Stopping any existing services..."
./stop-services.sh 2>/dev/null || true

# Start services with proper module paths - use server.py files
start_service "agent-services" "agent" "server" "8000"
start_service "analytics-services" "analytics" "server" "8001"
start_service "retriever-canonical" "retrievers" "server" "8003"
start_service "retriever-structured" "retrievers" "server" "8004"

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
echo ""
echo "Waiting for services to be ready..."
echo "You can test with: curl http://localhost:8000/health"
