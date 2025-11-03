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

"""Optimizer sub-agent for the Budget Optimizer."""

from google.adk.agents import Agent

from . import prompt
from .tools import suggest_optimizations, create_budget_plan
from budget_optimizer_agent.tools.firestore_client import date_system_prompt

optimizer_agent = Agent(
    model="gemini-2.5-pro",
    name="optimizer_agent",
    description="Generates budget optimization recommendations and creates budget plans.",
    instruction=prompt.OPTIMIZER_INSTR + "\n\n" + date_system_prompt(),
    tools=[
        suggest_optimizations,
        create_budget_plan,
    ],
)

