#!/bin/bash

# CAFI Product OpenShift Deployment Script with ngrok
# This script deploys the CAFI Product API to OpenShift with ngrok tunneling

set -e

echo "🚀 Starting CAFI Product OpenShift Deployment with ngrok..."

# Check if oc CLI is installed
if ! command -v oc &> /dev/null; then
    echo "❌ Error: OpenShift CLI (oc) is not installed"
    echo "Please install it from: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html"
    exit 1
fi

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    echo "❌ Error: Not logged in to OpenShift cluster"
    echo "Please login using: oc login <cluster-url>"
    exit 1
fi

echo "✅ Connected to OpenShift cluster: $(oc whoami --show-server)"
echo "✅ Logged in as: $(oc whoami)"

# Create or switch to namespace
echo ""
echo "📦 Creating/switching to namespace: cafi-product"
oc create namespace cafi-product --dry-run=client -o yaml | oc apply -f -
oc project cafi-product

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Create ConfigMap with application code
echo ""
echo "📝 Creating ConfigMap with application code..."
cd "$PROJECT_ROOT"
oc create configmap cafi-product-code \
  --from-file=app.py \
  --from-file=config/requirements.txt \
  --from-file=src/ \
  --dry-run=client -o yaml | oc apply -f -

# Apply the deployment
echo ""
echo "🔧 Applying OpenShift deployment configuration..."
oc apply -f "$SCRIPT_DIR/openshift-deployment.yaml"

# Wait for deployments to be ready
echo ""
echo "⏳ Waiting for deployments to be ready..."
oc rollout status deployment/cafi-product-api -n cafi-product --timeout=5m
oc rollout status deployment/ngrok-tunnel -n cafi-product --timeout=5m

# Get ngrok tunnel URL
echo ""
echo "🔍 Fetching ngrok tunnel URL..."
sleep 10  # Wait for ngrok to establish tunnel

NGROK_POD=$(oc get pods -n cafi-product -l app=ngrok -o jsonpath='{.items[0].metadata.name}')
echo "📡 ngrok pod: $NGROK_POD"

echo ""
echo "🌐 Fetching ngrok public URL..."
echo "Run this command to get the ngrok URL:"
echo "oc logs -n cafi-product $NGROK_POD | grep -o 'https://[a-z0-9-]*\.ngrok-free\.app'"

# Display deployment info
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Deployment Information:"
echo "=========================="
echo "Namespace: cafi-product"
echo "API Service: cafi-product-service:8000"
echo "ngrok Pod: $NGROK_POD"
echo ""
echo "🔗 To get the ngrok public URL, run:"
echo "oc logs -n cafi-product $NGROK_POD | grep 'url='"
echo ""
echo "🔍 To view API logs:"
echo "oc logs -f deployment/cafi-product-api -n cafi-product"
echo ""
echo "🔍 To view ngrok logs:"
echo "oc logs -f deployment/ngrok-tunnel -n cafi-product"
echo ""
echo "🧪 To test the API (replace <ngrok-url> with actual URL):"
echo "curl <ngrok-url>/health"
echo ""
echo "🗑️  To delete the deployment:"
echo "oc delete namespace cafi-product"

# Made with Bob
