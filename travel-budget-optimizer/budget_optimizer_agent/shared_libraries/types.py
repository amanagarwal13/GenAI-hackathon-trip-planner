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

"""Pydantic schemas for Budget Optimizer Agent"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ExpenseSchema(BaseModel):
    """Expense schema from Firestore"""
    id: str = Field(description="ID of the expense")
    name: str = Field(description="Name of the expense")
    amount: float = Field(description="Amount of the expense")
    date: str = Field(description="Date of the expense")
    category: str = Field(description="Category of the expense")


class BudgetPlanSchema(BaseModel):
    """Budget plan schema"""
    trip_id: Optional[str] = Field(None, description="ID of the trip")
    destination: str = Field(description="Destination of the trip")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")
    categories: dict[str, float] = Field(description="Budget amounts by category")
    total_budget: float = Field(description="Total budget amount")
    status: str = Field(default="planned", description="Status: planned, active, completed")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class DealAlertSchema(BaseModel):
    """Deal alert schema"""
    trip_id: Optional[str] = Field(None, description="ID of the trip")
    deal_type: str = Field(description="Type of deal: flight, hotel, activity, etc.")
    title: str = Field(description="Title of the deal")
    description: str = Field(description="Description of the deal")
    original_price: float = Field(description="Original price")
    deal_price: float = Field(description="Deal price")
    savings_amount: float = Field(description="Savings amount")
    savings_percent: float = Field(description="Savings percentage")
    source: str = Field(description="Source of the deal")
    url: Optional[str] = Field(None, description="URL to the deal")
    expires_at: Optional[str] = Field(None, description="Expiration date")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class OptimizationRecommendationSchema(BaseModel):
    """Optimization recommendation schema"""
    trip_id: Optional[str] = Field(None, description="ID of the trip")
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
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class SpendingPatternSchema(BaseModel):
    """Spending pattern analysis schema"""
    user_id: str = Field(description="User ID")
    period: str = Field(description="Period analyzed: month, year, all_time")
    start_date: Optional[str] = Field(None, description="Start date of period")
    end_date: Optional[str] = Field(None, description="End date of period")
    total_spending: float = Field(description="Total spending in period")
    category_breakdown: dict[str, float] = Field(description="Spending by category")
    average_daily_spending: float = Field(description="Average daily spending")
    top_categories: list[str] = Field(description="Top spending categories")
    insights: list[str] = Field(description="Key insights from the analysis")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class BudgetComparisonSchema(BaseModel):
    """Budget vs actual comparison schema"""
    trip_id: Optional[str] = Field(None, description="ID of the trip")
    category: str = Field(description="Category name")
    budgeted_amount: float = Field(description="Budgeted amount")
    actual_amount: float = Field(description="Actual amount spent")
    difference: float = Field(description="Difference (actual - budgeted)")
    percent_over_budget: Optional[float] = Field(None, description="Percentage over budget")
    status: str = Field(description="Status: on_track, over_budget, under_budget")


class DashboardDataSchema(BaseModel):
    """Dashboard data schema for UI rendering"""
    summary: dict = Field(description="Summary statistics")
    spending_analysis: dict = Field(description="Spending analysis data")
    recommendations: list[dict] = Field(description="List of recommendations")
    deals: list[dict] = Field(description="List of deals")
    budget_comparison: list[dict] = Field(description="Budget comparison data")
    forecasts: Optional[dict] = Field(None, description="Forecasted spending")

