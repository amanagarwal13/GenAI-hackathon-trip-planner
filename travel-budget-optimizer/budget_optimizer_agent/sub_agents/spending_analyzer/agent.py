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

"""Spending Analyzer sub-agent for the Budget Optimizer."""

from google.adk.agents import Agent

from . import prompt
from .tools import analyze_spending_patterns, compare_budget_vs_actual
from budget_optimizer_agent.tools.firestore_client import date_system_prompt

spending_analyzer_agent = Agent(
    model="gemini-2.5-pro",
    name="spending_analyzer_agent",
    description="Analyzes spending patterns from expense data and compares budgets with actual spending.",
    instruction=prompt.SPENDING_ANALYZER_INSTR + "\n\n" + date_system_prompt(),
    tools=[
        analyze_spending_patterns,
        compare_budget_vs_actual,
    ],
)

