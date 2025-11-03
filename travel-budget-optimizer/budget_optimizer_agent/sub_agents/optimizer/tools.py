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

"""Tools for Optimizer Sub-Agent"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from budget_optimizer_agent.tools.firestore_client import (
    get_expenses,
    get_budget_plans,
    save_budget_plan,
    save_recommendation,
    get_recommendations,
)


class OptimizationRecommendationSchema(BaseModel):
    """Schema for optimization recommendations"""
    category: str = Field(description="Category of the recommendation")
    title: str = Field(description="Title of the recommendation")
    description: str = Field(description="Detailed description")
    current_cost: float = Field(description="Current cost")
    suggested_cost: float = Field(description="Suggested cost")
    savings_amount: float = Field(description="Potential savings")
    savings_percent: float = Field(description="Savings percentage")
    reasoning: str = Field(description="Reasoning for the recommendation")
    actionable: bool = Field(default=True, description="Whether the recommendation is actionable")
    priority: int = Field(default=5, description="Priority level (1-10, 10 is highest)")


async def suggest_optimizations(
    trip_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    max_recommendations: int = 5
) -> str:
    """
    Generate budget optimization recommendations based on spending patterns.
    
    Args:
        trip_id: Optional trip ID
        start_date: Optional start date for analysis
        end_date: Optional end date for analysis
        max_recommendations: Maximum number of recommendations
    
    Returns:
        JSON string with optimization recommendations
    """
    # Get expenses for analysis
    expenses = await get_expenses(start_date=start_date, end_date=end_date)
    
    if not expenses:
        return "No expenses found for optimization analysis."
    
    # Analyze spending patterns
    category_totals = {}
    for exp in expenses:
        cat = exp.get("category", "Uncategorized")
        category_totals[cat] = category_totals.get(cat, 0.0) + exp["amount"]
    
    # Generate recommendations based on patterns
    recommendations = []
    
    # Find high-spending categories for optimization
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    for category, total_spending in sorted_categories[:max_recommendations]:
        # Generate optimization suggestions based on category
        if category.lower() in ["flights", "flight", "airfare"]:
            # Suggest booking alternatives
            suggested_cost = total_spending * 0.75  # 25% savings potential
            savings = total_spending - suggested_cost
            recommendations.append({
                "category": category,
                "title": "Consider booking mid-week flights",
                "description": f"Booking flights on Tuesday-Thursday can save up to 25% compared to weekend flights. Consider flexible dates for better prices.",
                "current_cost": total_spending,
                "suggested_cost": suggested_cost,
                "savings_amount": savings,
                "savings_percent": 25.0,
                "reasoning": "Mid-week flights typically cost 15-25% less than weekend flights. Flexible date booking can unlock additional savings.",
                "actionable": True,
                "priority": 9
            })
        
        elif category.lower() in ["hotel", "hotels", "accommodation"]:
            # Suggest alternatives
            suggested_cost = total_spending * 0.80  # 20% savings potential
            savings = total_spending - suggested_cost
            recommendations.append({
                "category": category,
                "title": "Consider alternative accommodations",
                "description": f"Alternative options like vacation rentals, hostels, or booking further from city center can save 20-30% on accommodation costs.",
                "current_cost": total_spending,
                "suggested_cost": suggested_cost,
                "savings_amount": savings,
                "savings_percent": 20.0,
                "reasoning": "Alternative accommodations often provide better value. Consider location flexibility for additional savings.",
                "actionable": True,
                "priority": 8
            })
        
        elif category.lower() in ["food", "restaurant", "dining"]:
            # Suggest budget-friendly options
            suggested_cost = total_spending * 0.70  # 30% savings potential
            savings = total_spending - suggested_cost
            recommendations.append({
                "category": category,
                "title": "Mix fine dining with local eateries",
                "description": f"Balancing expensive restaurants with local street food and markets can reduce dining costs by 30% while enhancing cultural experience.",
                "current_cost": total_spending,
                "suggested_cost": suggested_cost,
                "savings_amount": savings,
                "savings_percent": 30.0,
                "reasoning": "Local eateries and markets offer authentic experiences at a fraction of the cost. Mixing fine dining with budget options maximizes value.",
                "actionable": True,
                "priority": 7
            })
        
        elif category.lower() in ["transport", "transportation", "taxi", "uber"]:
            # Suggest public transport
            suggested_cost = total_spending * 0.50  # 50% savings potential
            savings = total_spending - suggested_cost
            recommendations.append({
                "category": category,
                "title": "Use public transportation or walk",
                "description": f"Public transportation, walking, or bike rentals can reduce transportation costs by 50% while providing better local experience.",
                "current_cost": total_spending,
                "suggested_cost": suggested_cost,
                "savings_amount": savings,
                "savings_percent": 50.0,
                "reasoning": "Public transport and walking are significantly cheaper than taxis/rideshares. Many destinations offer tourist passes for unlimited travel.",
                "actionable": True,
                "priority": 8
            })
        
        else:
            # Generic optimization
            suggested_cost = total_spending * 0.85  # 15% savings potential
            savings = total_spending - suggested_cost
            recommendations.append({
                "category": category,
                "title": f"Optimize {category} spending",
                "description": f"Review {category} expenses and look for opportunities to save 15-20% through better planning or alternatives.",
                "current_cost": total_spending,
                "suggested_cost": suggested_cost,
                "savings_amount": savings,
                "savings_percent": 15.0,
                "reasoning": f"General optimization opportunities exist in {category} spending. Review individual expenses for savings.",
                "actionable": True,
                "priority": 6
            })
    
    # Save recommendations to Firestore
    for rec in recommendations:
        if trip_id:
            rec["trip_id"] = trip_id
        await save_recommendation(rec)
    
    return OptimizationRecommendationSchema(
        category=recommendations[0]["category"] if recommendations else "general",
        title=recommendations[0]["title"] if recommendations else "No recommendations",
        description=recommendations[0]["description"] if recommendations else "",
        current_cost=recommendations[0]["current_cost"] if recommendations else 0.0,
        suggested_cost=recommendations[0]["suggested_cost"] if recommendations else 0.0,
        savings_amount=recommendations[0]["savings_amount"] if recommendations else 0.0,
        savings_percent=recommendations[0]["savings_percent"] if recommendations else 0.0,
        reasoning=recommendations[0]["reasoning"] if recommendations else "",
        actionable=True,
        priority=recommendations[0]["priority"] if recommendations else 5
    ).model_dump_json() if recommendations else "No optimization recommendations found."


async def create_budget_plan(
    destination: str,
    start_date: str,
    end_date: str,
    total_budget: float,
    categories: dict[str, float],
    trip_id: Optional[str] = None
) -> str:
    """
    Create a budget plan for a trip.
    
    Args:
        destination: Destination location
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        total_budget: Total budget amount
        categories: Budget amounts by category
        trip_id: Optional trip ID
    
    Returns:
        Document ID of created budget plan
    """
    budget_plan = {
        "trip_id": trip_id,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "total_budget": total_budget,
        "categories": categories,
        "status": "planned"
    }
    
    doc_id = await save_budget_plan(budget_plan)
    return f"Budget plan created successfully with ID: {doc_id}"

