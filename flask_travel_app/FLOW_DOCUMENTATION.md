# Flask Travel App - Architecture & Flow Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Agent Hierarchy](#agent-hierarchy)
4. [Request Flow](#request-flow)
5. [Agent Interactions](#agent-interactions)
6. [Sequence Diagrams](#sequence-diagrams)
7. [API Endpoints](#api-endpoints)
8. [Data Flow](#data-flow)

---

## 🎯 Overview

The Flask Travel App is a comprehensive travel planning platform that integrates multiple AI agents to provide end-to-end travel assistance. The application orchestrates three main agent types:

- **Travel Agent** (Root Agent with 8 sub-agents)
- **Packing Agent** (Smart Weather-Adaptive Packing Concierge)
- **Budget Agent** (Travel Budget Optimizer)
- **Expense Tracker Agent** (External FastAPI service)

---

## 🏗️ System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Frontend   │  │   Backend    │  │   Agent      │    │
│  │   (HTML/JS)  │→ │   (Flask)    │→ │   Singleton  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Vertex AI  │   │   Vertex AI  │   │   Vertex AI  │
│  Travel Agent│   │ Packing Agent│   │ Budget Agent │
└──────────────┘   └──────────────┘   └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│              Travel Agent Sub-Agents                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │Inspiration│ │ Planning  │ │ Booking  │ │ Pre-Trip │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ In-Trip  │ │Post-Trip │ │ Realtime │ │ Packing  │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────┐   ┌──────────────┐
│  Firestore   │   │ Expense API  │
│  Database    │   │   (FastAPI)  │
└──────────────┘   └──────────────┘
```

---

## 🤖 Agent Hierarchy

### 1. Travel Agent (Root Agent)

The main travel concierge agent that orchestrates all travel-related activities through its sub-agents.

**Sub-Agents:**

1. **Inspiration Agent** 🌟
   - Purpose: Provides destination ideas and POI suggestions
   - Tools: `map_tool` (Google Places API)
   - Output: `DestinationIdeas`, `POISuggestions`

2. **Planning Agent** 📅
   - Purpose: Creates comprehensive itineraries, finds flights and hotels
   - Sub-sub-agents:
     - `flight_search_agent`: Searches for flights using Google Search Grounding
     - `flight_seat_selection_agent`: Helps select seats
     - `hotel_search_agent`: Searches for hotels
     - `hotel_room_selection_agent`: Helps select hotel rooms
     - `itinerary_agent`: Creates and persists structured itineraries
   - Tools: `google_search_grounding`, `memorize`, `intelligent_budget_optimizer`, `save_itinerary_to_firestore`

3. **Booking Agent** 💳
   - Purpose: Handles booking confirmations and payments
   - Tools: `create_reservation`, `payment_choice`, `process_payment`

4. **Pre-Trip Agent** 🎒
   - Purpose: Prepares traveler for upcoming trip
   - Sub-sub-agents:
     - `what_to_pack_agent`: Provides packing suggestions
   - Tools: `google_search_grounding`

5. **In-Trip Agent** 🗺️
   - Purpose: Provides assistance during the trip
   - Sub-sub-agents:
     - `day_of_agent`: Handles day-of-trip needs
     - `trip_monitor_agent`: Monitors itinerary changes
   - Tools: `flight_status_check`, `event_booking_check`, `weather_impact_check`, `memorize`

6. **Post-Trip Agent** 📝
   - Purpose: Handles post-trip activities and feedback
   - Tools: `memorize`

7. **Realtime Agent** ⚡
   - Purpose: Handles real-time adjustments based on weather, traffic, etc.
   - Tools: `get_weather_forecast`, `get_traffic_conditions`

8. **Packing Assistant Agent** 🧳
   - Purpose: Provides personalized packing lists
   - Tools: `get_itinerary_details`, `get_weather_forecast`, `get_local_customs`

### 2. Packing Agent (Standalone)

**Sub-Agents:**

1. **Weather Analyzer Agent** 🌤️
   - Purpose: Analyzes weather conditions for packing
   - Tools: `weather_search_grounding`, `memorize`

2. **Cultural Advisor Agent** 🏛️
   - Purpose: Provides culturally-appropriate packing advice
   - Tools: `memorize`

3. **Packing Optimizer Agent** ⚖️
   - Purpose: Optimizes packing for weight and space
   - Tools: `analyze_packing_efficiency`, `suggest_optimizations`, `memorize`

4. **Outfit Planner Agent** 👔
   - Purpose: Creates daily outfit plans
   - Tools: `memorize`

### 3. Budget Agent

- Purpose: Optimizes travel budgets and expenses
- Integrated with expense tracking system

### 4. Expense Tracker Agent (External)

- Purpose: Tracks and categorizes travel expenses
- Deployed as separate FastAPI service
- Tools: Firestore integration for expense storage

---

## 🔄 Request Flow

### Initialization Flow

```
1. Flask App Starts
   ↓
2. AgentSingleton.__new__() called
   ↓
3. Load Environment Variables
   ↓
4. Initialize Vertex AI
   ↓
5. Connect to Agents:
   - travel_agent = agent_engines.get(travel_agent_resource_id)
   - packing_agent = agent_engines.get(packing_agent_resource_id)
   - budget_agent = agent_engines.get(budget_agent_resource_id)
   ↓
6. Initialize Session Service
   ↓
7. Initialize Firestore Client
   ↓
8. App Ready
```

### User Interaction Flow

```
User Opens Browser
   ↓
Loads Frontend (HTML/JS)
   ↓
User Completes Wizard (4 Steps):
   - Step 1: Basic Trip Info (origin, destination, dates)
   - Step 2: Budget & Preferences
   - Step 3: Travel Themes
   - Step 4: Personal Preferences
   ↓
User Clicks "Plan My Trip"
   ↓
Frontend Creates Session:
   POST /api/sessions
   { agent_type: 'travel' }
   ↓
Backend Creates Session:
   - Selects travel_agent
   - Calls session_service.create_session()
   - Returns session_id
   ↓
Frontend Sends Planning Request:
   POST /api/sessions/{session_id}/stream
   { content: "Plan trip with preferences...", agent_type: 'travel' }
   ↓
Backend Streams Response:
   - Calls travel_agent.stream_query()
   - Yields SSE events
   ↓
Frontend Displays Streamed Response
```

### Travel Planning Flow

```
User Request → Root Agent
   ↓
Root Agent Analyzes Request
   ↓
   ├─→ Inspiration Needed? → Inspiration Agent
   │                          ↓
   │                          Uses map_tool for POI suggestions
   │                          ↓
   │                          Returns destination ideas
   │
   ├─→ Planning Needed? → Planning Agent
   │                       ↓
   │                       ├─→ Flight Search Needed?
   │                       │   → flight_search_agent
   │                       │      → Uses google_search_grounding
   │                       │      → Returns flight options
   │                       │
   │                       ├─→ Seat Selection Needed?
   │                       │   → flight_seat_selection_agent
   │                       │
   │                       ├─→ Hotel Search Needed?
   │                       │   → hotel_search_agent
   │                       │      → Uses google_search_grounding
   │                       │
   │                       ├─→ Room Selection Needed?
   │                       │   → hotel_room_selection_agent
   │                       │
   │                       ├─→ Itinerary Creation Needed?
   │                       │   → itinerary_agent
   │                       │      → Uses save_itinerary_to_firestore
   │                       │      → Returns structured itinerary
   │                       │
   │                       └─→ Budget Optimization?
   │                           → intelligent_budget_optimizer tool
   │
   ├─→ Booking Needed? → Booking Agent
   │                      ↓
   │                      ├─→ create_reservation
   │                      ├─→ payment_choice
   │                      └─→ process_payment
   │
   ├─→ Pre-Trip Prep Needed? → Pre-Trip Agent
   │                            ↓
   │                            → what_to_pack_agent
   │                               → Uses google_search_grounding
   │
   ├─→ Packing Needed? → Packing Assistant Agent
   │                      ↓
   │                      Uses: get_itinerary_details,
   │                            get_weather_forecast,
   │                            get_local_customs
   │
   └─→ Other Needs? → Other Sub-Agents
```

---

## 🔀 Agent Interactions

### How Agents Use Sub-Agents

#### Example 1: Planning Agent → Flight Search Flow

```
Planning Agent receives request: "Find flights to Paris"
   ↓
Planning Agent calls flight_search_agent tool
   ↓
flight_search_agent receives request
   ↓
flight_search_agent uses google_search_grounding tool
   ↓
Google Search Grounding returns flight data
   ↓
flight_search_agent formats response as JSON
   ↓
Returns to Planning Agent
   ↓
Planning Agent presents options to user
   ↓
User selects flight
   ↓
Planning Agent calls memorize tool
   ↓
Stores selection in state
```

#### Example 2: Root Agent → Planning Agent → Itinerary Agent Flow

```
Root Agent receives: "Plan my trip to Mumbai"
   ↓
Root Agent transfers to Planning Agent
   ↓
Planning Agent collects trip preferences
   ↓
Planning Agent calls:
   - flight_search_agent → Gets flights
   - hotel_search_agent → Gets hotels
   ↓
Planning Agent calls itinerary_agent tool
   ↓
itinerary_agent creates structured itinerary
   ↓
itinerary_agent calls save_itinerary_to_firestore tool
   ↓
Itinerary saved to Firestore
   ↓
itinerary_agent returns itinerary to Planning Agent
   ↓
Planning Agent calls intelligent_budget_optimizer tool
   ↓
Budget optimizations suggested
   ↓
Planning Agent returns complete plan to Root Agent
   ↓
Root Agent presents to user
```

---

## 📊 Sequence Diagrams

See the HTML sequence diagram below for detailed visual representation of the interactions.

---

## 🔌 API Endpoints

### Session Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sessions` | POST | Create new session for agent |
| `/api/sessions/<session_id>/stream` | POST | Stream chat responses |

### Expense Tracking

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/expense/sessions` | POST | Create expense tracker session |
| `/api/expense/run` | POST | Run expense tracker (single response) |
| `/api/expense/run_sse` | POST | Run expense tracker (streaming) |
| `/api/expense/dashboard` | GET | Get expense dashboard data |
| `/api/expense/dashboard/range` | GET | Get filtered expense data |
| `/api/expense/upload-receipt` | POST | Process receipt image |

### Page Routes

| Route | Purpose |
|-------|---------|
| `/` | Home page |
| `/planner` | Travel planning interface |
| `/packing` | Packing assistant interface |
| `/budget` | Budget optimizer interface |
| `/expenses` | Expense tracker interface |

---

## 💾 Data Flow

### State Management

```
User Input
   ↓
Frontend JavaScript
   ↓
Flask Backend
   ↓
Agent Singleton
   ↓
Vertex AI Session Service
   ↓
Agent Engine (Reasoning Engine)
   ↓
Agent State (stored in session)
   ↓
Sub-Agent State
   ↓
Tools (memorize, firestore, etc.)
   ↓
Persistent Storage (Firestore)
```

### Memory Flow

```
Agent Tool Call: memorize(key, value)
   ↓
Stored in Agent Session State
   ↓
Available to all agents in session
   ↓
Persisted across conversation turns
   ↓
Loaded before each agent interaction
```

### Itinerary Flow

```
User completes wizard
   ↓
Trip preferences collected
   ↓
Planning Agent creates itinerary
   ↓
itinerary_agent formats itinerary
   ↓
save_itinerary_to_firestore called
   ↓
Stored in Firestore
   ↓
Available for:
   - In-trip agent
   - Packing agent
   - Post-trip agent
   - Expense tracking
```

---

## 🔐 Security & Authentication

- **User ID**: Currently hardcoded as `"flask-webapp-stable"` for all sessions
- **Session Management**: Each user gets unique session IDs per agent
- **Firestore**: Uses project-level authentication
- **Vertex AI**: Uses service account credentials

---

## 🚀 Deployment Architecture

```
Cloud Run (Flask App)
   ↓
Agent Engines (Vertex AI Reasoning Engines)
   ├─ Travel Agent Engine
   ├─ Packing Agent Engine
   └─ Budget Agent Engine
   ↓
Firestore Database
   ↓
External Services:
   ├─ Expense Tracker API (Cloud Run)
   ├─ Google Places API
   └─ Google Search Grounding
```

---

## 📝 Notes

- All agents use **Server-Sent Events (SSE)** for streaming responses
- Agent state is maintained in **Vertex AI sessions**
- Persistent data stored in **Firestore**
- Sub-agents communicate through **AgentTool** wrapper
- Tools can be called directly or through sub-agents

---

## 🎯 Key Design Patterns

1. **Singleton Pattern**: AgentSingleton ensures single connection instance
2. **Agent Orchestration**: Root agent delegates to specialized sub-agents
3. **Tool Composition**: Agents compose multiple tools for complex tasks
4. **State Management**: Session-based state persistence across interactions
5. **Streaming**: Real-time response streaming for better UX

---

**Last Updated**: 2025-11-02

