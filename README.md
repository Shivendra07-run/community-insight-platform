# Community Insight Decision Platform

This repository contains the code to deploy the Community Insight Decision Platform to Google Cloud Run.

## Local Testing
To test the app locally, install the dependencies and run it via streamlit:

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your_api_key" # or set in powershell: $env:GEMINI_API_KEY="your_api_key"
streamlit run app.py
```

## Google Cloud Run Deployment Commands

Follow these steps to deploy the application directly from source using the `gcloud` CLI.

1. **Set your Google Cloud Project ID**
```bash
# Replace 'your-project-id' with your actual GCP Project ID
PROJECT_ID="your-project-id" 
gcloud config set project $PROJECT_ID
```

2. **Enable Required Google Cloud APIs**
```bash
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com
```

3. **Build and Deploy to Cloud Run**
This command builds the container using the provided `Dockerfile` and deploys it in one step.
```bash
# Replace 'your_gemini_api_key_here' with your actual Gemini API Key
gcloud run deploy community-insight-platform \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars="GEMINI_API_KEY=your_gemini_api_key_here"
```

Once deployment is complete, the CLI will output a Service URL where your application is live!
