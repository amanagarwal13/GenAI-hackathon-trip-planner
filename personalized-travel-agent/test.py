#!/usr/bin/env python3
"""
Vertex AI Reasoning Engine Agent Chat Interface

This script provides an interactive chat interface for communicating with
a deployed Google Vertex AI Reasoning Engine agent.

Requirements:
    - google-cloud-aiplatform
    - google-adk
    - python-dotenv
    - vertexai

Usage:
    python vertex_ai_agent_chat.py
"""

import os
import asyncio
import sys
from typing import Optional
from dotenv import load_dotenv

try:
    from google.adk.sessions import VertexAiSessionService
    import vertexai
    from vertexai import agent_engines
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("\nPlease install required packages:")
    print("pip install google-cloud-aiplatform google-adk vertexai python-dotenv")
    sys.exit(1)


class VertexAIAgentChat:
    """Manages chat interactions with a Vertex AI Reasoning Engine agent."""
    
    def __init__(self, env_path: str = 'personalized-travel-agent/.env'):
        """
        Initialize the chat client with configuration from environment variables.
        
        Args:
            env_path: Path to the .env file containing configuration
        """
        # Load environment variables
        load_dotenv(env_path)
        
        # Configuration
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION")
        self.agent_resource_id = os.getenv(
            "AGENT_RESOURCE_ID", 
            "projects/56426154949/locations/us-central1/reasoningEngines/8671984547711156224"
        )
        self.user_id = os.getenv("USER_ID", "test-user-123")
        
        # Validate configuration
        self._validate_config()
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize agent and session service
        self.remote_agent = None
        self.session_service = None
        self.session = None
        
    def _validate_config(self):
        """Validate that all required configuration is present."""
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT not found in environment variables")
        if not self.location:
            raise ValueError("GOOGLE_CLOUD_LOCATION not found in environment variables")
        
        print("Configuration loaded successfully:")
        print(f"  PROJECT_ID: {self.project_id}")
        print(f"  LOCATION: {self.location}")
        print(f"  AGENT_RESOURCE_ID: {self.agent_resource_id}")
        print(f"  USER_ID: {self.user_id}")
        print("-" * 50)
    
    async def initialize(self):
        """Initialize the agent and create a chat session."""
        try:
            # Get reference to the deployed agent
            print("Connecting to agent...")
            self.remote_agent = agent_engines.get(self.agent_resource_id)
            print(f"✓ Connected to agent: {self.remote_agent.display_name}")
            
            # Create session service
            self.session_service = VertexAiSessionService(
                self.project_id, 
                self.location
            )
            
            # Create new chat session
            print("Creating chat session...")
            self.session = await self.session_service.create_session(
                app_name=self.agent_resource_id,
                user_id=self.user_id
            )
            print(f"✓ Session created: {self.session.id}")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            raise
    
    def process_stream_event(self, event) -> Optional[str]:
        """
        Process a single streaming event from the agent.
        
        Args:
            event: The streaming event from the agent
            
        Returns:
            Text content if present, None otherwise
        """
        # Handle text content
        if 'content' in event and 'parts' in event['content']:
            parts = event['content'].get('parts', [])
            if parts and isinstance(parts, list):
                text = parts[0].get('text', '')
                if text:
                    return text
        
        # Handle tool calls
        if 'actions' in event and 'tool_code' in event['actions']:
            tool_name = event['actions']['tool_code'].get('name', 'Unknown')
            tool_input = event['actions']['tool_code'].get('input', {})
            return f"\n[🔧 Calling tool: {tool_name}({tool_input})]"
        
        return None
    
    async def send_message(self, message: str) -> str:
        """
        Send a message to the agent and collect the response.
        
        Args:
            message: The user's message
            
        Returns:
            The agent's complete response
        """
        full_response = []
        
        try:
            # Stream the query and collect events
            for event in self.remote_agent.stream_query(
                user_id=self.user_id,
                session_id=self.session.id,
                message=message,
            ):
                text = self.process_stream_event(event)
                if text:
                    print(text, end="", flush=True)
                    full_response.append(text)
            
            print()  # New line after response
            return "".join(full_response)
            
        except Exception as e:
            error_msg = f"\n❌ Error during message processing: {e}"
            print(error_msg)
            return error_msg
    
    async def chat_loop(self):
        """Run the interactive chat loop."""
        print("\n🤖 Chat session started!")
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'clear' to clear the screen")
        print("Type 'info' to see session information")
        print("-" * 50)
        
        while True:
            try:
                # Get user input
                message = input("\n👤 You: ").strip()
                
                # Handle special commands
                if message.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Ending chat session...")
                    break
                
                if message.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                if message.lower() == 'info':
                    print(f"\nSession Information:")
                    print(f"  Session ID: {self.session.id}")
                    print(f"  User ID: {self.user_id}")
                    print(f"  Agent: {self.remote_agent.display_name}")
                    continue
                
                if not message:
                    continue
                
                # Send message and get response
                print("\n🤖 Agent: ", end="")
                await self.send_message(message)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("You can continue chatting or type 'quit' to exit.")
    
    async def run(self):
        """Main entry point to run the chat application."""
        try:
            await self.initialize()
            await self.chat_loop()
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            sys.exit(1)
        finally:
            print("\n✓ Session closed")


async def main():
    """Main function to run the chat application."""
    # You can customize the env file path here
    env_path = 'personalized-travel-agent/.env'
    
    # Check if custom env path is provided as command line argument
    if len(sys.argv) > 1:
        env_path = sys.argv[1]
    
    # Create and run the chat client
    chat_client = VertexAIAgentChat(env_path=env_path)
    await chat_client.run()


if __name__ == "__main__":
    # Print welcome banner
    print("=" * 50)
    print("  Vertex AI Reasoning Engine Chat Interface")
    print("=" * 50)
    
    try:
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Application terminated by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        sys.exit(1)