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

"""Deal Finder sub-agent for the Budget Optimizer."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

from . import prompt
from .tools import find_deals, save_deals_to_firestore, search_alternatives, track_price_changes
from budget_optimizer_agent.tools.firestore_client import date_system_prompt

# Create Google Search Grounding agent tool
_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search_grounding",
    description="An agent providing Google-search grounding capability for finding travel deals",
    instruction="""
    Search for current travel deals, discounts, and promotions.
    Extract deal information including prices, discounts, expiration dates, and sources.
    Provide actionable information with URLs when available.
    Focus on finding significant savings (>10% discount).
    """,
    tools=[google_search],
)

google_search_grounding = AgentTool(agent=_search_agent)

deal_finder_agent = Agent(
    model="gemini-2.5-pro",
    name="deal_finder_agent",
    description="Finds travel deals, discounts, and cost-saving opportunities using Google Search Grounding.",
    instruction=prompt.DEAL_FINDER_INSTR + "\n\n" + date_system_prompt(),
    tools=[
        google_search_grounding,
        find_deals,
        save_deals_to_firestore,
        search_alternatives,
        track_price_changes,
    ],
)

