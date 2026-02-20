#!/bin/bash

# TalentHunt Backend Deployment Script for Google Cloud Run
# Usage: ./deploy_gcp.sh

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="us-central1"
SERVICE_NAME="talenthunt-backend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
# Railway Public TCP Proxy Connection String (from previous context)
# NOTE: Ensure the TCP Proxy feature is enabled for your PostgreSQL service on Railway!
DATABASE_URL="postgresql+asyncpg://postgres:OJnYuzsNIXpJXdCJotkfjvrFSTLOkflj@shuttle.proxy.rlwy.net:56190/railway"

# --- Checks ---
if [ -z "$PROJECT_ID" ]; then
  echo "❌ Error: Could not determine Google Cloud Project ID."
  echo "👉 Please run 'gcloud init' or 'gcloud config set project <YOUR_PROJECT_ID>' first."
  exit 1
fi

echo "🚀 Deploying TalentHunt Backend to Google Cloud Run"
echo "   Project: $PROJECT_ID"
echo "   Region:  $REGION"
echo "   Service: $SERVICE_NAME"
echo ""

# --- 1. Enable APIs ---
echo "🔹 Enabling necessary Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
echo "✅ APIs enabled."

# --- 2. Build & Push Docker Image ---
echo "🔹 Building and pushing Docker image to GCR..."
gcloud builds submit --tag "$IMAGE_NAME" .
echo "✅ Image built and pushed: $IMAGE_NAME"

# --- 3. Deploy to Cloud Run ---
echo "🔹 Deploying container to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_NAME" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "DATABASE_URL=$DATABASE_URL" \
  --set-env-vars "JWT_SECRET_KEY=dev-secret-key-change-in-production" \
  --set-env-vars "JWT_ALGORITHM=HS256" \
  --set-env-vars "JWT_EXPIRATION_MINUTES=1440" \
  --set-env-vars "BACKEND_CORS_ORIGINS=https://frontend-six-gilt-39.vercel.app,http://localhost:3000" \
  --set-env-vars "API_PREFIX=/api/v1"

echo ""
echo "✅ Deployment Complete!"
echo "👇 Your Backend URL is listed above in the 'Service URL' line."
echo "📋 Please copy this URL and provide it to me so I can update the Frontend configuration."
