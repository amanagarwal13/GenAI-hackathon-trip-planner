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

"""Tools for Deal Finder Sub-Agent"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from budget_optimizer_agent.tools.firestore_client import (
    save_deal_alert,
    get_deal_alerts,
)


class DealSearchResultSchema(BaseModel):
    """Schema for deal search results"""
    deal_type: str = Field(description="Type of deal: flight, hotel, activity, etc.")
    title: str = Field(description="Title of the deal")
    description: str = Field(description="Description of the deal")
    original_price: Optional[float] = Field(None, description="Original price")
    deal_price: Optional[float] = Field(None, description="Deal price")
    savings_amount: Optional[float] = Field(None, description="Savings amount")
    savings_percent: Optional[float] = Field(None, description="Savings percentage")
    source: str = Field(description="Source of the deal")
    url: Optional[str] = Field(None, description="URL to the deal")
    expires_at: Optional[str] = Field(None, description="Expiration date")


async def find_deals(
    destination: str,
    deal_type: str = "all",
    trip_id: Optional[str] = None,
    max_results: int = 5
) -> str:
    """
    Find travel deals for a destination. This function should be called by the agent
    which will use Google Search Grounding to find actual deals.
    
    Args:
        destination: Destination city or location
        deal_type: Type of deal - "flight", "hotel", "activity", "all"
        trip_id: Optional trip ID to associate with deals
        max_results: Maximum number of deals to return
    
    Returns:
        JSON string with deal information
    """
    # This function will be enhanced by the agent using Google Search Grounding
    # For now, return a placeholder structure
    # The actual implementation will parse search results from Google Search Grounding
    
    deals = []
    
    # The agent should call this after using Google Search Grounding
    # This is a placeholder that will be populated by the agent's search results
    
    return DealSearchResultSchema(
        deal_type=deal_type,
        title=f"Deals for {destination}",
        description="Use Google Search Grounding to find actual deals",
        source="search",
    ).model_dump_json()


async def save_deals_to_firestore(deals: list[dict], trip_id: Optional[str] = None) -> list[str]:
    """
    Save multiple deals to Firestore.
    
    Args:
        deals: List of deal dictionaries
        trip_id: Optional trip ID
    
    Returns:
        List of document IDs
    """
    saved_ids = []
    for deal in deals:
        if trip_id:
            deal["trip_id"] = trip_id
        doc_id = await save_deal_alert(deal)
        saved_ids.append(doc_id)
    return saved_ids


async def search_alternatives(
    item_type: str,
    destination: str,
    current_price: float,
    date_range: Optional[str] = None
) -> str:
    """
    Search for cheaper alternatives to a travel item.
    
    Args:
        item_type: Type of item - "flight", "hotel", "activity"
        destination: Destination location
        current_price: Current price to compare against
        date_range: Optional date range
    
    Returns:
        JSON string with alternative options
    """
    # This will be enhanced by the agent using Google Search Grounding
    # to find alternatives and compare prices
    
    return f"Searching for {item_type} alternatives to {destination} priced below {current_price}"


async def track_price_changes(
    trip_id: str,
    item_type: str,
    item_name: str,
    current_price: float
) -> str:
    """
    Track price changes for a specific travel item.
    
    Args:
        trip_id: Trip ID
        item_type: Type of item
        item_name: Name/description of the item
        current_price: Current price
    
    Returns:
        JSON string with price tracking information
    """
    # Get existing deals for this trip
    existing_deals = await get_deal_alerts(trip_id=trip_id)
    
    # Check if price has dropped
    for deal in existing_deals:
        if deal.get("deal_type") == item_type and deal.get("deal_price"):
            if current_price < deal.get("deal_price", float('inf')):
                return f"Price drop detected! {item_name} is now {current_price} (was {deal.get('deal_price')})"
    
    # Save current price as new deal alert
    deal_data = {
        "trip_id": trip_id,
        "deal_type": item_type,
        "title": f"Price Alert: {item_name}",
        "description": f"Current price: {current_price}",
        "original_price": current_price,
        "deal_price": current_price,
        "savings_amount": 0.0,
        "savings_percent": 0.0,
        "source": "price_tracker"
    }
    await save_deal_alert(deal_data)
    
    return f"Price tracking started for {item_name} at {current_price}"

