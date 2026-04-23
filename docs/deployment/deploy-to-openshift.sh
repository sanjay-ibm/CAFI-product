#!/bin/bash

# CAFI Product OpenShift Deployment Script with Internal Registry
# This script builds images and deploys the CAFI Product API to OpenShift with ngrok tunneling

set -e

echo "🚀 Starting CAFI Product OpenShift Deployment..."

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

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Create or switch to namespace
echo ""
echo "📦 Creating/switching to namespace: cafi-product"
oc create namespace cafi-product --dry-run=client -o yaml | oc apply -f -
oc project cafi-product

# Build CAFI Product Image
echo ""
echo "🏗️  Building CAFI Product image..."
if ! oc get bc/cafi-product &> /dev/null; then
    echo "Creating BuildConfig for cafi-product..."
    oc new-build --name=cafi-product \
      --binary=true \
      --strategy=docker \
      -n cafi-product
fi

echo "Starting build from source..."
cd "$PROJECT_ROOT"
oc start-build cafi-product \
  --from-dir=. \
  --follow \
  -n cafi-product

echo "✅ CAFI Product image built successfully"

# Check if ngrok image exists
echo ""
echo "🔍 Checking ngrok image..."
if ! oc get is/ngrok &> /dev/null; then
    echo "⚠️  ngrok image not found in internal registry"
    echo ""
    echo "You need to build/push the ngrok image manually:"
    echo ""
    echo "Option 1: Pull and push ngrok image (requires Docker/Podman):"
    echo "  docker pull ngrok/ngrok:3"
    echo "  docker tag ngrok/ngrok:3 \$(oc registry info)/cafi-product/ngrok:3"
    echo "  docker push \$(oc registry info)/cafi-product/ngrok:3"
    echo ""
    echo "Option 2: Use OpenShift Route instead (no ngrok needed):"
    echo "  oc apply -f $SCRIPT_DIR/openshift-deployment-route.yaml"
    echo ""
    read -p "Do you want to continue without ngrok? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled. Please build ngrok image first."
        exit 1
    fi
    USE_ROUTE=true
else
    echo "✅ ngrok image found in registry"
    USE_ROUTE=false
fi

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
if [ "$USE_ROUTE" = true ]; then
    echo "🔧 Applying OpenShift deployment with Route (no ngrok)..."
    oc apply -f "$SCRIPT_DIR/openshift-deployment-route.yaml"
    
    # Wait for deployment
    echo ""
    echo "⏳ Waiting for deployment to be ready..."
    oc rollout status deployment/cafi-product-api -n cafi-product --timeout=5m
    
    # Get Route URL
    echo ""
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📊 Deployment Information:"
    echo "=========================="
    echo "Namespace: cafi-product"
    echo "API Service: cafi-product-service:8000"
    echo ""
    ROUTE_URL=$(oc get route cafi-product-route -n cafi-product -o jsonpath='{.spec.host}')
    echo "🌐 Public URL: https://$ROUTE_URL"
    echo ""
    echo "🧪 Test the API:"
    echo "curl https://$ROUTE_URL/health"
    
else
    echo "🔧 Applying OpenShift deployment with ngrok..."
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
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📊 Deployment Information:"
    echo "=========================="
    echo "Namespace: cafi-product"
    echo "API Service: cafi-product-service:8000"
    echo "ngrok Pod: $NGROK_POD"
    echo ""
    echo "🌐 Getting ngrok public URL..."
    NGROK_URL=$(oc logs $NGROK_POD -n cafi-product 2>/dev/null | grep -o 'https://[a-z0-9-]*\.ngrok-free\.app' | head -1)
    if [ -n "$NGROK_URL" ]; then
        echo "Public URL: $NGROK_URL"
        echo ""
        echo "🧪 Test the API:"
        echo "curl $NGROK_URL/health"
    else
        echo "⚠️  ngrok URL not ready yet. Run this command to get it:"
        echo "oc logs $NGROK_POD -n cafi-product | grep 'url='"
    fi
fi

echo ""
echo "🔍 To view API logs:"
echo "oc logs -f deployment/cafi-product-api -n cafi-product"
echo ""
if [ "$USE_ROUTE" = false ]; then
    echo "🔍 To view ngrok logs:"
    echo "oc logs -f deployment/ngrok-tunnel -n cafi-product"
    echo ""
fi
echo "🗑️  To delete the deployment:"
echo "oc delete namespace cafi-product"
echo ""
echo "✅ Deployment complete!"

# Made with Bob
