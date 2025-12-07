#!/bin/bash

# Update ConfigMap for existing StickyTux deployment
# This script updates CORS/CSRF configuration without full redeployment

set -e

PROJECT_NAME=${1:-stickytux}

echo "🔧 Updating StickyTux ConfigMap"
echo "Project: $PROJECT_NAME"

# Check if logged in
if ! oc whoami &> /dev/null; then
    echo "❌ Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

# Switch to project
echo "📁 Switching to project: $PROJECT_NAME"
oc project $PROJECT_NAME

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

echo "🔧 Updating URLs:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend: $BACKEND_URL"

# Update ConfigMap
echo "📝 Updating ConfigMap..."
oc patch configmap stickytux-config --type merge -p "{
  \"data\": {
    \"CORS_ALLOWED_ORIGINS\": \"$FRONTEND_URL,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174\",
    \"CSRF_TRUSTED_ORIGINS\": \"$FRONTEND_URL,$BACKEND_URL,https://*.$CLUSTER_DOMAIN,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174\",
    \"FRONTEND_URL\": \"$FRONTEND_URL\"
  }
}"

echo "🔄 Restarting backend deployment to pick up changes..."
oc rollout restart deployment/stickytux-backend

echo "✅ ConfigMap updated successfully!"
echo ""
echo "🔍 Monitor the rollout with:"
echo "  oc rollout status deployment/stickytux-backend"
echo ""
echo "📱 Access your application at:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend: $BACKEND_URL"