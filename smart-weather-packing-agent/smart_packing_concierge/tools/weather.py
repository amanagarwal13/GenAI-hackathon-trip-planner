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

"""Weather-related tools for the Smart Packing Concierge."""

from google.adk.tools import ToolContext
from datetime import datetime, timedelta
import random


def get_weather_forecast(destination: str, start_date: str, end_date: str, tool_context: ToolContext) -> dict:
    """
    Get detailed weather forecast for the travel destination and dates.

    Args:
        destination: Travel destination
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD)
        tool_context: The ADK tool context

    Returns:
        Detailed weather forecast information
    """
    # Mock weather data based on destination and season
    base_temp = _get_base_temperature(destination)
    climate_zone = _determine_climate_zone(destination)
    
    # Parse dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    
    forecast_days = []
    current_date = start
    
    while current_date <= end:
        # Generate realistic weather variation
        temp_variation = 5
        min_temp = base_temp - temp_variation + (current_date.day % 3)
        max_temp = base_temp + temp_variation + (current_date.day % 4)
        
        # Seasonal adjustments
        month = current_date.month
        if month in [12, 1, 2]:  # Winter
            min_temp -= 5
            max_temp -= 3
        elif month in [6, 7, 8, 9] and "india" in destination.lower():  # Monsoon
            min_temp += 2
            max_temp -= 2
        
        day_forecast = {
            "date": current_date.strftime("%Y-%m-%d"),
            "temperature_min": round(min_temp, 1),
            "temperature_max": round(max_temp, 1),
            "humidity": 60 + (current_date.day % 30),
            "precipitation_chance": _get_precipitation_chance(destination, month),
            "weather_description": _get_weather_description(destination, month, current_date.day),
            "wind_speed": 10 + (current_date.day % 15),
            "uv_index": max(1, min(11, 6 + (current_date.day % 6)))
        }
        
        forecast_days.append(day_forecast)
        current_date += timedelta(days=1)
    
    return {
        "location": destination,
        "forecast_days": forecast_days,
        "climate_zone": climate_zone,
        "seasonal_notes": _get_seasonal_notes(destination, start.month),
        "packing_implications": _get_packing_implications(forecast_days, climate_zone)
    }


def _get_base_temperature(destination: str) -> float:
    """Get base temperature for destination."""
    destination_lower = destination.lower()
    
    # Indian cities temperature mapping
    temp_map = {
        'mumbai': 28, 'delhi': 25, 'bangalore': 22, 'chennai': 30,
        'kolkata': 27, 'hyderabad': 26, 'pune': 24, 'jaipur': 26,
        'goa': 29, 'kerala': 28, 'rajasthan': 30, 'himachal': 15,
        'kashmir': 10, 'ladakh': 5, 'manali': 12, 'shimla': 15,
        'darjeeling': 18, 'ooty': 20, 'kodaikanal': 19
    }
    
    for city, temp in temp_map.items():
        if city in destination_lower:
            return temp
    
    return 25  # Default temperature


def _determine_climate_zone(destination: str) -> str:
    """Determine climate zone based on destination."""
    destination_lower = destination.lower()
    
    if any(x in destination_lower for x in ['mumbai', 'goa', 'kerala', 'chennai']):
        return "coastal"
    elif any(x in destination_lower for x in ['rajasthan', 'jaipur', 'jodhpur']):
        return "desert"
    elif any(x in destination_lower for x in ['himachal', 'kashmir', 'ladakh', 'manali']):
        return "mountain"
    elif any(x in destination_lower for x in ['mumbai', 'kolkata']):
        return "monsoon"
    else:
        return "temperate"


def _get_precipitation_chance(destination: str, month: int) -> int:
    """Get precipitation chance based on destination and month."""
    destination_lower = destination.lower()
    
    # Monsoon season in India
    if month in [6, 7, 8, 9] and any(x in destination_lower for x in ['mumbai', 'kerala', 'goa']):
        return 70 + random.randint(-10, 20)
    elif month in [12, 1, 2]:  # Winter - less rain
        return 10 + random.randint(0, 20)
    else:
        return 30 + random.randint(-10, 30)


def _get_weather_description(destination: str, month: int, day: int) -> str:
    """Get weather description based on location and season."""
    destination_lower = destination.lower()
    
    # Monsoon season
    if month in [6, 7, 8, 9] and any(x in destination_lower for x in ['mumbai', 'kerala']):
        descriptions = ["Heavy Rain", "Light Rain", "Cloudy", "Partly Cloudy"]
        return descriptions[day % 4]
    
    # Desert regions
    elif any(x in destination_lower for x in ['rajasthan', 'jaipur']):
        descriptions = ["Sunny", "Clear", "Hot", "Partly Cloudy"]
        return descriptions[day % 4]
    
    # Mountain regions
    elif any(x in destination_lower for x in ['himachal', 'kashmir']):
        descriptions = ["Clear", "Cloudy", "Light Snow", "Partly Cloudy"]
        return descriptions[day % 4]
    
    # Default
    descriptions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]
    return descriptions[day % 4]


def _get_seasonal_notes(destination: str, month: int) -> str:
    """Get seasonal notes for the destination."""
    destination_lower = destination.lower()
    
    if month in [6, 7, 8, 9]:  # Monsoon season
        if any(x in destination_lower for x in ['mumbai', 'kerala', 'goa']):
            return "Monsoon season - expect heavy rainfall and high humidity. Waterproof items essential."
    elif month in [12, 1, 2]:  # Winter
        if any(x in destination_lower for x in ['delhi', 'rajasthan', 'himachal']):
            return "Winter season - temperatures can drop significantly, especially at night. Layer clothing recommended."
    elif month in [3, 4, 5]:  # Summer
        if any(x in destination_lower for x in ['rajasthan', 'delhi']):
            return "Summer season - very hot and dry. Light, breathable clothing and sun protection essential."
    
    return "Pleasant weather expected for most of the trip."


def _get_packing_implications(forecast_days: list, climate_zone: str) -> list:
    """Get packing implications based on weather forecast."""
    implications = []
    
    # Temperature analysis
    max_temp = max(day["temperature_max"] for day in forecast_days)
    min_temp = min(day["temperature_min"] for day in forecast_days)
    
    if max_temp > 30:
        implications.append("Pack light, breathable clothing for hot weather")
        implications.append("Sunscreen and hat essential for UV protection")
    
    if min_temp < 15:
        implications.append("Pack warm layers for cold temperatures")
        implications.append("Jacket or sweater recommended for evenings")
    
    # Rain analysis
    rainy_days = sum(1 for day in forecast_days if day["precipitation_chance"] > 50)
    if rainy_days > 2:
        implications.append("Waterproof clothing and umbrella necessary")
        implications.append("Quick-dry fabrics recommended")
    
    # Humidity analysis
    avg_humidity = sum(day["humidity"] for day in forecast_days) / len(forecast_days)
    if avg_humidity > 70:
        implications.append("Moisture-wicking fabrics recommended for high humidity")
        implications.append("Extra underwear and socks for frequent changes")
    
    return implications
