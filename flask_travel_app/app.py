# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A monolithic Flask web application for the Personalized Travel Agent, using the Vertex AI SDK."""

import os
import asyncio
import json
from flask import Flask, render_template, request, Response, jsonify, stream_with_context
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from google.adk.sessions import VertexAiSessionService

# --- Agent Singleton Class ---
class AgentSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Initializing Agent Singleton...")
            cls._instance = super(AgentSingleton, cls).__new__(cls)
            try:
                # Load configuration - try multiple paths for .env file
                possible_env_paths = [
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'personalized-travel-agent', '.env'),
                    os.path.join(os.path.dirname(__file__), '.env'),
                    '.env'
                ]
                
                env_loaded = False
                for env_path in possible_env_paths:
                    if os.path.exists(env_path):
                        load_dotenv(dotenv_path=env_path)
                        env_loaded = True
                        print(f"✓ Loaded environment from: {env_path}")
                        break
                
                if not env_loaded:
                    print("⚠️ No .env file found, using system environment variables")
                
                # Get environment variables with fallbacks
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or "56426154949"
                location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GCP_LOCATION") or "us-central1"
                
                # Travel planner agent
                travel_agent_resource_id = os.getenv("AGENT_RESOURCE_ID") or "projects/56426154949/locations/us-central1/reasoningEngines/14940163998220288"
                
                # Smart packing agent
                packing_agent_resource_id = os.getenv("PACKING_AGENT_RESOURCE_ID") or "projects/56426154949/locations/us-central1/reasoningEngines/7744243024472834048"

                print(f"🔧 Configuration:")
                print(f"   Project ID: {project_id}")
                print(f"   Location: {location}")
                print(f"   Travel Agent Resource ID: {travel_agent_resource_id}")
                print(f"   Packing Agent Resource ID: {packing_agent_resource_id}")

                if not all([project_id, location, travel_agent_resource_id, packing_agent_resource_id]):
                    missing_vars = []
                    if not project_id: missing_vars.append("GOOGLE_CLOUD_PROJECT")
                    if not location: missing_vars.append("GOOGLE_CLOUD_LOCATION") 
                    if not travel_agent_resource_id: missing_vars.append("AGENT_RESOURCE_ID")
                    if not packing_agent_resource_id: missing_vars.append("PACKING_AGENT_RESOURCE_ID")
                    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

                # Initialize Vertex AI and connect to the agents
                vertexai.init(project=project_id, location=location)
                cls._instance.travel_agent = agent_engines.get(travel_agent_resource_id)
                cls._instance.packing_agent = agent_engines.get(packing_agent_resource_id)
                
                # For backward compatibility, keep remote_agent pointing to travel agent
                cls._instance.remote_agent = cls._instance.travel_agent
                
                # Correctly initialize the session service with positional arguments
                cls._instance.session_service = VertexAiSessionService(project_id, location)
                print(f"✓ Successfully connected to travel agent: {cls._instance.travel_agent.display_name}")
                print(f"✓ Successfully connected to packing agent: {cls._instance.packing_agent.display_name}")

            except Exception as e:
                print(f"❌ FATAL ERROR: Could not initialize agents. {e}")
                cls._instance.travel_agent = None
                cls._instance.packing_agent = None
                cls._instance.remote_agent = None
                cls._instance.session_service = None
        return cls._instance

# --- INITIALIZATION ---
app = Flask(__name__)
agent_connection = AgentSingleton() # Initialize the agent connection when the app starts

# --- PAGE ROUTING ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/planner')
def planner():
    return render_template('planner.html')

@app.route('/packing')
def packing():
    return render_template('packing.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

# --- API ENDPOINTS ---
@app.route('/api/sessions', methods=['POST'])
def create_session():
    print("🔄 Session creation request received")
    
    # Get agent type from request body (default to travel)
    data = request.get_json() or {}
    agent_type = data.get('agent_type', 'travel')
    
    # Select the appropriate agent
    if agent_type == 'packing':
        selected_agent = agent_connection.packing_agent
        agent_name = "packing agent"
    else:
        selected_agent = agent_connection.travel_agent
        agent_name = "travel agent"
    
    if not selected_agent:
        error_msg = f"{agent_name} not initialized"
        print(f"❌ {error_msg}")
        return jsonify({"error": error_msg}), 500
        
    if not agent_connection.session_service:
        error_msg = "Session service not initialized"
        print(f"❌ {error_msg}")
        return jsonify({"error": error_msg}), 500
    
    user_id = "flask-webapp-stable"
    try:
        print(f"🔧 Creating session with:")
        print(f"   App name: {selected_agent.resource_name}")
        print(f"   User ID: {user_id}")
        print(f"   Agent type: {agent_type}")
        
        # Use the initialized session service
        session = asyncio.run(agent_connection.session_service.create_session(
            app_name=selected_agent.resource_name,
            user_id=user_id
        ))
        print(f"✅ Created new session: {session.id}")
        return jsonify({"id": session.id, "agent_type": agent_type}), 201
    except Exception as e:
        error_msg = f"Failed to create session: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/sessions/<session_id>/stream', methods=['POST'])
def stream_chat(session_id: str):
    data = request.get_json()
    message = data.get('content')
    agent_type = data.get('agent_type', 'travel')
    user_id = "flask-webapp-stable"

    if not message:
        return jsonify({"error": "Missing 'content' in request body."}), 400

    # Select the appropriate agent
    if agent_type == 'packing':
        selected_agent = agent_connection.packing_agent
        agent_name = "packing agent"
    else:
        selected_agent = agent_connection.travel_agent
        agent_name = "travel agent"

    if not selected_agent:
        return jsonify({"error": f"{agent_name} not initialized. Check server logs."}), 500

    def event_stream():
        try:
            for event in selected_agent.stream_query(
                user_id=user_id,
                session_id=session_id,
                message=message,
            ):
                # Ensure proper JSON serialization and SSE formatting
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"data: {event_data}\n\n"
        except Exception as e:
            error_message = json.dumps({"error": f"An error occurred while streaming: {str(e)}"})
            yield f"data: {error_message}\n\n"

    response = Response(
        stream_with_context(event_stream()), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)