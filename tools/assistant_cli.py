#!/usr/bin/env python3
"""
AI Virtual Assistant CLI Tool
Command-line interface for interacting with the assistant
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.assistant_client import AssistantClient, AssistantConfig, interactive_chat

def main():
    parser = argparse.ArgumentParser(
        description="AI Virtual Assistant CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive chat
  python assistant_cli.py chat
  
  # Ask a single question
  python assistant_cli.py ask "What is the weather like?"
  
  # Check service health
  python assistant_cli.py health
  
  # Get system status
  python assistant_cli.py status
  
  # Analyze a document
  python assistant_cli.py analyze "This is a sample document text."
  
  # Get recommendations
  python assistant_cli.py recommend "machine learning"
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        default='http://localhost:8000',
        help='Assistant service URL (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check command
    subparsers.add_parser('health', help='Check service health')
    
    # Status command
    subparsers.add_parser('status', help='Get system status')
    
    # Models command
    subparsers.add_parser('models', help='List available models')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Start interactive chat')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a single question')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--context', '-c', help='Additional context')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a document')
    analyze_parser.add_argument('text', help='Text to analyze')
    analyze_parser.add_argument('--type', '-t', default='general', help='Analysis type')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Get recommendations')
    recommend_parser.add_argument('query', help='Search query')
    recommend_parser.add_argument('--limit', '-l', type=int, default=5, help='Number of recommendations')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Get conversation history')
    history_parser.add_argument('--limit', '-l', type=int, default=50, help='Number of messages')
    history_parser.add_argument('--session', '-s', help='Session ID')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear conversation history')
    clear_parser.add_argument('--session', '-s', help='Session ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create client
    config = AssistantConfig(base_url=args.url, timeout=args.timeout)
    client = AssistantClient(config)
    
    try:
        if args.command == 'health':
            result = client.health_check()
            print("✅ Service Health:")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'status':
            result = client.get_system_status()
            print("📊 System Status:")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'models':
            result = client.get_available_models()
            print("🤖 Available Models:")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'chat':
            print("🤖 Starting interactive chat...")
            interactive_chat(args.url)
            
        elif args.command == 'ask':
            context = {}
            if args.context:
                try:
                    context = json.loads(args.context)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON context: {args.context}")
                    return 1
            
            print(f"👤 Question: {args.question}")
            if context:
                print(f"📝 Context: {json.dumps(context, indent=2)}")
            
            print("\n🤔 Thinking...")
            result = client.ask_question(args.question, context=context)
            
            print(f"\n🤖 Assistant: {result.get('response', 'No response received')}")
            if 'confidence' in result:
                print(f"   Confidence: {result['confidence']:.2f}")
            if 'model_used' in result:
                print(f"   Model: {result['model_used']}")
                
        elif args.command == 'analyze':
            print(f"📄 Analyzing text: {args.text[:100]}{'...' if len(args.text) > 100 else ''}")
            print(f"🔍 Analysis type: {args.type}")
            
            result = client.analyze_document(args.text, args.type)
            print(f"\n📊 Analysis Results:")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'recommend':
            print(f"🔍 Getting recommendations for: {args.query}")
            print(f"📊 Limit: {args.limit}")
            
            result = client.get_recommendations(args.query, args.limit)
            print(f"\n💡 Recommendations:")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'history':
            print(f"📚 Getting conversation history...")
            if args.session:
                print(f"   Session ID: {args.session}")
            print(f"   Limit: {args.limit}")
            
            result = client.get_conversation_history(args.session, args.limit)
            print(f"\n💬 Conversation History:")
            print(json.dumps(result, indent=2))
            
        elif args.command == 'clear':
            if args.session:
                print(f"🧹 Clearing conversation history for session: {args.session}")
            else:
                print("🧹 Clearing all conversation history...")
            
            result = client.clear_conversation(args.session)
            print(f"✅ {result.get('message', 'History cleared')}")
            
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Make sure the assistant service is running at {args.url}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
