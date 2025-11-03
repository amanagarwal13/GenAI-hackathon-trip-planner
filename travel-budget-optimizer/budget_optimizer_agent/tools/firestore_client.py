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

"""Firestore client utilities for Budget Optimizer Agent"""

from datetime import datetime
from typing import Optional
from google.cloud.firestore import AsyncClient, FieldFilter, DocumentReference
from budget_optimizer_agent.shared_libraries.constants import (
    EXPENSE_COLLECTION_NAME,
    BUDGET_COLLECTION_NAME,
    BUDGET_PLANS_COLLECTION_NAME,
    DEAL_ALERTS_COLLECTION_NAME,
    OPTIMIZATION_RECOMMENDATIONS_COLLECTION_NAME,
    SPENDING_PATTERNS_COLLECTION_NAME,
)


# Initialize Firestore client
firestore_client: AsyncClient = AsyncClient()


def date_system_prompt() -> str:
    """Get current date prompt for agents"""
    return (
        "Today's date is "
        + str(datetime.now().date())
        + ". Please use this date for all finding relative other dates. Example: finding yesterday, tomorrow, weekend."
    )


async def get_expenses(start_date: Optional[str] = None, end_date: Optional[str] = None, category: Optional[str] = None) -> list[dict]:
    """
    Get expenses from Firestore with optional filters.
    
    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        category: Optional category filter
    
    Returns:
        List of expense dictionaries
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    query = collection_ref
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.where(filter=FieldFilter("date", ">=", start_dt.isoformat()))
    
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.where(filter=FieldFilter("date", "<=", end_dt.isoformat()))
    
    if category:
        query = query.where(filter=FieldFilter("category", "==", category))
    
    docs = await query.get()
    
    expenses = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        expenses.append({
            "id": doc.id,
            "name": data.get("name", ""),
            "amount": float(data.get("amount", 0)),
            "date": data.get("date", ""),
            "category": data.get("category", "Uncategorized")
        })
    
    return expenses


async def get_budgets(month: Optional[int] = None, year: Optional[int] = None) -> list[dict]:
    """
    Get budgets from Firestore with optional filters.
    
    Args:
        month: Optional month filter (1-12)
        year: Optional year filter
    
    Returns:
        List of budget dictionaries
    """
    collection_ref = firestore_client.collection(BUDGET_COLLECTION_NAME)
    query = collection_ref
    
    if month is not None:
        query = query.where(filter=FieldFilter("month", "==", month))
    
    if year is not None:
        query = query.where(filter=FieldFilter("year", "==", year))
    
    docs = await query.get()
    
    budgets = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        budgets.append({
            "id": doc.id,
            "amount": float(data.get("amount", 0)),
            "month": data.get("month"),
            "year": data.get("year")
        })
    
    return budgets


async def save_budget_plan(budget_plan: dict) -> str:
    """
    Save a budget plan to Firestore.
    
    Args:
        budget_plan: Budget plan dictionary
    
    Returns:
        Document ID of saved budget plan
    """
    collection_ref = firestore_client.collection(BUDGET_PLANS_COLLECTION_NAME)
    budget_plan["created_at"] = datetime.now().isoformat()
    doc_ref: DocumentReference = (await collection_ref.add(budget_plan))[1]
    return doc_ref.id


async def get_budget_plans(trip_id: Optional[str] = None, status: Optional[str] = None) -> list[dict]:
    """
    Get budget plans from Firestore.
    
    Args:
        trip_id: Optional trip ID filter
        status: Optional status filter
    
    Returns:
        List of budget plan dictionaries
    """
    collection_ref = firestore_client.collection(BUDGET_PLANS_COLLECTION_NAME)
    query = collection_ref
    
    if trip_id:
        query = query.where(filter=FieldFilter("trip_id", "==", trip_id))
    
    if status:
        query = query.where(filter=FieldFilter("status", "==", status))
    
    docs = await query.get()
    
    plans = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        plans.append({
            "id": doc.id,
            **data
        })
    
    return plans


async def save_deal_alert(deal_alert: dict) -> str:
    """
    Save a deal alert to Firestore.
    
    Args:
        deal_alert: Deal alert dictionary
    
    Returns:
        Document ID of saved deal alert
    """
    collection_ref = firestore_client.collection(DEAL_ALERTS_COLLECTION_NAME)
    deal_alert["created_at"] = datetime.now().isoformat()
    doc_ref: DocumentReference = (await collection_ref.add(deal_alert))[1]
    return doc_ref.id


async def get_deal_alerts(trip_id: Optional[str] = None, active_only: bool = True) -> list[dict]:
    """
    Get deal alerts from Firestore.
    
    Args:
        trip_id: Optional trip ID filter
        active_only: If True, only return non-expired deals
    
    Returns:
        List of deal alert dictionaries
    """
    collection_ref = firestore_client.collection(DEAL_ALERTS_COLLECTION_NAME)
    query = collection_ref
    
    if trip_id:
        query = query.where(filter=FieldFilter("trip_id", "==", trip_id))
    
    if active_only:
        today = datetime.now().isoformat()
        query = query.where(
            filter=FieldFilter("expires_at", ">=", today)
        )
    
    docs = await query.get()
    
    deals = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        deals.append({
            "id": doc.id,
            **data
        })
    
    return deals


async def save_recommendation(recommendation: dict) -> str:
    """
    Save an optimization recommendation to Firestore.
    
    Args:
        recommendation: Recommendation dictionary
    
    Returns:
        Document ID of saved recommendation
    """
    collection_ref = firestore_client.collection(OPTIMIZATION_RECOMMENDATIONS_COLLECTION_NAME)
    recommendation["created_at"] = datetime.now().isoformat()
    doc_ref: DocumentReference = (await collection_ref.add(recommendation))[1]
    return doc_ref.id


async def get_recommendations(trip_id: Optional[str] = None, limit: int = 10) -> list[dict]:
    """
    Get optimization recommendations from Firestore.
    
    Args:
        trip_id: Optional trip ID filter
        limit: Maximum number of recommendations to return
    
    Returns:
        List of recommendation dictionaries
    """
    collection_ref = firestore_client.collection(OPTIMIZATION_RECOMMENDATIONS_COLLECTION_NAME)
    query = collection_ref
    
    if trip_id:
        query = query.where(filter=FieldFilter("trip_id", "==", trip_id))
    
    docs = await query.get()
    
    recommendations = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        recommendations.append({
            "id": doc.id,
            **data
        })
    
    # Sort by priority (highest first) and limit
    recommendations.sort(key=lambda x: x.get("priority", 0), reverse=True)
    return recommendations[:limit]


async def save_spending_pattern(pattern: dict) -> str:
    """
    Save a spending pattern analysis to Firestore.
    
    Args:
        pattern: Spending pattern dictionary
    
    Returns:
        Document ID of saved pattern
    """
    collection_ref = firestore_client.collection(SPENDING_PATTERNS_COLLECTION_NAME)
    pattern["created_at"] = datetime.now().isoformat()
    doc_ref: DocumentReference = (await collection_ref.add(pattern))[1]
    return doc_ref.id


async def get_spending_patterns(user_id: str, period: Optional[str] = None) -> list[dict]:
    """
    Get spending patterns from Firestore.
    
    Args:
        user_id: User ID
        period: Optional period filter
    
    Returns:
        List of spending pattern dictionaries
    """
    collection_ref = firestore_client.collection(SPENDING_PATTERNS_COLLECTION_NAME)
    query = collection_ref.where(filter=FieldFilter("user_id", "==", user_id))
    
    if period:
        query = query.where(filter=FieldFilter("period", "==", period))
    
    docs = await query.get()
    
    patterns = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        patterns.append({
            "id": doc.id,
            **data
        })
    
    return patterns

