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
import base64
import requests
from datetime import datetime
from flask import Flask, render_template, request, Response, jsonify, stream_with_context
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
from google.adk.sessions import VertexAiSessionService
from google.cloud import firestore

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
                packing_agent_resource_id = os.getenv("PACKING_AGENT_RESOURCE_ID") or "projects/56426154949/locations/us-central1/reasoningEngines/2347206636650627072"
                
                # Budget optimizer agent
                budget_agent_resource_id = os.getenv("BUDGET_AGENT_RESOURCE_ID") or "projects/56426154949/locations/us-central1/reasoningEngines/1494337457217339392"

                print(f"🔧 Configuration:")
                print(f"   Project ID: {project_id}")
                print(f"   Location: {location}")
                print(f"   Travel Agent Resource ID: {travel_agent_resource_id}")
                print(f"   Packing Agent Resource ID: {packing_agent_resource_id}")
                print(f"   Budget Agent Resource ID: {budget_agent_resource_id}")

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
                
                # Budget optimizer agent (optional)
                if budget_agent_resource_id:
                    try:
                        cls._instance.budget_agent = agent_engines.get(budget_agent_resource_id)
                        print(f"✓ Successfully connected to budget agent: {cls._instance.budget_agent.display_name}")
                    except Exception as e:
                        print(f"⚠️ Could not connect to budget agent: {e}")
                        cls._instance.budget_agent = None
                else:
                    cls._instance.budget_agent = None
                    print("⚠️ Budget agent resource ID not configured")
                
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
                cls._instance.budget_agent = None
                cls._instance.remote_agent = None
                cls._instance.session_service = None
        return cls._instance

# --- INITIALIZATION ---
app = Flask(__name__)
agent_connection = AgentSingleton() # Initialize the agent connection when the app starts

# --- FIRESTORE CLIENT ---
EXPENSE_COLLECTION_NAME = "expenses"
def get_firestore_client():
    """Get Firestore client instance"""
    # Use the same project ID from agent connection
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or "56426154949"
    return firestore.Client(project=project_id)

firestore_client = get_firestore_client()

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

@app.route('/expenses')
def expenses():
    return render_template('expenses.html')

@app.route('/budget')
def budget():
    return render_template('budget.html')

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
    elif agent_type == 'budget':
        selected_agent = agent_connection.budget_agent
        agent_name = "budget agent"
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
    elif agent_type == 'budget':
        selected_agent = agent_connection.budget_agent
        agent_name = "budget agent"
    else:
        selected_agent = agent_connection.travel_agent
        agent_name = "travel agent"

    if not selected_agent:
        return jsonify({"error": f"{agent_name} not initialized. Check server logs."}), 500

    def event_stream():
        try:
            event_count = 0
            print(f"🔍 Starting stream for {agent_name} (session: {session_id})")
            for event in selected_agent.stream_query(
                user_id=user_id,
                session_id=session_id,
                message=message,
            ):
                event_count += 1
                # Debug: log first few events
                if event_count <= 3:
                    print(f"📨 Event {event_count}: {json.dumps(event, default=str)[:200]}")
                
                # Ensure proper JSON serialization and SSE formatting
                event_data = json.dumps(event, ensure_ascii=False, default=str)
                yield f"data: {event_data}\n\n"
            
            print(f"✅ Stream completed for {agent_name}. Total events: {event_count}")
            if event_count == 0:
                print(f"⚠️ WARNING: No events received from {agent_name}")
        except Exception as e:
            error_msg = f"An error occurred while streaming: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            error_message = json.dumps({"error": error_msg})
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

# --- EXPENSE TRACKER API ENDPOINTS ---
EXPENSE_TRACKER_BASE_URL = "https://expense-tracker-gcp-56426154949.us-east1.run.app"
EXPENSE_TRACKER_USER_ID = "flask-webapp-stable"

