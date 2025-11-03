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

"""Weather-related tools for the Smart Packing Concierge using Google Search Grounding."""

from google.adk.tools import ToolContext
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search
from datetime import datetime


# Create a specialized weather search agent using Google Search Grounding
_weather_search_agent = Agent(
    model="gemini-2.5-flash",
    name="weather_search_agent",
    description="An agent providing weather forecast information using Google Search Grounding",
    instruction="""
    You are a weather information specialist. When given a destination and date range, 
    search for current weather forecasts and climate information.
    
    Provide detailed weather information including:
    - Temperature ranges (min/max) for each day
    - Precipitation chances and amounts
    - Humidity levels
    - Wind speeds
    - UV index
    - Weather conditions (sunny, cloudy, rainy, etc.)
    - Seasonal patterns and climate zone information
    
    Format your response as structured information that can be used for packing recommendations.
    Include specific numbers and forecasts, not just general descriptions.
    """,
    tools=[google_search],
)

weather_search_grounding = AgentTool(agent=_weather_search_agent)
