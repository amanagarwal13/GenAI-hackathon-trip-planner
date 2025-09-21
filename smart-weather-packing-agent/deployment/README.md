# Smart Weather-Adaptive Packing Concierge Deployment

This directory contains deployment scripts for deploying the Smart Weather-Adaptive Packing Concierge to Google Cloud Vertex AI Agent Engine.

## Prerequisites

1. **Google Cloud Project** with Vertex AI API enabled
2. **Google Cloud Storage Bucket** for staging
3. **Environment Variables** configured
4. **Authentication** set up (`gcloud auth application-default login`)

## Environment Setup

Create a `.env` file in the root directory with:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name

# Optional
PACKING_SCENARIO=smart_packing_concierge/profiles/default_preferences.json
OPENWEATHER_API_KEY=your-weather-api-key
GOOGLE_PLACES_API_KEY=your-places-api-key
```

## Deployment Commands

### 1. Create Deployment

Deploy the Smart Packing Concierge to Vertex AI:

```bash
# Install deployment dependencies
poetry install --with deployment

# Deploy the agent
python deployment/deploy.py --create
```

This will output a resource ID like:
```
projects/your-project/locations/us-central1/reasoningEngines/1234567890123456789
```

### 2. Test Deployment

Test the deployed agent with a sample query:

```bash
python deployment/deploy.py --quicktest --resource_id=<RESOURCE_ID>
```

Sample test query:
> "I'm traveling to Mumbai during monsoon season for business meetings and temple visits. Help me pack smartly for the weather and cultural requirements."

### 3. Delete Deployment

Remove the deployed agent:

```bash
python deployment/deploy.py --delete --resource_id=<RESOURCE_ID>
```

## Deployment Features

### Smart Packing Intelligence
The deployed agent provides:

- **🌤️ Weather Analysis**: Real-time weather-adaptive packing recommendations
- **🏛️ Cultural Guidance**: India-specific dress codes and cultural requirements
- **⚖️ Packing Optimization**: Weight, space, and efficiency strategies
- **👔 Outfit Planning**: Daily outfit recommendations with weather considerations

### Multi-Agent Architecture
The deployment includes four specialized sub-agents:

1. **Weather Analyzer Agent**: Analyzes weather patterns and conditions
2. **Cultural Advisor Agent**: Provides culturally-sensitive recommendations
3. **Packing Optimizer Agent**: Optimizes for weight, space, and efficiency
4. **Outfit Planner Agent**: Creates daily outfit plans

### Environment Variables
The deployment supports these environment variables:

- `PACKING_SCENARIO`: Path to packing preferences file
- `OPENWEATHER_API_KEY`: Weather API key for real-time data
- `GOOGLE_PLACES_API_KEY`: Places API for location intelligence

## Usage Examples

### CLI Deployment
```bash
# Create with custom settings
python deployment/deploy.py \
  --create \
  --project_id=my-project \
  --location=us-central1 \
  --bucket=my-staging-bucket \
  --packing_preferences_path=custom_preferences.json

# Quick test with specific message
python deployment/deploy.py \
  --quicktest \
  --resource_id=projects/.../reasoningEngines/123
```

### Integration with Travel Concierge

The Smart Packing Concierge can be integrated with your main Travel Concierge:

```python
# In travel_concierge/agent.py
from smart_packing_concierge.agent import root_agent as smart_packing_agent

root_agent = Agent(
    # ... existing config ...
    sub_agents=[
        inspiration_agent,
        planning_agent,
        booking_agent,
        # ... other agents ...
        smart_packing_agent,  # Add packing intelligence!
    ],
)
```

## Monitoring and Logs

- **Vertex AI Console**: Monitor agent performance and usage
- **Cloud Logging**: View detailed execution logs
- **Tracing**: Enabled by default for debugging

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```
   ❌ Missing required environment variable: GOOGLE_CLOUD_PROJECT
   ```
   Solution: Set all required environment variables in `.env`

2. **Authentication Errors**
   ```
   ❌ Permission denied
   ```
   Solution: Run `gcloud auth application-default login`

3. **Bucket Access Issues**
   ```
   ❌ Cannot access staging bucket
   ```
   Solution: Ensure bucket exists and you have write permissions

### Debug Mode

Enable detailed logging:
```bash
export GOOGLE_CLOUD_LOG_LEVEL=DEBUG
python deployment/deploy.py --create
```

## Production Considerations

- **Resource Limits**: Monitor usage and set appropriate quotas
- **Security**: Use IAM roles with minimal required permissions
- **Scaling**: Agent Engine automatically scales based on demand
- **Cost Optimization**: Monitor usage patterns and optimize accordingly

---

**🚀 Your Smart Weather-Adaptive Packing Concierge is ready for production deployment!**