@app.route('/api/expense/sessions', methods=['POST'])
def create_expense_session():
    """Create or update an expense tracker session"""
    print("🔄 Expense tracker session creation request received")
    
    data = request.get_json() or {}
    session_id = data.get('session_id', f"session_{int(datetime.now().timestamp())}")
    
    try:
        # First, get the list of available agents
        list_url = f"{EXPENSE_TRACKER_BASE_URL}/list-apps"
        list_response = requests.get(list_url)
        list_response.raise_for_status()
        available_agents = list_response.json()
        
        if not available_agents or len(available_agents) == 0:
            raise ValueError("No expense tracker agents available")
        
        app_name = available_agents[0]  # Use first available agent
        
        # Create or update session
        session_url = f"{EXPENSE_TRACKER_BASE_URL}/apps/{app_name}/users/{EXPENSE_TRACKER_USER_ID}/sessions/{session_id}"
        initial_state = data.get('initial_state', {
            "visit_count": 1,
            "created_at": datetime.now().isoformat(),
            "user_preferences": {
                "currency": "INR",
                "timezone": "Asia/Kolkata"
            }
        })
        
        session_response = requests.post(session_url, json=initial_state, headers={"Content-Type": "application/json"})
        
        # Handle 409 Conflict gracefully - session already exists, which is fine
        if session_response.status_code == 409:
            print(f"ℹ️ Session {session_id} already exists, returning existing session")
            # Try to get the existing session data
            try:
                get_session_response = requests.get(session_url)
                if get_session_response.ok:
                    session_data = get_session_response.json()
                else:
                    # If we can't get session data, return basic info
                    session_data = {"status": "exists"}
            except:
                session_data = {"status": "exists"}
            
            return jsonify({
                "id": session_id,
                "app_name": app_name,
                "session_data": session_data
            }), 200  # Return 200 instead of 201 since session already exists
        
        session_response.raise_for_status()
        session_data = session_response.json()
        
        print(f"✅ Created expense tracker session: {session_id}")
        return jsonify({
            "id": session_id,
            "app_name": app_name,
            "session_data": session_data
        }), 201
        
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors separately
        if e.response.status_code == 409:
            # Session already exists - return success
            # Ensure we have app_name (get it if not already set)
            if 'app_name' not in locals():
                try:
                    list_url = f"{EXPENSE_TRACKER_BASE_URL}/list-apps"
                    list_response = requests.get(list_url)
                    list_response.raise_for_status()
                    available_agents = list_response.json()
                    if available_agents and len(available_agents) > 0:
                        app_name = available_agents[0]
                    else:
                        app_name = None
                except:
                    app_name = None
            
            print(f"ℹ️ Session {session_id} already exists (409), returning success")
            return jsonify({
                "id": session_id,
                "app_name": app_name,
                "session_data": {"status": "exists"}
            }), 200
        else:
            error_msg = f"Failed to create expense tracker session: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return jsonify({"error": error_msg}), 500
    except Exception as e:
        error_msg = f"Failed to create expense tracker session: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/expense/run', methods=['POST'])
def expense_run():
    """Run expense tracker agent with single response"""
    data = request.get_json()
    app_name = data.get('app_name')
    session_id = data.get('session_id')
    message_text = data.get('message')
    
    if not all([app_name, session_id, message_text]):
        return jsonify({"error": "Missing required fields: app_name, session_id, message"}), 400
    
    try:
        url = f"{EXPENSE_TRACKER_BASE_URL}/run"
        payload = {
            "app_name": app_name,
            "user_id": EXPENSE_TRACKER_USER_ID,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message_text}]
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        events = response.json()
        
        return jsonify(events), 200
        
    except Exception as e:
        error_msg = f"Error running expense tracker agent: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/expense/run_sse', methods=['POST'])
def expense_run_sse():
    """Run expense tracker agent with streaming response"""
    data = request.get_json()
    app_name = data.get('app_name')
    session_id = data.get('session_id')
    message_text = data.get('message')
    token_streaming = data.get('streaming', False)
    
    if not all([app_name, session_id, message_text]):
        return jsonify({"error": "Missing required fields: app_name, session_id, message"}), 400
    
    def event_stream():
        try:
            url = f"{EXPENSE_TRACKER_BASE_URL}/run_sse"
            payload = {
                "app_name": app_name,
                "user_id": EXPENSE_TRACKER_USER_ID,
                "session_id": session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": message_text}]
                },
                "streaming": token_streaming
            }
            
            response = requests.post(url, json=payload, headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        yield decoded_line + '\n\n'
            
        except Exception as e:
            error_message = json.dumps({"error": f"An error occurred while streaming: {str(e)}"})
            yield f"data: {error_message}\n\n"
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )

