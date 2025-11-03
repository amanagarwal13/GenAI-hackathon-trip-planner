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

"""Firestore persistence tools for itineraries."""

from datetime import datetime
from typing import Optional, Dict, Any
import json

from google.adk.tools import ToolContext

# Try to import firestore, but don't fail if not available
try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    firestore = None  # Set to None to avoid NameError


def save_itinerary_to_firestore(tool_context: ToolContext) -> dict:
    """
    Save the current itinerary to Firestore.

    Args:
        tool_context: The ADK tool context containing the itinerary in state

    Returns:
        A status message indicating success or failure
    """
    if not FIRESTORE_AVAILABLE or firestore is None:
        return {
            "status": "error",
            "message": "Firestore not available. Please install google-cloud-firestore package."
        }

    itinerary = tool_context.state.get('itinerary')
    if not itinerary:
        return {
            "status": "error",
            "message": "No itinerary found in the current state to save."
        }

    # Get user_id from state or use default
    user_id = tool_context.state.get('user_id', 'default_user')

    try:
        db = firestore.Client()
        doc_ref = db.collection("itineraries").document(user_id)
        
        # Check if document exists to preserve created_at
        doc = doc_ref.get()
        
        # Prepare data to save
        itinerary_data = {
            "itinerary": itinerary,
            "user_id": user_id,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        
        # Set created_at only if document doesn't exist
        if not doc.exists:
            itinerary_data["created_at"] = firestore.SERVER_TIMESTAMP
        
        # Merge to preserve other fields if updating
        doc_ref.set(itinerary_data, merge=True)
        
        # Also update session state to mark as persisted
        tool_context.state["itinerary_persisted"] = True
        tool_context.state["itinerary_firestore_id"] = user_id
        
        return {
            "status": "success",
            "message": f"Itinerary saved successfully for user {user_id}",
            "user_id": user_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save itinerary to Firestore: {str(e)}"
        }


def load_itinerary_from_firestore(user_id: str, tool_context: ToolContext) -> dict:
    """
    Load a saved itinerary from Firestore.

    Args:
        user_id: The user ID to load the itinerary for
        tool_context: The ADK tool context to populate with the itinerary

    Returns:
        A status message with the loaded itinerary or error
    """
    if not FIRESTORE_AVAILABLE or firestore is None:
        return {
            "status": "error",
            "message": "Firestore not available. Please install google-cloud-firestore package."
        }

    try:
        db = firestore.Client()
        doc_ref = db.collection("itineraries").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {
                "status": "not_found",
                "message": f"No saved itinerary found for user {user_id}"
            }
        
        data = doc.to_dict()
        itinerary = data.get("itinerary")
        
        if itinerary:
            # Load itinerary into session state
            tool_context.state["itinerary"] = itinerary
            tool_context.state["itinerary_persisted"] = True
            tool_context.state["itinerary_firestore_id"] = user_id
            
            return {
                "status": "success",
                "message": f"Itinerary loaded successfully for user {user_id}",
                "itinerary": itinerary
            }
        else:
            return {
                "status": "error",
                "message": "Itinerary document exists but contains no itinerary data"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load itinerary from Firestore: {str(e)}"
        }


def delete_itinerary_from_firestore(user_id: str, tool_context: ToolContext) -> dict:
    """
    Delete a saved itinerary from Firestore.

    Args:
        user_id: The user ID whose itinerary should be deleted
        tool_context: The ADK tool context

    Returns:
        A status message indicating success or failure
    """
    if not FIRESTORE_AVAILABLE or firestore is None:
        return {
            "status": "error",
            "message": "Firestore not available. Please install google-cloud-firestore package."
        }

    try:
        db = firestore.Client()
        doc_ref = db.collection("itineraries").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {
                "status": "not_found",
                "message": f"No saved itinerary found for user {user_id}"
            }
        
        doc_ref.delete()
        
        # Clear from session state
        if "itinerary_persisted" in tool_context.state:
            del tool_context.state["itinerary_persisted"]
        if "itinerary_firestore_id" in tool_context.state:
            del tool_context.state["itinerary_firestore_id"]
        
        return {
            "status": "success",
            "message": f"Itinerary deleted successfully for user {user_id}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete itinerary from Firestore: {str(e)}"
        }


def save_itinerary_to_firestore(tool_context: ToolContext) -> dict:
    """
    Save the current itinerary to Firestore.

    Args:
        tool_context: The ADK tool context containing the itinerary in state

    Returns:
        A status message indicating success or failure
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Please install google-cloud-firestore package."
        }

    itinerary = tool_context.state.get('itinerary')
    if not itinerary:
        return {
            "status": "error",
            "message": "No itinerary found in the current state to save."
        }

    # Get user_id from state or use default
    user_id = tool_context.state.get('user_id', 'default_user')

    try:
        db = firestore.Client()
        doc_ref = db.collection("itineraries").document(user_id)
        
        # Check if document exists to preserve created_at
        doc = doc_ref.get()
        
        # Prepare data to save
        itinerary_data = {
            "itinerary": itinerary,
            "user_id": user_id,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        
        # Set created_at only if document doesn't exist
        if not doc.exists:
            itinerary_data["created_at"] = firestore.SERVER_TIMESTAMP
        
        # Merge to preserve other fields if updating
        doc_ref.set(itinerary_data, merge=True)
        
        # Also update session state to mark as persisted
        tool_context.state["itinerary_persisted"] = True
        tool_context.state["itinerary_firestore_id"] = user_id
        
        return {
            "status": "success",
            "message": f"Itinerary saved successfully for user {user_id}",
            "user_id": user_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save itinerary to Firestore: {str(e)}"
        }


def load_itinerary_from_firestore(user_id: str, tool_context: ToolContext) -> dict:
    """
    Load a saved itinerary from Firestore.

    Args:
        user_id: The user ID to load the itinerary for
        tool_context: The ADK tool context to populate with the itinerary

    Returns:
        A status message with the loaded itinerary or error
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Please install google-cloud-firestore package."
        }

    try:
        db = firestore.Client()
        doc_ref = db.collection("itineraries").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {
                "status": "not_found",
                "message": f"No saved itinerary found for user {user_id}"
            }
        
        data = doc.to_dict()
        itinerary = data.get("itinerary")
        
        if itinerary:
            # Load itinerary into session state
            tool_context.state["itinerary"] = itinerary
            tool_context.state["itinerary_persisted"] = True
            tool_context.state["itinerary_firestore_id"] = user_id
            
            return {
                "status": "success",
                "message": f"Itinerary loaded successfully for user {user_id}",
                "itinerary": itinerary
            }
        else:
            return {
                "status": "error",
                "message": "Itinerary document exists but contains no itinerary data"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load itinerary from Firestore: {str(e)}"
        }


def delete_itinerary_from_firestore(user_id: str, tool_context: ToolContext) -> dict:
    """
    Delete a saved itinerary from Firestore.

    Args:
        user_id: The user ID whose itinerary should be deleted
        tool_context: The ADK tool context

    Returns:
        A status message indicating success or failure
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Please install google-cloud-firestore package."
        }

    try:
        db = firestore.Client()
        doc_ref = db.collection("itineraries").document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {
                "status": "not_found",
                "message": f"No saved itinerary found for user {user_id}"
            }
        
        doc_ref.delete()
        
        # Clear from session state
        if "itinerary_persisted" in tool_context.state:
            del tool_context.state["itinerary_persisted"]
        if "itinerary_firestore_id" in tool_context.state:
            del tool_context.state["itinerary_firestore_id"]
        
        return {
            "status": "success",
            "message": f"Itinerary deleted successfully for user {user_id}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete itinerary from Firestore: {str(e)}"
        }

