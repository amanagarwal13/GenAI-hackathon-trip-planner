# GenAI Hackathon Trip Planner

This repository contains a comprehensive, AI-powered travel planning solution built for the GenAI Hackathon. It combines a beautiful web interface with a powerful multi-agent system to create a personalized travel concierge experience, from initial inspiration to packing for your trip.

## ✨ Features

- **🤖 AI-Powered Chat Interface**: An interactive, conversational interface for planning your trip.
- **🧙‍♂️ Multi-Step Wizard**: A guided experience to gather all your travel preferences, including destination, budget, dates, themes, and more.
- **🌍 Comprehensive Trip Planning**: From inspiration and itinerary generation to booking flights and hotels (mocked).
- **🌤️ Smart Weather-Adaptive Packing**: Get intelligent packing recommendations based on real-time weather forecasts and cultural norms for your destination.
- **🏛️ Cultural Sensitivity**: Destination-specific dress codes and cultural requirements are taken into account.
- **👔 Daily Outfit Planning**: Receive day-by-day outfit recommendations based on your planned activities and the weather.
- **📱 Modern, Responsive UI**: A beautiful glassmorphism design that works seamlessly on desktop and mobile devices.
- **⚡ Real-time Streaming**: Get live responses from the AI agent.

## 🏗️ Architecture

The project consists of three main components:

1.  **Flask Travel App (`flask_travel_app/`)**: A Flask-based web application that provides the user interface for the travel planner. It communicates with the `personalized-travel-agent`.
2.  **Personalized Travel Agent (`personalized-travel-agent/`)**: A sophisticated multi-agent system built with the Google Agent Development Kit (ADK). This is the "brain" of the operation, handling trip inspiration, planning, and booking.
3.  **Smart Weather Packing Agent (`smart-weather-packing-agent/`)**: A specialized agent, also built with ADK, that provides intelligent packing advice. It can be used as a standalone agent or integrated into the main travel agent's workflow.

```
[ User ] <--> [ Flask Travel App (UI) ] <--> [ Personalized Travel Agent ]
                                                     |
                                                     V
                                         [ Smart Weather Packing Agent ]
```

## 🚀 Getting Started

To get the full application running, you will need to set up each of the three components.

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/) for dependency management in the agent projects.
- A Google Cloud Project with the Vertex AI API enabled.
- API Key for Google Maps Platform Places API.
- `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).

### Installation & Setup

#### 1. Personalized Travel Agent

This is the core agent that powers the travel planning.

```bash
cd personalized-travel-agent
poetry install
cp .env.example .env
```

Now, edit the `.env` file and fill in your Google Cloud Project details and Places API key.

#### 2. Smart Weather Packing Agent

This agent provides packing recommendations.

```bash
cd smart-weather-packing-agent
poetry install
```

Set the required environment variables for your Google Cloud project.

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

#### 3. Flask Travel App

This is the web interface.

```bash
cd flask_travel_app
pip install -r requirements.txt
cp .env.example .env
```

You will need to deploy the `personalized-travel-agent` to a Vertex AI Reasoning Engine first and then put the `AGENT_RESOURCE_ID` in the `.env` file for the Flask app.

### Running the Application

1.  **Deploy the Personalized Travel Agent**: Follow the deployment instructions in `personalized-travel-agent/README.md` to deploy it as a Vertex AI Reasoning Engine.
2.  **Configure the Flask App**: Update the `.env` file in `flask_travel_app/` with the `AGENT_RESOURCE_ID` of your deployed agent.
3.  **Run the Flask App**:
    ```bash
    cd flask_travel_app
    python app.py
    ```
4.  Open your browser to `http://localhost:5000` to start planning your trip!

##  Projects

Here is a brief overview of each sub-project. For more details, please see the `README.md` file in each directory.

### 🌐 `flask_travel_app/`

A modern, responsive web application built with Flask and vanilla JavaScript. It provides a beautiful and intuitive interface for interacting with the travel agent.

### 🤖 `personalized-travel-agent/`

A multi-agent system built with Google's ADK. It acts as a personal travel concierge, with different agents specializing in:
-   **Inspiration**: Suggesting destinations and activities.
-   **Planning**: Creating detailed itineraries.
-   **Booking**: Handling mock flight, hotel, and payment processing.
-   **Pre-trip, In-trip, and Post-trip assistance**.

### 🧳 `smart-weather-packing-agent/`

A specialized AI agent that provides intelligent, weather-adaptive, and culturally-sensitive packing recommendations. It has sub-agents for:
-   **Weather Analysis**
-   **Cultural Advice**
-   **Packing Optimization**
-   **Daily Outfit Planning**

## ☁️ Deployment

The recommended way to deploy the application is to:
1.  Deploy the `personalized-travel-agent` to **Vertex AI Reasoning Engine**.
2.  Deploy the `flask_travel_app` to **Google Cloud Run**. A `deploy.sh` script is provided in the `flask_travel_app` directory to simplify this process.

Please refer to the README files in the respective project directories for detailed deployment instructions.

## 📝 License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for more details.
