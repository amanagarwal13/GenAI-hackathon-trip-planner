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

"""Tools for the packing optimizer sub-agent."""

from google.adk.tools import ToolContext


def analyze_packing_efficiency(packing_list: str, trip_duration: int, destination: str, tool_context: ToolContext) -> dict:
    """
    Analyze the efficiency of a packing list and identify optimization opportunities.

    Args:
        packing_list: Comma-separated list of items being packed
        trip_duration: Length of trip in days
        destination: Travel destination
        tool_context: The ADK tool context

    Returns:
        Analysis of packing efficiency with metrics and insights
    """
    items = [item.strip() for item in packing_list.split(',')]
    
    # Weight estimation based on common items
    weight_estimates = {
        't-shirt': 150, 'shirt': 200, 'pants': 400, 'jeans': 600, 'jacket': 800,
        'sweater': 500, 'underwear': 50, 'socks': 30, 'sneakers': 800, 'boots': 1200,
        'sandals': 300, 'phone charger': 100, 'laptop': 2000, 'camera': 500,
        'toothbrush': 20, 'sunscreen': 150, 'book': 300, 'umbrella': 400
    }
    
    analysis = {
        "total_items": len(items),
        "estimated_weight_kg": 0,
        "efficiency_score": 100,
        "optimization_opportunities": [],
        "weight_breakdown": {},
        "space_efficiency": "good",
        "redundancy_issues": [],
        "missing_essentials": []
    }
    
    # Calculate estimated weight
    total_weight_grams = 0
    category_weights = {}
    
    for item in items:
        item_lower = item.lower()
        estimated_weight = 0
        
        # Match item to weight estimate
        for key, weight in weight_estimates.items():
            if key in item_lower:
                estimated_weight = weight
                break
        
        if estimated_weight == 0:
            # Default estimates by category
            if any(x in item_lower for x in ['clothing', 'shirt', 'pants']):
                estimated_weight = 200
            elif any(x in item_lower for x in ['electronics', 'charger', 'device']):
                estimated_weight = 150
            elif any(x in item_lower for x in ['shoes', 'footwear']):
                estimated_weight = 600
            else:
                estimated_weight = 100
        
        total_weight_grams += estimated_weight
        
        # Categorize for analysis
        category = _categorize_item(item_lower)
        if category not in category_weights:
            category_weights[category] = 0
        category_weights[category] += estimated_weight
    
    analysis["estimated_weight_kg"] = round(total_weight_grams / 1000, 2)
    analysis["weight_breakdown"] = {k: round(v/1000, 2) for k, v in category_weights.items()}
    
    # Analyze efficiency
    items_per_day = len(items) / trip_duration
    if items_per_day > 8:
        analysis["efficiency_score"] -= 20
        analysis["optimization_opportunities"].append("Consider reducing items - packing more than 8 items per day")
    
    # Check for heavy items
    if analysis["estimated_weight_kg"] > 20:
        analysis["efficiency_score"] -= 15
        analysis["optimization_opportunities"].append("Total weight exceeds 20kg - consider lighter alternatives")
    
    # Check for redundancy
    clothing_items = [item for item in items if any(x in item.lower() for x in ['shirt', 'pants', 'jacket'])]
    if len(clothing_items) > trip_duration * 1.5:
        analysis["redundancy_issues"].append("Excessive clothing items for trip duration")
        analysis["efficiency_score"] -= 10
    
    # Check for essentials
    essential_categories = ['documents', 'charger', 'toiletries', 'medication']
    packed_categories = set(_categorize_item(item.lower()) for item in items)
    
    for essential in essential_categories:
        if essential not in packed_categories:
            analysis["missing_essentials"].append(essential)
            analysis["efficiency_score"] -= 5
    
    # Space efficiency assessment
    if len(items) > 50:
        analysis["space_efficiency"] = "poor"
    elif len(items) > 30:
        analysis["space_efficiency"] = "moderate"
    
    return analysis


