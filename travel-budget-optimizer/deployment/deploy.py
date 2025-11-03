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

"""Deployment script for Travel Budget Optimizer & Deal Finder Agent."""

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

# This import path assumes you run the script from the 'travel-budget-optimizer' directory
from budget_optimizer_agent.agent import root_agent

from google.adk.sessions import VertexAiSessionService

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")

flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("quicktest", False, "Try a new deployment with one turn.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "quicktest"])


def create(env_vars: dict[str, str]) -> None:
    """Creates a new deployment."""
    print("Creating Travel Budget Optimizer & Deal Finder Agent deployment...")
    print(env_vars)
    
    app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
        env_vars=env_vars,
    )

    # Use relative path - assumes script is run from travel-budget-optimizer directory
    # This matches the pattern used by other agents (smart_packing_concierge, travel_concierge)
    remote_agent = agent_engines.create(  
        app,
        display_name="Travel-Budget-Optimizer-Deal-Finder-ADK",
        description="An intelligent AI agent for travel budget optimization and deal finding.",                    
        requirements=[
            "google-adk (==1.0.0)",
            "google-cloud-aiplatform[agent_engines] (==1.93.1)",
            "google-genai (==1.16.1)",
            "google-cloud-firestore (>=2.16.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
            "requests (>=2.32.3,<3.0.0)",
            "deprecated (>=1.2.14,<2.0.0)",
            "python-dotenv (>=1.0.0,<2.0.0)",
        ],
        extra_packages=[
            "./budget_optimizer_agent",  # Relative path - run script from travel-budget-optimizer directory
        ],
    )
    print(f"✅ Created Travel Budget Optimizer: {remote_agent.resource_name}")
    print(f"🎯 Use this resource ID for testing: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"🗑️ Deleted Travel Budget Optimizer: {resource_id}")


def send_message(session_service: VertexAiSessionService, resource_id: str, message: str) -> None:
    """Send a message to the deployed Budget Optimizer Agent."""

    session = asyncio.run(session_service.create_session(
            app_name=resource_id,
            user_id="budget_optimizer_user"
        )
    )

    remote_agent = agent_engines.get(resource_id)

    print(f"💰 Testing Travel Budget Optimizer: {resource_id}")
    print(f"📝 Message: {message}")
    print("=" * 60)
    
    for event in remote_agent.stream_query(
        user_id="budget_optimizer_user",
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

    # Ensure we're running from the travel-budget-optimizer directory
    # Change to parent directory if we're in deployment subdirectory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    if Path.cwd() != project_root:
        os.chdir(project_root)
        print(f"⚠️ Changed working directory to: {project_root}")

    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    print("💰 Travel Budget Optimizer & Deal Finder Agent Deployment")
    print("=" * 60)
    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")
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
        
        # Test with a budget optimization query
        test_message = "Analyze my travel spending patterns and provide optimization recommendations."
        send_message(session_service, FLAGS.resource_id, test_message)
    else:
        print("❌ Unknown command. Use --create, --delete, or --quicktest")


if __name__ == "__main__":
    app.run(main)

