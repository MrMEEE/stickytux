#!/bin/bash

# StickyTux OpenShift Deployment Script
# This script automates the deployment of StickyTux to OpenShift
# 
# Features:
# - Auto-detects OpenShift cluster domain
# - Dynamically generates CORS and CSRF configurations
# - Configures storage classes
# - Builds and deploys both frontend and backend
# 
# Usage: ./deploy.sh [PROJECT_NAME] [GITHUB_REPO]

set -e

PROJECT_NAME=${1:-stickytux}
GITHUB_REPO=${2:-https://github.com/MrMEEE/stickytux.git}

# Determine the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

echo "🚀 Deploying StickyTux to OpenShift"
echo "Project: $PROJECT_NAME"
echo "Repository: $GITHUB_REPO"
echo "Script location: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo ""

# Ask for storage class
echo "📦 Storage Configuration"
echo "Available storage classes:"
oc get storageclass --no-headers | awk '{print "  - " $1 " (" $2 ")"}'
echo ""
read -p "Enter storage class name (or press Enter for default): " STORAGE_CLASS

if [ -n "$STORAGE_CLASS" ]; then
    echo "Using storage class: $STORAGE_CLASS"
else
    echo "Using default storage class"
fi
echo ""

# Check if oc is installed
if ! command -v oc &> /dev/null; then
    echo "❌ OpenShift CLI (oc) is not installed"
    exit 1
fi

# Check if logged in
if ! oc whoami &> /dev/null; then
    echo "❌ Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

# Create project if it doesn't exist
echo "📁 Creating/switching to project: $PROJECT_NAME"
oc new-project $PROJECT_NAME 2>/dev/null || oc project $PROJECT_NAME

# Update GitHub repository URL in build configs if provided
if [ "$GITHUB_REPO" != "https://github.com/MrMEEE/stickytux.git" ]; then
    echo "🔧 Updating repository URL to: $GITHUB_REPO"
    sed -i "s|uri: https://github.com/MrMEEE/stickytux.git|uri: $GITHUB_REPO|g" "$SCRIPT_DIR/backend-buildconfig.yaml"
    sed -i "s|uri: https://github.com/MrMEEE/stickytux.git|uri: $GITHUB_REPO|g" "$SCRIPT_DIR/frontend-buildconfig.yaml"
fi

echo "🏗️  Creating ImageStreams..."
oc apply -f "$SCRIPT_DIR/imagestreams.yaml"

echo "🔐 Creating ConfigMap and Secrets..."

# Auto-detect OpenShift cluster domain
CLUSTER_DOMAIN=$(oc get routes -n openshift-console console -o jsonpath='{.spec.host}' | sed 's/^console-openshift-console\.//')
if [ -z "$CLUSTER_DOMAIN" ]; then
    echo "⚠️  Could not auto-detect cluster domain, using default apps.okd.outerrim.lan"
    CLUSTER_DOMAIN="apps.okd.outerrim.lan"
fi

echo "🌐 Detected cluster domain: $CLUSTER_DOMAIN"

# Generate dynamic CORS and CSRF URLs
FRONTEND_URL="https://$PROJECT_NAME-frontend-$PROJECT_NAME.$CLUSTER_DOMAIN"
BACKEND_URL="https://$PROJECT_NAME-backend-$PROJECT_NAME.$CLUSTER_DOMAIN"

echo "🔧 Configuring URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend: $BACKEND_URL"

# Create dynamic ConfigMap
cat > "/tmp/configmap-dynamic.yaml" << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: stickytux-config
  labels:
    app: stickytux
data:
  DJANGO_SETTINGS_MODULE: "backend.settings"
  WEB_CONCURRENCY: "4"
  NODE_ENV: "production"
  
  # CORS Configuration - dynamically generated
  CORS_ALLOWED_ORIGINS: "$FRONTEND_URL,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174"
  CORS_ALLOW_ALL_ORIGINS: "true"
  CORS_ALLOW_CREDENTIALS: "true"
  
  # CSRF Configuration - dynamically generated
  CSRF_TRUSTED_ORIGINS: "$FRONTEND_URL,$BACKEND_URL,https://*.$CLUSTER_DOMAIN,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174"
  
  # Django Configuration
  ALLOWED_HOSTS: "*"
  DEBUG: "false"
  
  # Frontend URL for dynamic CORS
  FRONTEND_URL: "$FRONTEND_URL"
EOF

oc apply -f "/tmp/configmap-dynamic.yaml"
rm "/tmp/configmap-dynamic.yaml"

oc apply -f "$SCRIPT_DIR/secrets.yaml"

echo "💾 Creating Persistent Volume Claims..."
# Apply storage class to PVCs if specified
if [ -n "$STORAGE_CLASS" ]; then
    echo "Setting storage class to: $STORAGE_CLASS"
    # Create temporary PVC files with storage class
    sed "s/# storageClassName will be set by deployment script/storageClassName: $STORAGE_CLASS/" "$SCRIPT_DIR/pvc.yaml" > "/tmp/pvc-with-storage.yaml"
    oc apply -f "/tmp/pvc-with-storage.yaml"
    rm "/tmp/pvc-with-storage.yaml"
else
    oc apply -f "$SCRIPT_DIR/pvc.yaml"
fi

echo "🛠️  Creating BuildConfigs..."
oc apply -f "$SCRIPT_DIR/backend-buildconfig.yaml"
oc apply -f "$SCRIPT_DIR/frontend-buildconfig.yaml"

echo "🔨 Starting builds..."
oc start-build stickytux-backend-build
oc start-build stickytux-frontend-build

echo "⏳ Waiting for builds to complete..."
oc logs -f bc/stickytux-backend-build &
BACKEND_PID=$!
oc logs -f bc/stickytux-frontend-build &
FRONTEND_PID=$!

# Wait for both builds
wait $BACKEND_PID
wait $FRONTEND_PID

echo "🚢 Deploying applications..."
oc apply -f "$SCRIPT_DIR/deployments.yaml"
oc apply -f "$SCRIPT_DIR/services.yaml"
oc apply -f "$SCRIPT_DIR/routes.yaml"

echo "⏳ Waiting for deployments to be ready..."
oc rollout status deployment/stickytux-backend
oc rollout status deployment/stickytux-frontend

echo "🌐 Getting route URLs..."
FRONTEND_URL=$(oc get route stickytux-frontend -o jsonpath='{.spec.host}')
BACKEND_URL=$(oc get route stickytux-backend -o jsonpath='{.spec.host}')

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📱 Frontend URL: https://$FRONTEND_URL"
echo "🔧 Backend URL:  https://$BACKEND_URL"
echo ""
echo "🔍 To check the status:"
echo "  oc get pods"
echo "  oc logs -f deployment/stickytux-backend"
echo "  oc logs -f deployment/stickytux-frontend"
echo ""
echo "🗑️  To clean up:"
echo "  oc delete project $PROJECT_NAME"