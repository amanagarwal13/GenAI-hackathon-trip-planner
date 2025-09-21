# Copyright 2024 Google LLC
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

"""Tools for the realtime sub-agent."""

from google.adk.tools import ToolContext

def get_weather_forecast(location: str, tool_context: ToolContext) -> dict:
    """
    Gets the weather forecast for a given location.

    Args:
        location: The location to get the weather forecast for.
        tool_context: The ADK tool context.

    Returns:
        The weather forecast for the location.
    """
    # In a real application, this would call a weather API.
    return {"forecast": f"The weather in {location} is sunny with a high of 25°C."}


def get_traffic_conditions(start_location: str, end_location: str, tool_context: ToolContext) -> dict:
    """
    Gets the traffic conditions between two locations.

    Args:
        start_location: The start location.
        end_location: The end location.
        tool_context: The ADK tool context.

    Returns:
        The traffic conditions between the two locations.
    """
    # In a real application, this would call a traffic API (e.g., Google Maps).
    return {
        "conditions": f"The traffic between {start_location} and {end_location} is light."
    }
