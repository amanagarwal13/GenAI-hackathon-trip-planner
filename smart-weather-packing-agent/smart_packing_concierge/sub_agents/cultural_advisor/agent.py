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

"""Cultural advisor sub-agent for the Smart Packing Concierge."""

from google.adk.agents import Agent

from . import prompt
from .tools import get_cultural_guidelines, validate_cultural_appropriateness
from smart_packing_concierge.tools.memory import memorize

cultural_advisor_agent = Agent(
    model="gemini-2.5-pro",
    name="cultural_advisor_agent",
    description="Provides culturally-sensitive packing recommendations based on destination customs and dress codes.",
    instruction=prompt.CULTURAL_ADVISOR_INSTR,
    tools=[
        get_cultural_guidelines,
        validate_cultural_appropriateness,
        memorize,
    ],
)
