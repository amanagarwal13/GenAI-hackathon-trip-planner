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

"""Tools for the cultural advisor sub-agent."""

from google.adk.tools import ToolContext


def get_cultural_guidelines(destination: str, activities: str, tool_context: ToolContext) -> dict:
    """
    Get cultural guidelines and dress codes for a destination.

    Args:
        destination: Travel destination
        activities: Planned activities (comma-separated)
        tool_context: The ADK tool context

    Returns:
        Cultural guidelines and dress code recommendations
    """
    destination_lower = destination.lower()
    activity_list = [activity.strip().lower() for activity in activities.split(',')]
    
    guidelines = {
        "destination": destination,
        "general_dress_code": [],
        "religious_site_requirements": [],
        "business_attire": [],
        "cultural_items_to_pack": [],
        "etiquette_tips": [],
        "local_customs": [],
        "color_preferences": [],
        "fabric_recommendations": []
    }
    
    # India-specific guidelines
    if any(x in destination_lower for x in ['india', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'pune', 'jaipur', 'goa', 'kerala', 'rajasthan']):
        guidelines["general_dress_code"] = [
            "Dress modestly, especially in rural areas and traditional neighborhoods",
            "Cover shoulders and knees in most public places",
            "Avoid tight-fitting or revealing clothing",
            "Light, breathable fabrics are preferred due to climate"
        ]
        
        guidelines["religious_site_requirements"] = [
            "Temples: Covered shoulders, long pants/skirts, remove shoes",
            "Gurudwaras: Head covering mandatory, remove shoes",
            "Mosques: Modest dress, head covering for women, remove shoes",
            "Churches: Respectful attire, covered shoulders recommended"
        ]
        
        guidelines["cultural_items_to_pack"] = [
            "Scarf or dupatta for head covering",
            "Long-sleeve shirts or kurtas",
            "Long pants or modest skirts",
            "Easy-to-remove shoes (slip-ons or sandals)",
            "Socks for walking on temple floors"
        ]
        
        guidelines["etiquette_tips"] = [
            "Use right hand for eating and greeting",
            "Remove shoes before entering homes and temples",
            "Greet with 'Namaste' (palms together)",
            "Ask permission before photographing people",
            "Avoid pointing feet towards people or religious objects"
        ]
        
        guidelines["local_customs"] = [
            "Bargaining is expected in markets",
            "Tipping is customary in restaurants (10-15%)",
            "Eating with hands is acceptable and common",
            "Public displays of affection should be avoided"
        ]
        
        # Regional variations
        if any(x in destination_lower for x in ['rajasthan', 'jaipur', 'udaipur']):
            guidelines["color_preferences"] = [
                "Bright colors are welcomed and appreciated",
                "Traditional Rajasthani colors (red, orange, pink) are respected",
                "Avoid all-black outfits in celebratory contexts"
            ]
            
        if any(x in destination_lower for x in ['kerala', 'goa']):
            guidelines["fabric_recommendations"] = [
                "Cotton and linen for humid coastal climate",
                "Quick-dry fabrics for monsoon season",
                "Light colors to reflect heat"
            ]
            
        if any(x in destination_lower for x in ['himachal', 'kashmir', 'ladakh']):
            guidelines["cultural_items_to_pack"].extend([
                "Warm layers for mountain temples",
                "Respectful clothing for Buddhist monasteries",
                "Sturdy shoes for mountain terrain"
            ])
    
    # Business-specific guidelines
    if 'business' in activity_list:
        guidelines["business_attire"] = [
            "Formal shirts and trousers/formal pants",
            "Blazer or suit jacket recommended",
            "Leather shoes and belt",
            "Conservative colors (navy, black, grey, white)",
            "Minimal jewelry and accessories"
        ]
    
    # Religious activity guidelines
    if any(x in activity_list for x in ['religious', 'temple', 'spiritual']):
        guidelines["religious_site_requirements"].extend([
            "Pack extra modest clothing for multiple temple visits",
            "Bring small denominations for donations",
            "Consider white or light-colored clothing for certain temples"
        ])
    
    # Festival considerations
    if any(x in activity_list for x in ['festival', 'celebration']):
        guidelines["cultural_items_to_pack"].extend([
            "Festive clothing (bright colors welcome)",
            "Traditional Indian attire if participating in celebrations",
            "Comfortable shoes for standing/walking during events"
        ])
    
    return guidelines


def validate_cultural_appropriateness(packing_list: list, destination: str, tool_context: ToolContext) -> dict:
    """
    Validate if a packing list meets cultural requirements for the destination.

    Args:
        packing_list: List of items being packed
        destination: Travel destination
        tool_context: The ADK tool context

    Returns:
        Validation results with suggestions for improvement
    """
    destination_lower = destination.lower()
    
    validation_results = {
        "is_culturally_appropriate": True,
        "missing_items": [],
        "inappropriate_items": [],
        "suggestions": [],
        "cultural_score": 100
    }
    
    # Check for essential cultural items for India
    if any(x in destination_lower for x in ['india']):
        essential_items = ['modest clothing', 'scarf', 'long pants', 'covered shoulders']
        packed_items_lower = [item.lower() for item in packing_list]
        
        for essential in essential_items:
            if not any(essential in item for item in packed_items_lower):
                validation_results["missing_items"].append(essential)
                validation_results["cultural_score"] -= 15
        
        # Check for potentially inappropriate items
        inappropriate_keywords = ['short shorts', 'tank top', 'crop top', 'mini skirt']
        for item in packing_list:
            if any(keyword in item.lower() for keyword in inappropriate_keywords):
                validation_results["inappropriate_items"].append(item)
                validation_results["cultural_score"] -= 10
    
    # Generate suggestions
    if validation_results["missing_items"]:
        validation_results["suggestions"].append("Consider adding modest clothing items for cultural sites")
    
    if validation_results["inappropriate_items"]:
        validation_results["suggestions"].append("Some items may not be appropriate for conservative areas")
    
    validation_results["is_culturally_appropriate"] = validation_results["cultural_score"] >= 70
    
    return validation_results
