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

"""Packing assistant sub-agent for the Travel Concierge."""

from google.adk.agents import Agent

from . import prompt
from .tools import get_itinerary_details, get_weather_forecast, get_local_customs

packing_assistant_agent = Agent(
    model="gemini-2.5-pro",
    name="packing_assistant_agent",
    description="Provides a personalized packing list based on the user's itinerary.",
    instruction=prompt.PACKING_ASSISTANT_INSTR,
    tools=[
        get_itinerary_details,
        get_weather_forecast,
        get_local_customs,
    ],
)