# --- DASHBOARD QUERY FUNCTIONS ---
def get_dashboard_data(start_date=None, end_date=None):
    """
    Query Firestore and return aggregated expense data for dashboard.
    
    Args:
        start_date: Optional start date string (YYYY-MM-DD format)
        end_date: Optional end date string (YYYY-MM-DD format)
    
    Returns:
        dict: Dashboard data with total, categories, expense_count, date_range, etc.
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    
    # Build query based on date range
    query = collection_ref
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.where("date", ">=", start_dt.isoformat())
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        # Add one day to include the entire end_date
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
        query = query.where("date", "<=", end_dt.isoformat())
    
    # Execute query
    docs = query.stream()
    
    expenses = []
    total_amount = 0.0
    categories = {}
    expense_count = 0
    dates = []
    
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        
        amount = float(data.get("amount", 0))
        category = data.get("category", "Uncategorized")
        expense_date = data.get("date")
        
        expenses.append({
            "id": doc.id,
            "name": data.get("name", ""),
            "amount": amount,
            "category": category,
            "date": expense_date
        })
        
        total_amount += amount
        expense_count += 1
        
        # Aggregate by category
        if category not in categories:
            categories[category] = 0.0
        categories[category] += amount
        
        # Track dates
        if expense_date:
            try:
                # Parse ISO format date
                if isinstance(expense_date, str):
                    date_obj = datetime.fromisoformat(expense_date.replace('Z', '+00:00'))
                else:
                    date_obj = expense_date
                dates.append(date_obj.date() if hasattr(date_obj, 'date') else date_obj)
            except:
                pass
    
    # Calculate date range
    date_range = {}
    if dates:
        dates.sort()
        date_range = {
            "first_expense": dates[0].isoformat() if hasattr(dates[0], 'isoformat') else str(dates[0]),
            "last_expense": dates[-1].isoformat() if hasattr(dates[-1], 'isoformat') else str(dates[-1])
        }
    
    # Calculate average expense
    average_expense = total_amount / expense_count if expense_count > 0 else 0.0
    
    return {
        "total_amount": total_amount,
        "expense_count": expense_count,
        "average_expense": average_expense,
        "categories": categories,
        "date_range": date_range,
        "expenses": expenses[:10]  # Return last 10 expenses for preview
    }

@app.route('/api/expense/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data for all expenses or filtered by date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        dashboard_data = get_dashboard_data(start_date=start_date, end_date=end_date)
        
        return jsonify({
            "success": True,
            "data": dashboard_data
        }), 200
        
    except Exception as e:
        error_msg = f"Error fetching dashboard data: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/expense/dashboard/range', methods=['GET'])
def get_dashboard_range():
    """Get dashboard data filtered by date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({"error": "Both start_date and end_date are required (YYYY-MM-DD format)"}), 400
        
        # Validate date format
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        dashboard_data = get_dashboard_data(start_date=start_date, end_date=end_date)
        
        return jsonify({
            "success": True,
            "data": dashboard_data,
            "filters": {
                "start_date": start_date,
                "end_date": end_date
            }
        }), 200
        
    except Exception as e:
        error_msg = f"Error fetching dashboard data: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/expense/upload-receipt', methods=['POST'])
def upload_receipt():
    """Process receipt image using expense tracker agent"""
    print("🔄 Receipt upload request received")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400
    
    # Get session info from request
    data = request.form.to_dict()
    app_name = data.get('app_name')
    session_id = data.get('session_id')
    
    if not app_name or not session_id:
        return jsonify({"error": "Missing app_name or session_id"}), 400
    
    try:
        # Read image data and encode to base64
        image_data = file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        mime_type = file.content_type or "image/jpeg"
        
        # Send image directly to expense tracker agent
        url = f"{EXPENSE_TRACKER_BASE_URL}/run"
        payload = {
            "app_name": app_name,
            "user_id": EXPENSE_TRACKER_USER_ID,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [
                    {"text": "Please analyze this receipt image and add the expense to my records. Extract all relevant information including merchant name, amount, date, category, and items."},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64
                        }
                    }
                ]
            }
        }
        
        print(f"📤 Sending receipt image to expense tracker agent...")
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        events = response.json()
        
        print(f"✅ Receipt processed successfully")
        
        # Return the agent's response
        return jsonify({
            "success": True,
            "events": events,
            "message": "Receipt sent to expense tracker agent for processing"
        }), 200
        
    except Exception as e:
        error_msg = f"Error processing receipt: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)