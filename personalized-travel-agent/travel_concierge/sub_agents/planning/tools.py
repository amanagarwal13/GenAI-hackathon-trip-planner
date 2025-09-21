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

"""Tools for the planning sub-agent."""

import random
from google.adk.tools import ToolContext

def intelligent_budget_optimizer(tool_context: ToolContext) -> dict:
    """
    Analyzes the current itinerary and suggests cost-saving alternatives.

    Args:
        tool_context: The ADK tool context containing the itinerary in its state.

    Returns:
        A dictionary containing a list of optimization suggestions.
    """
    itinerary = tool_context.state.get('itinerary')
    if not itinerary or not itinerary.get('days'):
        return {"error": "No itinerary found to optimize."}

    suggestions = []
    total_savings = 0

    # Mock Logic: Find cheaper flight alternatives
    for day in itinerary.get('days', []):
        for event in day.get('events', []):
            if event.get('eventType') == 'flight' and event.get('price'):
                original_price = float(event['price'])
                # Simulate finding a cheaper flight (e.g., on an adjacent day or with a different airline)
                cheaper_price = round(original_price * random.uniform(0.75, 0.90), 2)
                savings = round(original_price - cheaper_price, 2)
                total_savings += savings
                suggestions.append(
                    f"Flight Suggestion: Change flight {event.get('flightNumber', '')} to a different time or carrier to save approximately ₹{savings}. The new estimated price would be ₹{cheaper_price}."
                )

    # Mock Logic: Find better value hotel alternatives
    for day in itinerary.get('days', []):
        for event in day.get('events', []):
            if event.get('eventType') == 'hotel' and event.get('price'):
                original_price = float(event['price'])
                # Simulate finding a hotel with better ratings for a slightly higher price or similar for less
                suggestion_type = random.choice(['cheaper', 'better_value'])
                if suggestion_type == 'cheaper':
                    cheaper_price = round(original_price * random.uniform(0.80, 0.95), 2)
                    savings = round(original_price - cheaper_price, 2)
                    total_savings += savings
                    suggestions.append(
                        f"Hotel Suggestion: Switch from {event.get('description', '')} to a similar hotel nearby and save approximately ₹{savings} per night. The new estimated price would be ₹{cheaper_price}."
                    )
                else: # better_value
                    new_price = round(original_price * random.uniform(1.0, 1.1), 2)
                    suggestions.append(
                        f"Hotel Suggestion: For just ₹{round(new_price - original_price, 2)} more per night, you could upgrade from {event.get('description', '')} to a hotel with a higher guest rating and better amenities. The new estimated price would be ₹{new_price}."
                    )
    
    if not suggestions:
        return {"status": "No obvious savings found, the itinerary is already well-optimized."}

    return {
        "status": "success",
        "potential_savings": f"₹{round(total_savings, 2)}",
        "suggestions": suggestions
    }
