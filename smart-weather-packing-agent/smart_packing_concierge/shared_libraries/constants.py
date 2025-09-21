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

"""Constants for the Smart Weather-Adaptive Packing Concierge."""

# Weather thresholds
COLD_TEMPERATURE_THRESHOLD = 15  # Celsius
HOT_TEMPERATURE_THRESHOLD = 30   # Celsius
HIGH_HUMIDITY_THRESHOLD = 70     # Percentage
RAIN_PROBABILITY_THRESHOLD = 50  # Percentage

# Packing categories
ESSENTIAL_CATEGORIES = ["documents", "medical", "electronics"]
WEATHER_DEPENDENT_CATEGORIES = ["clothing", "footwear", "accessories"]
CULTURAL_CATEGORIES = ["clothing", "accessories"]

# Weight estimates (in grams)
ITEM_WEIGHT_ESTIMATES = {
    "t_shirt": 150,
    "shirt": 200,
    "pants": 400,
    "jeans": 600,
    "jacket": 800,
    "sweater": 500,
    "underwear": 50,
    "socks": 30,
    "sneakers": 800,
    "boots": 1200,
    "sandals": 300,
    "phone_charger": 100,
    "laptop": 2000,
    "camera": 500,
    "toothbrush": 20,
    "sunscreen": 150,
}

# Cultural considerations by region
CULTURAL_REGIONS = {
    "india": {
        "modest_dress_required": True,
        "temple_dress_code": True,
        "shoe_removal_common": True,
        "conservative_areas": ["temples", "rural_areas", "religious_sites"]
    },
    "middle_east": {
        "modest_dress_required": True,
        "head_covering_required": True,
        "conservative_areas": ["mosques", "traditional_areas"]
    },
    "southeast_asia": {
        "modest_dress_required": True,
        "temple_dress_code": True,
        "shoe_removal_common": True
    }
}

# Climate zone characteristics
CLIMATE_CHARACTERISTICS = {
    "tropical": {
        "high_humidity": True,
        "frequent_rain": True,
        "hot_temperatures": True,
        "recommended_fabrics": ["cotton", "linen", "moisture_wicking"]
    },
    "desert": {
        "low_humidity": True,
        "extreme_temperatures": True,
        "sun_protection_critical": True,
        "recommended_fabrics": ["light_cotton", "linen"]
    },
    "monsoon": {
        "very_high_humidity": True,
        "heavy_rainfall": True,
        "waterproof_essential": True,
        "recommended_fabrics": ["quick_dry", "synthetic"]
    },
    "mountain": {
        "temperature_variation": True,
        "layering_essential": True,
        "wind_protection": True,
        "recommended_fabrics": ["wool", "fleece", "windproof"]
    }
}