def suggest_optimizations(current_analysis: dict, destination: str, trip_type: str, tool_context: ToolContext) -> dict:
    """
    Suggest specific optimizations based on packing analysis.

    Args:
        current_analysis: Results from analyze_packing_efficiency
        destination: Travel destination
        trip_type: Type of trip (business, leisure, adventure)
        tool_context: The ADK tool context

    Returns:
        Specific optimization recommendations
    """
    optimizations = {
        "weight_reduction": [],
        "space_saving": [],
        "multi_purpose_items": [],
        "local_purchase_suggestions": [],
        "packing_techniques": [],
        "estimated_savings": {
            "weight_kg": 0,
            "space_percent": 0
        }
    }
    
    # Weight reduction suggestions
    if current_analysis.get("estimated_weight_kg", 0) > 15:
        optimizations["weight_reduction"] = [
            "Replace heavy jeans with lighter travel pants (save ~200g per pair)",
            "Choose lightweight, quick-dry fabrics over cotton",
            "Limit shoes to 2 pairs maximum (wear heaviest while traveling)",
            "Use travel-size toiletries or solid alternatives",
            "Consider leaving laptop if not essential (save ~2kg)"
        ]
        optimizations["estimated_savings"]["weight_kg"] = 2.5
    
    # Space saving suggestions
    optimizations["space_saving"] = [
        "Roll clothes instead of folding (save 30% space)",
        "Use packing cubes for organization and compression",
        "Wear heaviest items (boots, jacket) while traveling",
        "Pack socks and underwear inside shoes",
        "Use compression bags for bulky items"
    ]
    optimizations["estimated_savings"]["space_percent"] = 25
    
    # Multi-purpose items
    optimizations["multi_purpose_items"] = [
        "Sarong: towel, blanket, scarf, cover-up",
        "Smartphone: camera, map, translator, entertainment",
        "Bandana: headband, face mask, towel, first aid",
        "Duct tape: repairs, first aid, gear fixes",
        "Safety pins: clothing repairs, gear fixes"
    ]
    
    # Destination-specific local purchase suggestions
    destination_lower = destination.lower()
    if any(x in destination_lower for x in ['india']):
        optimizations["local_purchase_suggestions"] = [
            "Cotton clothing: Better quality and prices in India",
            "Ayurvedic toiletries: Authentic and affordable locally",
            "Traditional clothing: Kurtas, sarees for cultural experiences",
            "Comfortable sandals: Designed for local climate",
            "Spices and tea: Fresh from source for gifts"
        ]
    else:
        optimizations["local_purchase_suggestions"] = [
            "Basic toiletries: Available everywhere, save space",
            "Casual clothing: Often cheaper at destination",
            "Souvenirs: Better selection and prices locally",
            "Adapters and cables: Widely available"
        ]
    
    # Trip-type specific suggestions
    if trip_type.lower() == 'business':
        optimizations["packing_techniques"].extend([
            "Pack one complete outfit in carry-on",
            "Use garment folder for wrinkle-free formal wear",
            "Limit to 2 pairs of dress shoes maximum"
        ])
    elif trip_type.lower() == 'leisure':
        optimizations["packing_techniques"].extend([
            "Pack versatile pieces that mix and match",
            "Bring comfortable walking shoes as priority",
            "Leave space for souvenirs (pack 80% full)"
        ])
    
    # General packing techniques
    optimizations["packing_techniques"].extend([
        "Use the 'one week rule': pack for one week, do laundry as needed",
        "Stick to 2-3 color palette for easy mixing",
        "Pack items inside other items (chargers in shoes, etc.)",
        "Use every pocket and compartment efficiently"
    ])
    
    return optimizations


def _categorize_item(item_lower: str) -> str:
    """Categorize an item for analysis purposes."""
    if any(x in item_lower for x in ['shirt', 'pants', 'jacket', 'dress', 'clothing']):
        return 'clothing'
    elif any(x in item_lower for x in ['shoes', 'boots', 'sandals', 'footwear']):
        return 'footwear'
    elif any(x in item_lower for x in ['charger', 'phone', 'laptop', 'camera', 'electronics']):
        return 'electronics'
    elif any(x in item_lower for x in ['toothbrush', 'shampoo', 'soap', 'toiletries']):
        return 'toiletries'
    elif any(x in item_lower for x in ['passport', 'documents', 'tickets']):
        return 'documents'
    elif any(x in item_lower for x in ['medication', 'medicine', 'pills']):
        return 'medical'
    else:
        return 'accessories'
