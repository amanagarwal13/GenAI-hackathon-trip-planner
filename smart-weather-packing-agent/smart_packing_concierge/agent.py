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

"""Smart Weather-Adaptive Packing Concierge using Agent Development Kit"""

from google.adk.agents import Agent

from smart_packing_concierge import prompt

from smart_packing_concierge.sub_agents.weather_analyzer.agent import weather_analyzer_agent
from smart_packing_concierge.sub_agents.cultural_advisor.agent import cultural_advisor_agent
from smart_packing_concierge.sub_agents.packing_optimizer.agent import packing_optimizer_agent
from smart_packing_concierge.sub_agents.outfit_planner.agent import outfit_planner_agent

from smart_packing_concierge.tools.memory import _load_packing_preferences


root_agent = Agent(
    model="gemini-2.5-pro",
    name="root_agent",
    description="A Smart Weather-Adaptive Packing Concierge using specialized sub-agents for intelligent travel packing recommendations",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        weather_analyzer_agent,
        cultural_advisor_agent,
        packing_optimizer_agent,
        outfit_planner_agent,
    ],
    before_agent_callback=_load_packing_preferences,
)
