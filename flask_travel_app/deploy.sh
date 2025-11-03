#!/bin/bash

# Flask Travel App - Cloud Run Deployment Script
# This script deploys the Flask travel app to Google Cloud Run with proper environment variables

# Configuration
PROJECT_ID="56426154949"
LOCATION="us-central1"
SERVICE_NAME="flask-travel-app"
AGENT_RESOURCE_ID="projects/56426154949/locations/us-central1/reasoningEngines/14940163998220288"

echo "🚀 Deploying Flask Travel App to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Location: $LOCATION"
echo "   Service: $SERVICE_NAME"

# Build and deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$LOCATION,AGENT_RESOURCE_ID=$AGENT_RESOURCE_ID,GCP_PROJECT=$PROJECT_ID,GCP_LOCATION=$LOCATION" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=3600 \
    --max-instances=10 \
    --port=8080

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your app should be available at the URL shown above"
    echo ""
    echo "📋 Environment variables set:"
    echo "   GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
    echo "   GOOGLE_CLOUD_LOCATION=$LOCATION"
    echo "   AGENT_RESOURCE_ID=$AGENT_RESOURCE_ID"
    echo "   GCP_PROJECT=$PROJECT_ID"
    echo "   GCP_LOCATION=$LOCATION"
else
    echo "❌ Deployment failed!"
    exit 1
fi






