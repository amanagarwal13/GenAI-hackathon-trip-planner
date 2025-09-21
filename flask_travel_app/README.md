# 🌍 AI Travel Planner - Flask Web Application

A beautiful, modern web interface for the AI Travel Planner powered by Google Vertex AI.

## ✨ Features

- **🤖 AI-Powered Chat Interface**: Interactive conversation with your travel planning agent
- **📋 Trip Parameters**: Set destination, budget, dates, and travel themes
- **🎨 Modern UI**: Beautiful glassmorphism design with smooth animations
- **📱 Responsive Design**: Works great on desktop and mobile devices
- **⚡ Real-time Streaming**: Live responses from the AI agent
- **🎯 Contextual Planning**: Automatically includes your trip parameters in conversations

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Cloud Project** with Vertex AI enabled

## 🌐 Cloud Run Deployment (Recommended)

### Option 1: Using the deployment script

1. Make the deployment script executable:
```bash
chmod +x deploy.sh
```

2. Run the deployment:
```bash
./deploy.sh
```

### Option 2: Manual deployment

```bash
gcloud run deploy flask-travel-app \
    --source . \
    --project=56426154949 \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=56426154949,GOOGLE_CLOUD_LOCATION=us-central1,AGENT_RESOURCE_ID=projects/56426154949/locations/us-central1/reasoningEngines/14940163998220288" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=3600 \
    --max-instances=10 \
    --port=8080
```

## 🐛 Troubleshooting Cloud Run Issues

If you get "Sorry, there was an error setting up the chat" error:

1. **Check the logs**:
```bash
gcloud logs read --project=56426154949 --service=flask-travel-app --limit=50
```

2. **Verify environment variables**:
```bash
gcloud run services describe flask-travel-app --region=us-central1 --project=56426154949
```

3. **Required environment variables**:
   - `GOOGLE_CLOUD_PROJECT=56426154949`
   - `GOOGLE_CLOUD_LOCATION=us-central1`
   - `AGENT_RESOURCE_ID=projects/56426154949/locations/us-central1/reasoningEngines/14940163998220288`
3. **Deployed Travel Agent** on Vertex AI Reasoning Engine

### Installation

1. **Install required packages:**
   ```bash
   pip install flask python-dotenv google-cloud-aiplatform google-adk vertexai
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `personalized-travel-agent/` directory with:
   ```env
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   AGENT_RESOURCE_ID=projects/your-project/locations/us-central1/reasoningEngines/your-agent-id
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### 🧙‍♂️ **Step-by-Step Wizard Experience:**

1. **Basic Trip Info** (Step 1):
   - 📍 Enter origin and destination
   - 📅 Select travel dates
   - ✅ Form validation ensures all required fields

2. **Budget & Preferences** (Step 2):
   - 💰 Set your total budget
   - 👥 Choose number of travelers
   - 🏨 Select accommodation preference (Budget/Mid-range/Luxury)

3. **Travel Themes** (Step 3):
   - 🎯 Select multiple interests: Adventure, Heritage, Beach, Culinary, Wildlife, Spiritual, Nightlife, Shopping
   - 🎨 Beautiful card-based selection with visual feedback

4. **Personal Preferences** (Step 4):
   - 🍽️ Food preferences (Vegetarian, Vegan, etc.)
   - ⏱️ Travel pace (Relaxed, Moderate, Packed)
   - 📝 Special requirements (Optional)

5. **🚀 Plan My Trip!**
   - Click the button to generate your complete itinerary
   - AI creates a comprehensive day-by-day plan
   - Includes activities, timings, costs, and recommendations

6. **💬 Interactive Chat**:
   - Ask questions about your itinerary
   - Request modifications or alternatives
   - Get additional recommendations
   - Real-time conversation with your travel assistant

## 🛠️ Technical Details

