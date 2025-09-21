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

"""Common data schema and types for smart-packing-concierge agents."""

from typing import Optional, Union, List
from enum import Enum

from google.genai import types
from pydantic import BaseModel, Field


# Convenient declaration for controlled generation.
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json"
)


class ActivityType(str, Enum):
    """Types of activities during travel."""
    SIGHTSEEING = "sightseeing"
    ADVENTURE = "adventure"
    BUSINESS = "business"
    BEACH = "beach"
    CULTURAL = "cultural"
    RELIGIOUS = "religious"
    NIGHTLIFE = "nightlife"
    SHOPPING = "shopping"
    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    FORMAL = "formal"
    CASUAL = "casual"


class ClimateZone(str, Enum):
    """Climate zones for packing recommendations."""
    TROPICAL = "tropical"
    DESERT = "desert"
    TEMPERATE = "temperate"
    COLD = "cold"
    MONSOON = "monsoon"
    MOUNTAIN = "mountain"
    COASTAL = "coastal"
    URBAN = "urban"


class PackingCategory(str, Enum):
    """Categories of packing items."""
    CLOTHING = "clothing"
    FOOTWEAR = "footwear"
    ACCESSORIES = "accessories"
    ELECTRONICS = "electronics"
    TOILETRIES = "toiletries"
    DOCUMENTS = "documents"
    MEDICAL = "medical"
    EMERGENCY = "emergency"


class Priority(str, Enum):
    """Priority levels for packing items."""
    ESSENTIAL = "essential"
    IMPORTANT = "important"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class WeatherCondition(BaseModel):
    """Weather condition for a specific day."""
    date: str = Field(description="Date in YYYY-MM-DD format")
    temperature_min: float = Field(description="Minimum temperature in Celsius")
    temperature_max: float = Field(description="Maximum temperature in Celsius")
    humidity: int = Field(description="Humidity percentage")
    precipitation_chance: int = Field(description="Chance of precipitation (0-100)")
    weather_description: str = Field(description="Weather description (sunny, rainy, etc.)")
    wind_speed: Optional[float] = Field(default=None, description="Wind speed in km/h")
    uv_index: Optional[int] = Field(default=None, description="UV index (0-11)")


class WeatherForecast(BaseModel):
    """Complete weather forecast for the trip."""
    location: str = Field(description="Location name")
    forecast_days: List[WeatherCondition] = Field(description="Daily weather conditions")
    climate_zone: ClimateZone = Field(description="Primary climate zone")
    seasonal_notes: Optional[str] = Field(default=None, description="Seasonal considerations")


class PackingItem(BaseModel):
    """Individual packing item with details."""
    name: str = Field(description="Item name")
    category: PackingCategory = Field(description="Item category")
    priority: Priority = Field(description="Packing priority")
    quantity: int = Field(default=1, description="Recommended quantity")
    reason: str = Field(description="Why this item is recommended")
    alternatives: List[str] = Field(default_factory=list, description="Alternative items")
    local_availability: bool = Field(default=False, description="Can be bought locally")
    weather_dependent: bool = Field(default=False, description="Depends on weather conditions")
    cultural_requirement: bool = Field(default=False, description="Required for cultural reasons")


class PackingList(BaseModel):
    """A comprehensive packing list."""
    destination: str = Field(description="Travel destination")
    travel_dates: str = Field(description="Travel date range")
    items: List[PackingItem] = Field(description="List of packing items")
    total_items: int = Field(description="Total number of items")
    packing_tips: List[str] = Field(default_factory=list, description="General packing tips")
    cultural_notes: List[str] = Field(default_factory=list, description="Cultural considerations")
    weather_notes: List[str] = Field(default_factory=list, description="Weather-related notes")


class DailyOutfit(BaseModel):
    """Daily outfit recommendation."""
    date: str = Field(description="Date in YYYY-MM-DD format")
    weather_summary: str = Field(description="Weather summary for the day")
    morning_outfit: List[str] = Field(description="Morning outfit items")
    afternoon_outfit: List[str] = Field(description="Afternoon outfit items")
    evening_outfit: List[str] = Field(description="Evening outfit items")
    activity_gear: List[str] = Field(description="Activity-specific gear needed")
    weather_accessories: List[str] = Field(description="Weather-related accessories")


class OutfitPlan(BaseModel):
    """Complete outfit plan for the trip."""
    destination: str = Field(description="Travel destination")
    daily_outfits: List[DailyOutfit] = Field(description="Daily outfit recommendations")
    general_tips: List[str] = Field(default_factory=list, description="General outfit tips")


class CulturalAdvice(BaseModel):
    """Cultural advice for a destination."""
    destination: str = Field(description="Travel destination")
    dress_code_tips: List[str] = Field(description="Dress code recommendations")
    cultural_items: List[str] = Field(description="Culturally important items to pack")
    etiquette_tips: List[str] = Field(description="Cultural etiquette tips")
    religious_considerations: List[str] = Field(description="Religious site considerations")
    local_customs: List[str] = Field(description="Local customs to be aware of")


class PackingOptimization(BaseModel):
    """Packing optimization recommendations."""
    weight_optimization: List[str] = Field(description="Weight reduction suggestions")
    space_optimization: List[str] = Field(description="Space saving tips")
    multi_purpose_items: List[str] = Field(description="Items that serve multiple purposes")
    leave_behind_suggestions: List[str] = Field(description="Items that can be left behind")
    local_purchase_recommendations: List[str] = Field(description="Items better bought locally")
    estimated_weight_kg: Optional[float] = Field(default=None, description="Estimated total weight")


class PackingPreferences(BaseModel):
    """User packing preferences."""
    preferred_brands: List[str] = Field(default_factory=list, description="Preferred clothing brands")
    packing_style: str = Field(default="balanced", description="Packing style (minimalist, balanced, comprehensive)")
    luggage_type: str = Field(default="suitcase", description="Preferred luggage type")
    weight_limit_kg: Optional[float] = Field(default=None, description="Weight limit in kg")
    special_requirements: List[str] = Field(default_factory=list, description="Special packing requirements")
