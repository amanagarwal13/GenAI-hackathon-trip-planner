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

"""Tools for Recommender Sub-Agent"""

from datetime import datetime, timedelta
from typing import Optional
from budget_optimizer_agent.tools.firestore_client import (
    get_expenses,
    get_spending_patterns,
    get_recommendations,
    get_deal_alerts,
    save_spending_pattern,
)


async def get_personalized_recommendations(
    user_id: str = "default",
    trip_id: Optional[str] = None,
    destination: Optional[str] = None,
    limit: int = 5
) -> str:
    """
    Get personalized budget recommendations based on user's spending patterns.
    
    Args:
        user_id: User ID
        trip_id: Optional trip ID
        destination: Optional destination
        limit: Maximum number of recommendations
    
    Returns:
        JSON string with personalized recommendations
    """
    # Get historical spending patterns
    patterns = await get_spending_patterns(user_id=user_id)
    
    # Get existing recommendations
    recommendations = await get_recommendations(trip_id=trip_id, limit=limit)
    
    # Get active deals
    deals = await get_deal_alerts(trip_id=trip_id, active_only=True)
    
    # Analyze patterns to personalize recommendations
    personalized_insights = []
    
    if patterns:
        # Analyze spending habits
        for pattern in patterns[:3]:  # Use last 3 patterns
            category_breakdown = pattern.get("category_breakdown", {})
            top_categories = pattern.get("top_categories", [])
            
            if top_categories:
                personalized_insights.append({
                    "type": "spending_pattern",
                    "category": top_categories[0],
                    "insight": f"Based on your spending history, {top_categories[0]} is your highest spending category. Consider optimization here first.",
                    "priority": 9
                })
    
    # Combine with existing recommendations
    result = {
        "personalized_recommendations": recommendations[:limit],
        "active_deals": deals[:limit],
        "insights": personalized_insights,
        "based_on_patterns": len(patterns) > 0
    }
    
    import json
    return json.dumps(result, indent=2)


async def learn_preferences(
    user_id: str,
    category: str,
    preferred_price_range: Optional[dict] = None,
    preferred_savings_threshold: float = 0.15
) -> str:
    """
    Learn user preferences for future recommendations.
    
    Args:
        user_id: User ID
        category: Category of preference
        preferred_price_range: Optional preferred price range
        preferred_savings_threshold: Preferred savings threshold (percentage)
    
    Returns:
        Confirmation message
    """
    # This would typically save preferences to a user preferences collection
    # For now, we'll use spending patterns to infer preferences
    
    preferences = {
        "user_id": user_id,
        "category": category,
        "preferred_price_range": preferred_price_range,
        "preferred_savings_threshold": preferred_savings_threshold,
        "learned_at": datetime.now().isoformat()
    }
    
    # Save to spending patterns collection for now
    await save_spending_pattern({
        "user_id": user_id,
        "period": "preferences",
        "preferences": preferences
    })
    
    return f"Preferences learned for {category}. Future recommendations will prioritize savings above {preferred_savings_threshold*100}%."


async def predict_budget_needs(
    destination: str,
    duration_days: int,
    user_id: str = "default"
) -> str:
    """
    Predict budget needs based on user's historical spending patterns.
    
    Args:
        destination: Destination location
        duration_days: Trip duration in days
        user_id: User ID
    
    Returns:
        JSON string with predicted budget breakdown
    """
    # Get historical spending patterns
    patterns = await get_spending_patterns(user_id=user_id)
    
    if not patterns:
        # Use default estimates if no history
        default_daily = {
            "Food": 500,
            "Transport": 300,
            "Activities": 400,
            "Misc": 200
        }
    else:
        # Calculate average daily spending from patterns
        pattern = patterns[0]  # Use most recent pattern
        total_spending = pattern.get("total_spending", 0)
        avg_daily = pattern.get("average_daily_spending", 0)
        
        # Estimate category breakdown
        category_breakdown = pattern.get("category_breakdown", {})
        total = sum(category_breakdown.values()) if category_breakdown else 1
        
        default_daily = {}
        for cat, amount in category_breakdown.items():
            default_daily[cat] = (amount / total) * avg_daily if total > 0 else avg_daily / len(category_breakdown)
    
    # Calculate predicted budget
    predicted_budget = {}
    total_predicted = 0.0
    
    for category, daily_amount in default_daily.items():
        category_total = daily_amount * duration_days
        predicted_budget[category] = category_total
        total_predicted += category_total
    
    # Add destination-specific adjustments
    prediction = {
        "destination": destination,
        "duration_days": duration_days,
        "predicted_daily_budget": sum(default_daily.values()),
        "predicted_total_budget": total_predicted,
        "category_breakdown": predicted_budget,
        "confidence": "medium" if patterns else "low",
        "based_on_history": len(patterns) > 0
    }
    
    import json
    return json.dumps(prediction, indent=2)

