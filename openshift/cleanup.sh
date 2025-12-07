#!/bin/bash

# StickyTux OpenShift Cleanup Script
# This script removes all StickyTux resources from OpenShift

set -e

PROJECT_NAME=${1:-stickytux}

echo "🗑️  Cleaning up StickyTux deployment from OpenShift"
echo "Project: $PROJECT_NAME"
echo ""

# Check if logged in
if ! oc whoami &> /dev/null; then
    echo "❌ Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

# Switch to project
oc project $PROJECT_NAME 2>/dev/null || {
    echo "❌ Project $PROJECT_NAME does not exist"
    exit 1
}

echo "⚠️  WARNING: This will delete all StickyTux resources including persistent data!"
echo "This includes:"
echo "  - Deployments and pods"
echo "  - Services and routes"
echo "  - Build configurations and images"
echo "  - Persistent volume claims (DATABASE AND MEDIA FILES)"
echo "  - Secrets and config maps"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo ""
echo "🔄 Removing StickyTux resources..."

# Remove deployments first (this will stop the pods)
echo "Removing deployments..."
oc delete deployment -l app=stickytux --ignore-not-found=true

# Remove services and routes
echo "Removing services and routes..."
oc delete service -l app=stickytux --ignore-not-found=true
oc delete route -l app=stickytux --ignore-not-found=true

# Remove build configurations and builds
echo "Removing build configurations..."
oc delete buildconfig -l app=stickytux --ignore-not-found=true
oc delete build -l app=stickytux --ignore-not-found=true

# Remove image streams
echo "Removing image streams..."
oc delete imagestream -l app=stickytux --ignore-not-found=true

# Remove secrets and config maps
echo "Removing secrets and config maps..."
oc delete secret -l app=stickytux --ignore-not-found=true
oc delete configmap -l app=stickytux --ignore-not-found=true

# Ask about PVCs separately since they contain data
echo ""
echo "⚠️  Persistent Volume Claims contain your data:"
oc get pvc -l app=stickytux --no-headers 2>/dev/null | while read pvc rest; do
    echo "  - $pvc"
done

echo ""
read -p "Do you want to delete persistent volume claims? This will permanently delete all data! (type 'DELETE' to confirm): " DELETE_PVC

if [ "$DELETE_PVC" = "DELETE" ]; then
    echo "Removing persistent volume claims..."
    oc delete pvc -l app=stickytux --ignore-not-found=true
    echo "💥 All data has been permanently deleted!"
else
    echo "💾 Persistent volume claims preserved. You can manually delete them later with:"
    echo "    oc delete pvc stickytux-database-pvc stickytux-media-pvc"
fi

echo ""
echo "✅ StickyTux cleanup completed!"
echo ""
echo "📊 Remaining resources in project $PROJECT_NAME:"
oc get all,pvc,secrets,configmap --show-labels | grep -E "(app=stickytux|NAME)" || echo "No StickyTux resources found"