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

"""Tools for the outfit planner sub-agent."""

from google.adk.tools import ToolContext
from datetime import datetime, timedelta


def create_daily_outfits(destination: str, start_date: str, end_date: str, activities: str, tool_context: ToolContext) -> dict:
    """
    Create daily outfit recommendations based on weather, activities, and cultural considerations.

    Args:
        destination: Travel destination
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD)
        activities: Planned activities (comma-separated)
        tool_context: The ADK tool context

    Returns:
        Daily outfit recommendations for the entire trip
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    
    activity_list = [activity.strip().lower() for activity in activities.split(',')]
    destination_lower = destination.lower()
    
    outfit_plan = {
        "destination": destination,
        "trip_duration": (end - start).days + 1,
        "daily_outfits": [],
        "packing_essentials": [],
        "versatile_pieces": []
    }
    
    current_date = start
    day_number = 1
    
    while current_date <= end:
        # Get weather for this day (mock data)
        weather = _get_daily_weather(destination, current_date)
        
        # Determine main activity for the day
        main_activity = _get_daily_activity(activity_list, day_number)
        
        # Create outfit for the day
        daily_outfit = {
            "date": current_date.strftime("%Y-%m-%d"),
            "day_number": day_number,
            "weather_summary": f"{weather['description']}, {weather['temp_min']}-{weather['temp_max']}°C",
            "main_activity": main_activity,
            "morning_outfit": _create_morning_outfit(weather, main_activity, destination_lower),
            "afternoon_outfit": _create_afternoon_outfit(weather, main_activity, destination_lower),
            "evening_outfit": _create_evening_outfit(weather, main_activity, destination_lower),
            "activity_gear": _get_activity_gear(main_activity, weather),
            "weather_accessories": _get_weather_accessories(weather),
            "cultural_notes": _get_cultural_outfit_notes(destination_lower, main_activity)
        }
        
        outfit_plan["daily_outfits"].append(daily_outfit)
        current_date += timedelta(days=1)
        day_number += 1
    
    # Add general recommendations
    outfit_plan["packing_essentials"] = _get_packing_essentials(destination_lower, activity_list)
    outfit_plan["versatile_pieces"] = _get_versatile_pieces(destination_lower, activity_list)
    
    return outfit_plan


def get_outfit_combinations(base_items: str, destination: str, tool_context: ToolContext) -> dict:
    """
    Suggest outfit combinations using a set of base items.

    Args:
        base_items: Comma-separated list of clothing items available
        destination: Travel destination
        tool_context: The ADK tool context

    Returns:
        Multiple outfit combinations using the available items
    """
    items = [item.strip() for item in base_items.split(',')]
    destination_lower = destination.lower()
    
    combinations = {
        "casual_day_outfits": [],
        "formal_outfits": [],
        "cultural_site_outfits": [],
        "evening_outfits": [],
        "mix_match_tips": []
    }
    
    # Categorize available items
    tops = [item for item in items if any(x in item.lower() for x in ['shirt', 'top', 'blouse', 'tee'])]
    bottoms = [item for item in items if any(x in item.lower() for x in ['pants', 'skirt', 'shorts', 'jeans'])]
    dresses = [item for item in items if 'dress' in item.lower()]
    outerwear = [item for item in items if any(x in item.lower() for x in ['jacket', 'sweater', 'cardigan'])]
    
    # Create casual combinations
    for top in tops[:3]:  # Limit to avoid too many combinations
        for bottom in bottoms[:2]:
            combinations["casual_day_outfits"].append({
                "outfit": f"{top} + {bottom}",
                "suitable_for": "Sightseeing, casual dining, shopping",
                "weather": "Mild to warm weather"
            })
    
    # Cultural site outfits (modest combinations)
    modest_tops = [item for item in tops if any(x in item.lower() for x in ['long sleeve', 'modest', 'covered'])]
    long_bottoms = [item for item in bottoms if any(x in item.lower() for x in ['long pants', 'trousers', 'maxi'])]
    
    if modest_tops and long_bottoms:
        combinations["cultural_site_outfits"].append({
            "outfit": f"{modest_tops[0]} + {long_bottoms[0]}",
            "suitable_for": "Temples, religious sites, conservative areas",
            "cultural_note": "Covers shoulders and knees as required"
        })
    
    # Evening combinations
    if dresses:
        combinations["evening_outfits"].append({
            "outfit": f"{dresses[0]} + light jacket",
            "suitable_for": "Dinner, evening activities",
            "note": "Versatile for various evening occasions"
        })
    
    # Mix and match tips
    combinations["mix_match_tips"] = [
        "Stick to 2-3 color palette for easy mixing",
        "Choose pieces that work for multiple occasions",
        "Layer items for temperature changes throughout the day",
        "Bring one statement piece to dress up basic outfits"
    ]
    
    return combinations


def _get_daily_weather(destination: str, date: datetime) -> dict:
    """Get mock weather data for a specific day."""
    # Mock weather based on destination and season
    base_temp = 25  # Default
    
    destination_lower = destination.lower()
    if any(x in destination_lower for x in ['mumbai', 'chennai']):
        base_temp = 30
    elif any(x in destination_lower for x in ['delhi', 'jaipur']):
        base_temp = 28
    elif any(x in destination_lower for x in ['bangalore', 'pune']):
        base_temp = 24
    elif any(x in destination_lower for x in ['himachal', 'kashmir']):
        base_temp = 15
    
    # Seasonal adjustments
    month = date.month
    if month in [12, 1, 2]:  # Winter
        base_temp -= 5
    elif month in [6, 7, 8, 9]:  # Monsoon
        base_temp -= 2
    
    return {
        "temp_min": base_temp - 3,
        "temp_max": base_temp + 5,
        "description": ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"][date.day % 4],
        "humidity": 60 + (date.day % 30),
        "rain_chance": 20 + (date.day % 40)
    }


def _get_daily_activity(activities: list, day_number: int) -> str:
    """Determine main activity for a specific day."""
    if not activities:
        return "sightseeing"
    
    # Cycle through activities
    return activities[(day_number - 1) % len(activities)]


def _create_morning_outfit(weather: dict, activity: str, destination: str) -> list:
    """Create morning outfit based on conditions."""
    outfit = []
    
    # Base layer based on temperature
    if weather["temp_max"] > 30:
        outfit.append("Light cotton t-shirt or breathable top")
    elif weather["temp_max"] > 20:
        outfit.append("Comfortable shirt or light top")
    else:
        outfit.append("Long-sleeve shirt or light sweater")
    
    # Bottoms based on activity and culture
    if activity in ['religious', 'cultural'] or any(x in destination for x in ['india']):
        outfit.append("Long pants or modest skirt")
    elif weather["temp_max"] > 28:
        outfit.append("Light pants or comfortable shorts")
    else:
        outfit.append("Comfortable pants or jeans")
    
    # Footwear
    if activity in ['sightseeing', 'adventure']:
        outfit.append("Comfortable walking shoes")
    else:
        outfit.append("Casual shoes or sandals")
    
    return outfit


def _create_afternoon_outfit(weather: dict, activity: str, destination: str) -> list:
    """Create afternoon outfit (often same as morning with adjustments)."""
    morning_outfit = _create_morning_outfit(weather, activity, destination)
    
    # Add sun protection for hot afternoons
    if weather["temp_max"] > 28:
        morning_outfit.append("Hat or cap for sun protection")
    
    # Add layer for temperature changes
    if weather["temp_max"] - weather["temp_min"] > 8:
        morning_outfit.append("Light jacket or cardigan for temperature changes")
    
    return morning_outfit


def _create_evening_outfit(weather: dict, activity: str, destination: str) -> list:
    """Create evening outfit."""
    outfit = []
    
    # Evening tends to be cooler
    if weather["temp_min"] < 20:
        outfit.append("Long-sleeve shirt or light sweater")
    else:
        outfit.append("Nice shirt or blouse")
    
    # Bottoms - slightly more formal for evening
    if activity == 'business':
        outfit.append("Dress pants or formal trousers")
    elif any(x in destination for x in ['india']) and activity in ['cultural', 'religious']:
        outfit.append("Long pants or modest skirt")
    else:
        outfit.append("Nice pants or casual dress")
    
    # Evening footwear
    if activity == 'business':
        outfit.append("Dress shoes")
    else:
        outfit.append("Comfortable evening shoes or nice sandals")
    
    return outfit


def _get_activity_gear(activity: str, weather: dict) -> list:
    """Get activity-specific gear needed."""
    gear = []
    
    if activity == 'adventure':
        gear.extend(["Daypack", "Water bottle", "Comfortable hiking shoes"])
    elif activity == 'business':
        gear.extend(["Professional bag", "Business cards", "Laptop if needed"])
    elif activity in ['religious', 'cultural']:
        gear.extend(["Scarf for head covering", "Easy-to-remove shoes"])
    elif activity == 'beach':
        gear.extend(["Swimwear", "Beach towel", "Flip-flops"])
    
    # General sightseeing gear
    if activity == 'sightseeing':
        gear.extend(["Comfortable daypack", "Camera", "Water bottle"])
    
    return gear


def _get_weather_accessories(weather: dict) -> list:
    """Get weather-related accessories."""
    accessories = []
    
    if weather["temp_max"] > 28:
        accessories.extend(["Sunscreen", "Sunglasses", "Hat"])
    
    if weather["rain_chance"] > 50:
        accessories.extend(["Umbrella", "Light rain jacket"])
    
    if weather["humidity"] > 70:
        accessories.append("Extra tissues/handkerchief")
    
    return accessories


def _get_cultural_outfit_notes(destination: str, activity: str) -> str:
    """Get cultural notes for outfit choices."""
    if any(x in destination for x in ['india']):
        if activity in ['religious', 'cultural']:
            return "Modest dress required - covered shoulders and knees. Remove shoes at temples."
        else:
            return "Dress respectfully - avoid overly revealing clothing in public areas."
    
    return "Dress comfortably and appropriately for local customs."


def _get_packing_essentials(destination: str, activities: list) -> list:
    """Get essential items to pack for the trip."""
    essentials = [
        "Comfortable walking shoes",
        "Versatile pants that work for multiple occasions",
        "Light jacket or cardigan for temperature changes",
        "Sun protection (hat, sunglasses, sunscreen)"
    ]
    
    if any(x in destination for x in ['india']):
        essentials.extend([
            "Modest long-sleeve shirts",
            "Scarf or dupatta for temple visits",
            "Easy-to-remove shoes"
        ])
    
    if 'business' in activities:
        essentials.extend([
            "Professional attire",
            "Dress shoes",
            "Blazer or formal jacket"
        ])
    
    return essentials


def _get_versatile_pieces(destination: str, activities: list) -> list:
    """Get versatile pieces that work for multiple occasions."""
    return [
        "Dark jeans or pants (dress up or down)",
        "White or neutral button-down shirt",
        "Comfortable dress that works day to night",
        "Cardigan or light jacket for layering",
        "Neutral-colored scarf (warmth, style, cultural coverage)",
        "Comfortable shoes that look good with multiple outfits"
    ]
