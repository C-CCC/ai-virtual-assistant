"""
AI Virtual Assistant Client
Easy-to-use Python client for interacting with the assistant
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AssistantConfig:
    """Configuration for the assistant client"""
    base_url: str = "http://localhost:8000"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class AssistantClient:
    """Client for interacting with the AI Virtual Assistant"""
    
    def __init__(self, config: Optional[AssistantConfig] = None):
        self.config = config or AssistantConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Virtual-Assistant-Client/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """Make HTTP request with retry logic"""
        url = f"{self.config.base_url}{endpoint}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    timeout=self.config.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise Exception(f"All {self.config.retry_attempts} attempts failed: {e}")
    
    def health_check(self) -> Dict:
        """Check if the assistant service is healthy"""
        return self._make_request('GET', '/health')
    
    def chat(self, message: str, context: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Send a chat message to the assistant
        
        Args:
            message: The user's message
            context: Optional context information
            **kwargs: Additional parameters (model, temperature, etc.)
        
        Returns:
            Assistant's response
        """
        data = {
            'message': message,
            'context': context or {},
            **kwargs
        }
        return self._make_request('POST', '/chat', data=data)
    
    def ask_question(self, question: str, **kwargs) -> Dict:
        """
        Ask a specific question (alias for chat)
        
        Args:
            question: The question to ask
            **kwargs: Additional parameters
        
        Returns:
            Assistant's response
        """
        return self.chat(question, **kwargs)
    
    def get_recommendations(self, query: str, limit: int = 5, **kwargs) -> Dict:
        """
        Get recommendations based on a query
        
        Args:
            query: Search query
            limit: Maximum number of recommendations
            **kwargs: Additional parameters
        
        Returns:
            List of recommendations
        """
        data = {
            'query': query,
            'limit': limit,
            **kwargs
        }
        return self._make_request('POST', '/recommendations', data=data)
    
    def analyze_document(self, document_text: str, analysis_type: str = "general", **kwargs) -> Dict:
        """
        Analyze a document
        
        Args:
            document_text: Text content to analyze
            analysis_type: Type of analysis (general, sentiment, summary, etc.)
            **kwargs: Additional parameters
        
        Returns:
            Analysis results
        """
        data = {
            'document_text': document_text,
            'analysis_type': analysis_type,
            **kwargs
        }
        return self._make_request('POST', '/analyze', data=data)
    
    def get_conversation_history(self, session_id: Optional[str] = None, limit: int = 50) -> Dict:
        """
        Get conversation history
        
        Args:
            session_id: Optional session ID
            limit: Maximum number of messages to return
        
        Returns:
            Conversation history
        """
        params = {'limit': limit}
        if session_id:
            params['session_id'] = session_id
        
        return self._make_request('GET', '/conversations', params=params)
    
    def clear_conversation(self, session_id: Optional[str] = None) -> Dict:
        """
        Clear conversation history
        
        Args:
            session_id: Optional session ID
        
        Returns:
            Confirmation message
        """
        data = {}
        if session_id:
            data['session_id'] = session_id
        
        return self._make_request('POST', '/conversations/clear', data=data)
    
    def get_available_models(self) -> Dict:
        """Get list of available AI models"""
        return self._make_request('GET', '/models')
    
    def get_system_status(self) -> Dict:
        """Get system status and metrics"""
        return self._make_request('GET', '/status')

# Convenience functions for quick usage
def quick_chat(message: str, base_url: str = "http://localhost:8000") -> str:
    """Quick chat function for simple interactions"""
    client = AssistantClient(AssistantConfig(base_url=base_url))
    try:
        response = client.chat(message)
        return response.get('response', 'No response received')
    except Exception as e:
        return f"Error: {e}"

def interactive_chat(base_url: str = "http://localhost:8000"):
    """Start an interactive chat session"""
    client = AssistantClient(AssistantConfig(base_url=base_url))
    
    print("🤖 AI Virtual Assistant - Interactive Chat")
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'help' for available commands")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\n📚 Available Commands:")
                print("  • Type any question or message to chat")
                print("  • 'status' - Check system status")
                print("  • 'models' - List available models")
                print("  • 'clear' - Clear conversation history")
                print("  • 'quit' or 'exit' - End session")
                continue
            
            if user_input.lower() == 'status':
                status = client.get_system_status()
                print(f"\n📊 System Status: {json.dumps(status, indent=2)}")
                continue
            
            if user_input.lower() == 'models':
                models = client.get_available_models()
                print(f"\n🤖 Available Models: {json.dumps(models, indent=2)}")
                continue
            
            if user_input.lower() == 'clear':
                client.clear_conversation()
                print("\n🧹 Conversation history cleared")
                continue
            
            if not user_input:
                continue
            
            # Send message to assistant
            print("\n🤔 Thinking...")
            response = client.chat(user_input)
            
            # Display response
            assistant_response = response.get('response', 'No response received')
            print(f"\n🤖 Assistant: {assistant_response}")
            
            # Show additional info if available
            if 'confidence' in response:
                print(f"   Confidence: {response['confidence']:.2f}")
            if 'model_used' in response:
                print(f"   Model: {response['model_used']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please check if the assistant service is running")

if __name__ == "__main__":
    # Example usage
    print("AI Virtual Assistant Client")
    print("=" * 30)
    
    # Check if service is running
    try:
        client = AssistantClient()
        health = client.health_check()
        print(f"✅ Service is healthy: {health}")
        
        # Start interactive chat
        interactive_chat()
        
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        print("Make sure the assistant service is running on http://localhost:8000")
