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

"""Memory and state management tools for the Smart Packing Concierge."""

import os
import json
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext


def memorize(information: str, tool_context: ToolContext) -> dict:
    """
    Memorize important packing-related information for future reference.

    Args:
        information: Information to remember about packing preferences or requirements
        tool_context: The ADK tool context

    Returns:
        Confirmation of what was memorized
    """
    # Store in session state
    if 'packing_memory' not in tool_context.state:
        tool_context.state['packing_memory'] = []
    
    tool_context.state['packing_memory'].append(information)
    
    return {
        "status": "memorized",
        "information": information,
        "total_memories": len(tool_context.state['packing_memory'])
    }


def _load_packing_preferences(callback_context: CallbackContext) -> None:
    """
    Load default packing preferences and user profile information.
    
    Args:
        callback_context: The ADK callback context
    """
    # Load default packing preferences
    default_preferences = {
        "packing_style": "balanced",
        "weight_conscious": True,
        "cultural_sensitivity": True,
        "weather_adaptive": True,
        "preferred_categories": ["clothing", "electronics", "documents", "toiletries"],
        "special_requirements": []
    }
    
    # Set default user profile
    default_user_profile = {
        "name": "Traveler",
        "packing_experience": "intermediate",
        "travel_frequency": "occasional",
        "preferred_luggage": "suitcase",
        "cultural_awareness": "high"
    }
    
    # Try to load from environment variable or use default
    scenario_path = os.getenv("PACKING_SCENARIO", None)
    
    if scenario_path and os.path.exists(scenario_path):
        try:
            with open(scenario_path, 'r') as f:
                loaded_data = json.load(f)
                callback_context.state.update(loaded_data)
        except Exception as e:
            print(f"Error loading packing scenario: {e}")
            callback_context.state['packing_preferences'] = default_preferences
            callback_context.state['user_profile'] = default_user_profile
    else:
        callback_context.state['packing_preferences'] = default_preferences
        callback_context.state['user_profile'] = default_user_profile
    
    # Initialize packing memory if not exists
    if 'packing_memory' not in callback_context.state:
        callback_context.state['packing_memory'] = []
        
    # Set default itinerary if not exists
    if 'itinerary' not in callback_context.state:
        callback_context.state['itinerary'] = {}
        
    print(f"✓ Smart Packing Concierge initialized with default preferences")


def get_packing_memory(tool_context: ToolContext) -> dict:
    """
    Retrieve stored packing memories and preferences.

    Args:
        tool_context: The ADK tool context

    Returns:
        Dictionary containing packing memories and preferences
    """
    return {
        "packing_memories": tool_context.state.get('packing_memory', []),
        "packing_preferences": tool_context.state.get('packing_preferences', {}),
        "user_profile": tool_context.state.get('user_profile', {})
    }
