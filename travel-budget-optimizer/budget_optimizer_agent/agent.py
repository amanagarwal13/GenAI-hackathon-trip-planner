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

"""Travel Budget Optimizer & Deal Finder Agent using Agent Development Kit"""

from google.adk.agents import Agent

from budget_optimizer_agent import prompt
from budget_optimizer_agent.sub_agents.spending_analyzer.agent import spending_analyzer_agent
from budget_optimizer_agent.sub_agents.deal_finder.agent import deal_finder_agent
from budget_optimizer_agent.sub_agents.optimizer.agent import optimizer_agent
from budget_optimizer_agent.sub_agents.recommender.agent import recommender_agent
from budget_optimizer_agent.tools.firestore_client import date_system_prompt


root_agent = Agent(
    model="gemini-2.5-pro",
    name="budget_optimizer_agent",
    description="A Travel Budget Optimizer & Deal Finder Agent using specialized sub-agents for intelligent budget optimization",
    instruction=prompt.ROOT_AGENT_INSTR + "\n\n" + date_system_prompt(),
    sub_agents=[
        spending_analyzer_agent,
        deal_finder_agent,
        optimizer_agent,
        recommender_agent,
    ],
)

