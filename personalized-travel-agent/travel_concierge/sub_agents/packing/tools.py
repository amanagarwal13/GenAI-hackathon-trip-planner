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

"""Tools for the packing assistant sub-agent."""

from google.adk.tools import ToolContext

def get_itinerary_details(tool_context: ToolContext) -> dict:
    """
    Extracts key details from the itinerary for packing purposes.

    Args:
        tool_context: The ADK tool context containing the itinerary.

    Returns:
        A dictionary with the destination, trip duration, and a list of activity types.
    """
    itinerary = tool_context.state.get('itinerary')
    if not itinerary:
        return {"error": "No itinerary found in the current state."}

    start_date = itinerary.get('startDate', 'N/A')
    end_date = itinerary.get('endDate', 'N/A')
    destination = itinerary.get('destination', 'N/A')

    activities = set()
    for day in itinerary.get('days', []):
        for event in day.get('events', []):
            if event.get('category'):
                activities.add(event['category'])
            elif event.get('eventType') == 'hotel':
                activities.add('Leisure')
            elif event.get('eventType') == 'flight':
                activities.add('Travel')
    
    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "activities": list(activities) if activities else ["General sightseeing"]
    }

def get_weather_forecast(destination: str, start_date: str, end_date: str, tool_context: ToolContext) -> dict:
    """
    Gets the weather forecast for the trip duration at the destination.

    Args:
        destination: The travel destination.
        start_date: The start date of the trip.
        end_date: The end date of the trip.
        tool_context: The ADK tool context.

    Returns:
        A mock weather forecast.
    """
    # Mock implementation
    return {
        "forecast": f"The weather in {destination} from {start_date} to {end_date} is expected to be warm and sunny, with average temperatures between 28°C and 32°C. A chance of light evening showers."
    }

def get_local_customs(destination: str, tool_context: ToolContext) -> dict:
    """
    Provides advice on local customs and dress codes.

    Args:
        destination: The travel destination.
        tool_context: The ADK tool context.

    Returns:
        A dictionary with mock advice.
    """
    # Mock implementation with some examples
    advice = {
        "Rajasthan": "It is respectful to dress modestly, especially when visiting religious sites. Covering shoulders and knees is recommended. Carry a scarf.",
        "Goa": "Beachwear is common in tourist areas, but it's a good idea to cover up when visiting towns or villages. Light cotton clothing is ideal.",
        "Kerala": "Light, breathable clothing is best for the humid climate. If visiting a temple, men may be required to wear a mundu and women a saree or long skirt."
    }
    return {
        "advice": advice.get(destination, "No specific dress code information, but it's always wise to dress respectfully.")
    }
