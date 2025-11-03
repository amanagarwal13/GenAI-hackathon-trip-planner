# Travel Budget Optimizer & Deal Finder Agent

A sophisticated AI agent built with Google's Agent Development Kit (ADK) that intelligently analyzes travel expenses, finds deals, and optimizes budgets using Firestore integration.

## Features

- **Spending Pattern Analysis**: Analyzes expense data from Firestore to identify spending trends and patterns
- **Deal Finding**: Uses Google Search Grounding to find current travel deals on flights, hotels, and activities
- **Budget Optimization**: Generates actionable recommendations to reduce travel costs
- **Personalized Recommendations**: Learns from spending patterns to provide tailored advice
- **Dashboard Visualization**: Auto-generated dashboard with recommendations, deals, and spending analysis

## Architecture

The agent uses a multi-agent architecture with specialized sub-agents:

- **Spending Analyzer Agent**: Analyzes spending patterns and compares budgets vs actual spending
- **Deal Finder Agent**: Finds deals using Google Search Grounding
- **Optimizer Agent**: Generates optimization recommendations
- **Recommender Agent**: Provides personalized recommendations based on user history

## Setup

### Prerequisites

- Python 3.11+
- Google Cloud Project with Vertex AI enabled
- Firestore database (same as expense tracker)
- Google ADK 1.0+

### Installation

```bash
cd travel-budget-optimizer
poetry install
# or
pip install -r requirements.txt
```

### Configuration

Set environment variables:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
```

## Deployment

Deploy to Vertex AI Reasoning Engine:

```bash
cd deployment
python deploy.py --create
```

This will output a resource ID that you can use in the Flask app:

```bash
export BUDGET_AGENT_RESOURCE_ID=projects/.../reasoningEngines/...
```

## Flask Integration

The agent is integrated into the Flask app at `/budget`:

1. **Agent Singleton**: Added budget agent to `AgentSingleton` in `app.py`
2. **API Endpoints**:
   - `POST /api/budget/sessions` - Create session
   - `POST /api/budget/stream` - Stream chat responses
   - `POST /api/budget/generate-dashboard` - Auto-generate dashboard
3. **Frontend**: `budget.html` template with chat and dashboard tabs

## Usage

### Chat Interface

Ask questions like:
- "Analyze my travel spending patterns"
- "Find deals for flights to Mumbai"
- "Suggest budget optimizations"
- "Compare my budget with actual spending"

### Dashboard

The dashboard automatically loads on page load and shows:
- Summary cards with savings potential and budget status
- Top 5 optimization recommendations with savings amounts
- Active deals and alerts
- Spending analysis by category

## Firestore Collections

### New Collections Created

- `budget_plans` - Trip budget plans
- `deal_alerts` - Tracked deals and price alerts
- `optimization_recommendations` - AI-generated recommendations
- `spending_patterns` - Cached spending analysis

### Existing Collections (Read-only)

- `expenses` - Expense data from expense tracker
- `budgets` - Budget data from expense tracker

## Testing

Quick test after deployment:

```bash
python deployment/deploy.py --quicktest --resource_id=<RESOURCE_ID>
```

## Integration with Other Agents

The budget optimizer integrates seamlessly with:
- **Expense Tracker**: Reads expense data from Firestore
- **Travel Planner**: Can analyze costs for planned trips
- **Smart Packing Agent**: Provides budget context for packing decisions

## License

Apache License 2.0

