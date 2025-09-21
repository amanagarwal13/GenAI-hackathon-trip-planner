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

"""Deployment script for Smart Weather-Adaptive Packing Concierge."""

import asyncio
import os
import sys
from pathlib import Path

from absl import app, flags
from dotenv import load_dotenv

# Add the parent directory to Python path to enable imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# This import path assumes you run the script from the 'smart-weather-packing-agent' directory
from smart_packing_concierge.agent import root_agent

from google.adk.sessions import VertexAiSessionService

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")

flags.DEFINE_string(
    "packing_preferences_path",
    None,
    "Relative path to the packing preferences file, e.g. smart_packing_concierge/profiles/default_preferences.json",
)
flags.DEFINE_string("weather_api_key", None, "API Key for Weather Services")
flags.DEFINE_string("places_api_key", None, "API Key for Google Places API")

flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("quicktest", False, "Try a new deployment with one turn.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "quicktest"])


def create(env_vars: dict[str, str]) -> None:
    """Creates a new deployment."""
    print("Creating Smart Weather-Adaptive Packing Concierge deployment...")
    print(env_vars)
    
    app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=env_vars,
    )

    remote_agent = agent_engines.create(  
        app,
        display_name="Smart-Weather-Adaptive-Packing-Concierge-ADK",
        description="An intelligent AI agent for weather-adaptive, culturally-sensitive travel packing recommendations.",                    
        requirements=[
            "google-adk (==1.0.0)",
            "google-cloud-aiplatform[agent_engines] (==1.93.1)",
            "google-genai (==1.16.1)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
            "requests (>=2.32.3,<3.0.0)",
            "deprecated (>=1.2.14,<2.0.0)",
            "python-dotenv (>=1.0.0,<2.0.0)",
        ],
        extra_packages=[
            "./smart_packing_concierge",  # The main package
        ],
    )
    print(f"✅ Created Smart Packing Concierge: {remote_agent.resource_name}")
    print(f"🎯 Use this resource ID for testing: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"🗑️ Deleted Smart Packing Concierge: {resource_id}")


def send_message(session_service: VertexAiSessionService, resource_id: str, message: str) -> None:
    """Send a message to the deployed Smart Packing Concierge."""

    session = asyncio.run(session_service.create_session(
            app_name=resource_id,
            user_id="smart_packer_user"
        )
    )

    remote_agent = agent_engines.get(resource_id)

    print(f"🧳 Testing Smart Packing Concierge: {resource_id}")
    print(f"📝 Message: {message}")
    print("=" * 60)
    
    for event in remote_agent.stream_query(
        user_id="smart_packer_user",
        session_id=session.id,
        message=message,
    ):
        print(event)
    print("=" * 60)
    print("✅ Test completed successfully!")


def main(argv: list[str]) -> None:
    """Main deployment function."""

    load_dotenv()
    env_vars = {}

    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    
    # Variables for Smart Packing Concierge from .env
    packing_preferences_path = (
        FLAGS.packing_preferences_path
        if FLAGS.packing_preferences_path
        else os.getenv("PACKING_SCENARIO")
    )
    if packing_preferences_path:
        env_vars["PACKING_SCENARIO"] = packing_preferences_path
    
    weather_api_key = (
        FLAGS.weather_api_key
        if FLAGS.weather_api_key
        else os.getenv("OPENWEATHER_API_KEY")
    )
    if weather_api_key:
        env_vars["OPENWEATHER_API_KEY"] = weather_api_key
    
    places_api_key = (
        FLAGS.places_api_key
        if FLAGS.places_api_key
        else os.getenv("GOOGLE_PLACES_API_KEY")
    )
    if places_api_key:
        env_vars["GOOGLE_PLACES_API_KEY"] = places_api_key

    print("🧳 Smart Weather-Adaptive Packing Concierge Deployment")
    print("=" * 60)
    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")
    print(f"PACKING_PREFERENCES: {packing_preferences_path}")
    print(f"WEATHER_API: {'***' + weather_api_key[-5:] if weather_api_key else 'Not set'}")
    print(f"PLACES_API: {'***' + places_api_key[-5:] if places_api_key else 'Not set'}")
    print("=" * 60)

    if not project_id:
        print("❌ Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("❌ Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("❌ Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.create:
        create(env_vars)
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("❌ resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.quicktest:
        if not FLAGS.resource_id:
            print("❌ resource_id is required for quicktest")
            return
        session_service = VertexAiSessionService(project_id, location)
        
        # Test with a smart packing query
        test_message = "I'm traveling to Mumbai during monsoon season for business meetings and temple visits. Help me pack smartly for the weather and cultural requirements."
        send_message(session_service, FLAGS.resource_id, test_message)
    else:
        print("❌ Unknown command. Use --create, --delete, or --quicktest")


if __name__ == "__main__":
    app.run(main)
