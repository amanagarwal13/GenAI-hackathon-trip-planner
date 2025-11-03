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

"""Tools for Spending Analyzer Sub-Agent"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from budget_optimizer_agent.tools.firestore_client import (
    get_expenses,
    get_budgets,
    get_budget_plans,
    save_spending_pattern,
)
from budget_optimizer_agent.shared_libraries.constants import DEFAULT_CURRENCY


class SpendingAnalysisOutputSchema(BaseModel):
    """Output schema for spending analysis"""
    total_spending: float = Field(description="Total spending amount")
    expense_count: int = Field(description="Number of expenses")
    average_expense: float = Field(description="Average expense amount")
    category_breakdown: dict[str, float] = Field(description="Spending by category")
    top_categories: list[str] = Field(description="Top spending categories")
    date_range: dict = Field(description="Date range of expenses")
    insights: list[str] = Field(description="Key insights from the analysis")


class BudgetComparisonOutputSchema(BaseModel):
    """Output schema for budget comparison"""
    total_budgeted: float = Field(description="Total budgeted amount")
    total_actual: float = Field(description="Total actual spending")
    difference: float = Field(description="Difference (actual - budgeted)")
    percent_over_budget: Optional[float] = Field(None, description="Percentage over budget")
    category_comparisons: list[dict] = Field(description="Comparison by category")
    status: str = Field(description="Overall status: on_track, over_budget, under_budget")
    insights: Optional[list[str]] = Field(default_factory=list, description="Key insights from comparison")


async def analyze_spending_patterns(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    user_id: str = "default"
) -> str:
    """
    Analyze spending patterns from Firestore expenses.
    
    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        category: Optional category filter
        user_id: User ID for storing patterns
    
    Returns:
        JSON string with spending analysis
    """
    expenses = await get_expenses(start_date=start_date, end_date=end_date, category=category)
    
    if not expenses:
        return SpendingAnalysisOutputSchema(
            total_spending=0.0,
            expense_count=0,
            average_expense=0.0,
            category_breakdown={},
            top_categories=[],
            date_range={},
            insights=["No expenses found for the specified period."]
        ).model_dump_json()
    
    total_spending = sum(exp["amount"] for exp in expenses)
    expense_count = len(expenses)
    average_expense = total_spending / expense_count if expense_count > 0 else 0.0
    
    # Category breakdown
    category_breakdown = {}
    for exp in expenses:
        cat = exp.get("category", "Uncategorized")
        category_breakdown[cat] = category_breakdown.get(cat, 0.0) + exp["amount"]
    
    # Top categories
    top_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]
    top_categories_list = [cat[0] for cat in top_categories]
    
    # Date range
    dates = [exp.get("date", "") for exp in expenses if exp.get("date")]
    date_range = {}
    if dates:
        try:
            parsed_dates = [datetime.fromisoformat(d.replace('Z', '+00:00')).date() for d in dates if d]
            if parsed_dates:
                parsed_dates.sort()
                date_range = {
                    "first_expense": parsed_dates[0].isoformat(),
                    "last_expense": parsed_dates[-1].isoformat()
                }
        except:
            pass
    
    # Generate insights
    insights = []
    if total_spending > 0:
        insights.append(f"Total spending: {DEFAULT_CURRENCY} {total_spending:,.2f} across {expense_count} expenses")
        insights.append(f"Average expense: {DEFAULT_CURRENCY} {average_expense:,.2f}")
        
        if top_categories:
            top_cat = top_categories[0]
            insights.append(f"Highest spending category: {top_cat[0]} ({DEFAULT_CURRENCY} {top_cat[1]:,.2f})")
    
    if len(category_breakdown) > 1:
        insights.append(f"Expenses spread across {len(category_breakdown)} categories")
    
    # Save pattern for future reference
    pattern_data = {
        "user_id": user_id,
        "period": "custom" if (start_date or end_date) else "all_time",
        "start_date": start_date,
        "end_date": end_date,
        "total_spending": total_spending,
        "category_breakdown": category_breakdown,
        "average_daily_spending": average_expense,
        "top_categories": top_categories_list,
        "insights": insights
    }
    await save_spending_pattern(pattern_data)
    
    result = SpendingAnalysisOutputSchema(
        total_spending=total_spending,
        expense_count=expense_count,
        average_expense=average_expense,
        category_breakdown=category_breakdown,
        top_categories=top_categories_list,
        date_range=date_range,
        insights=insights
    )
    
    return result.model_dump_json()


async def compare_budget_vs_actual(
    trip_id: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> str:
    """
    Compare budgeted amounts with actual spending.
    
    Args:
        trip_id: Optional trip ID for trip-specific budget
        month: Optional month for monthly budget comparison
        year: Optional year for monthly budget comparison
    
    Returns:
        JSON string with budget comparison
    """
    # Get budgets
    budgets = []
    if trip_id:
        budget_plans = await get_budget_plans(trip_id=trip_id)
        if budget_plans:
            # Use first budget plan for comparison
            plan = budget_plans[0]
            budgets = [{
                "categories": plan.get("categories", {}),
                "total": plan.get("total_budget", 0.0)
            }]
    elif month is not None and year is not None:
        monthly_budgets = await get_budgets(month=month, year=year)
        if monthly_budgets:
            budgets = [{
                "categories": {},
                "total": monthly_budgets[0].get("amount", 0.0)
            }]
    
    if not budgets:
        result = BudgetComparisonOutputSchema(
            total_budgeted=0.0,
            total_actual=0.0,
            difference=0.0,
            category_comparisons=[],
            status="no_budget",
            insights=["No budget found for comparison."]
        )
        return result.model_dump_json()
    
    budget = budgets[0]
    total_budgeted = budget.get("total", 0.0)
    budget_categories = budget.get("categories", {})
    
    # Get actual expenses
    if trip_id:
        # For trip-specific, get expenses for trip dates
        plan = budget_plans[0]
        start_date = plan.get("start_date")
        end_date = plan.get("end_date")
        expenses = await get_expenses(start_date=start_date, end_date=end_date)
    elif month is not None and year is not None:
        # For monthly, get expenses for that month
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        expenses = await get_expenses(start_date=start_date, end_date=end_date)
    else:
        expenses = await get_expenses()
    
    # Calculate actual spending
    total_actual = sum(exp["amount"] for exp in expenses)
    
    # Category breakdown
    actual_categories = {}
    for exp in expenses:
        cat = exp.get("category", "Uncategorized")
        actual_categories[cat] = actual_categories.get(cat, 0.0) + exp["amount"]
    
    # Compare by category
    category_comparisons = []
    all_categories = set(list(budget_categories.keys()) + list(actual_categories.keys()))
    
    for cat in all_categories:
        budgeted = budget_categories.get(cat, 0.0)
        actual = actual_categories.get(cat, 0.0)
        difference = actual - budgeted
        percent_over = (difference / budgeted * 100) if budgeted > 0 else None
        
        if actual > budgeted:
            status = "over_budget"
        elif actual < budgeted * 0.8:  # Under 80% of budget
            status = "under_budget"
        else:
            status = "on_track"
        
        category_comparisons.append({
            "category": cat,
            "budgeted_amount": budgeted,
            "actual_amount": actual,
            "difference": difference,
            "percent_over_budget": percent_over,
            "status": status
        })
    
    # Overall status
    difference = total_actual - total_budgeted
    percent_over_budget = (difference / total_budgeted * 100) if total_budgeted > 0 else None
    
    if total_actual > total_budgeted:
        status = "over_budget"
    elif total_actual < total_budgeted * 0.8:
        status = "under_budget"
    else:
        status = "on_track"
    
    result = BudgetComparisonOutputSchema(
        total_budgeted=total_budgeted,
        total_actual=total_actual,
        difference=difference,
        percent_over_budget=percent_over_budget,
        category_comparisons=category_comparisons,
        status=status
    )
    
    return result.model_dump_json()