### Architecture
- **Backend**: Flask with Server-Sent Events (SSE) for real-time streaming
- **Frontend**: Vanilla JavaScript with modern CSS animations
- **AI Integration**: Google Vertex AI Reasoning Engine via ADK
- **Styling**: Glassmorphism design with CSS Grid and Flexbox

### Key Files
- `app.py` - Main Flask application with API endpoints
- `static/planner.js` - Frontend JavaScript for chat functionality
- `static/style.css` - Modern CSS styling with animations
- `templates/` - HTML templates using Jinja2

### API Endpoints
- `POST /api/sessions` - Create new chat session
- `POST /api/sessions/{id}/stream` - Stream chat responses

## 🎨 Major Enhancements Made

### ✅ **Complete UX Redesign**
- **🧙‍♂️ Multi-Step Wizard** - Guided onboarding experience with 4 steps
- **📊 Progress Tracking** - Visual progress bar and step indicators
- **✨ Modern UI** - Glassmorphism design with beautiful gradients
- **📱 Fully Responsive** - Works perfectly on all devices

### ✅ **Enhanced Trip Planning**
- **🎯 Comprehensive Data Collection** - Origin, destination, budget, themes, preferences
- **🚀 One-Click Planning** - "Plan My Trip" generates complete itineraries
- **📋 Smart Form Validation** - Real-time validation with helpful feedback
- **🎨 Interactive Theme Selection** - Beautiful card-based interface

### ✅ **Advanced Agent Integration**
- **💬 Structured Prompting** - Sends comprehensive trip context to AI
- **📝 Detailed Itinerary Generation** - Day-by-day plans with activities and costs
- **🔄 Real-time Streaming** - Live responses with proper event handling
- **🛠️ Tool Call Display** - Shows when AI is using tools

### ✅ **Professional Chat Experience**
- **💭 Context-Aware Conversations** - AI remembers all your preferences
- **🎨 Beautiful Message Formatting** - Proper styling for different message types
- **⚡ Loading States** - Visual feedback during processing
- **✏️ Edit Preferences** - Easy way to modify trip parameters

## 🔧 Troubleshooting

### Common Issues

1. **"Agent not initialized" error:**
   - Check your `.env` file configuration
   - Verify your Google Cloud credentials
   - Ensure the agent is deployed and accessible

2. **Import errors:**
   - Install all required packages: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Chat not working:**
   - Open browser developer tools to check for JavaScript errors
   - Verify the Flask server is running on port 5000
   - Check network connectivity

### Debug Mode

The app runs in debug mode by default. Check the console output for detailed error messages.

## 🌟 Features Comparison

| Feature | Before | After |
|---------|--------|-------|
| **User Experience** | 🔶 Basic form + chat | ✅ **4-step guided wizard** |
| **Trip Planning** | 🔶 Manual parameter entry | ✅ **One-click comprehensive planning** |
| **Agent Integration** | ❌ Broken streaming | ✅ **Perfect streaming + structured prompts** |
| **UI Design** | 🔶 Basic styling | ✅ **Modern glassmorphism + animations** |
| **Data Collection** | 🔶 Limited fields | ✅ **Comprehensive preferences (8+ categories)** |
| **Itinerary Generation** | ❌ No structured output | ✅ **Detailed day-by-day itineraries** |
| **Chat Experience** | 🔶 Basic messages | ✅ **Context-aware + beautiful formatting** |
| **Responsiveness** | 🔶 Limited mobile support | ✅ **Fully responsive design** |
| **Visual Feedback** | ❌ No loading states | ✅ **Progress bars + loading animations** |
| **Form Validation** | ❌ No validation | ✅ **Real-time validation + helpful errors** |

### 🎯 **Key Workflow Improvements:**

**Before:** Fill form → Chat → Hope for good results  
**After:** Guided wizard → Comprehensive data collection → One-click planning → Professional itinerary → Interactive refinement

## 📝 License

This project is part of the Google ADK samples and follows the Apache 2.0 License.

---

**Happy Traveling! 🧳✈️**
