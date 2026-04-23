#!/bin/bash

##############################################################################
# Fix ImagePullBackOff Issue
# 
# This script fixes the image pull issue by ensuring the build completes
# and the deployment uses the correct image reference.
##############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_NAME="cfai-project"
APP_NAME="product-catalog-api"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Fixing ImagePullBackOff Issue${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if in correct project
oc project ${PROJECT_NAME}

# Step 1: Check if build exists
echo -e "${BLUE}Step 1: Checking build status...${NC}"
if ! oc get bc/${APP_NAME} &> /dev/null; then
    echo -e "${RED}BuildConfig not found. Creating...${NC}"
    
    # Create BuildConfig
    cat <<EOF | oc apply -f -
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
spec:
  output:
    to:
      kind: ImageStreamTag
      name: ${APP_NAME}:latest
  source:
    type: Binary
  strategy:
    type: Docker
    dockerStrategy:
      dockerfilePath: Dockerfile
EOF
    echo -e "${GREEN}✓ BuildConfig created${NC}"
fi

# Step 2: Check if ImageStream exists
echo -e "${BLUE}Step 2: Checking ImageStream...${NC}"
if ! oc get is/${APP_NAME} &> /dev/null; then
    echo -e "${YELLOW}ImageStream not found. Creating...${NC}"
    oc create imagestream ${APP_NAME}
    echo -e "${GREEN}✓ ImageStream created${NC}"
fi

# Step 3: Start build if no successful build exists
echo -e "${BLUE}Step 3: Checking for successful build...${NC}"
BUILD_STATUS=$(oc get builds -l app=${APP_NAME} -o jsonpath='{.items[-1].status.phase}' 2>/dev/null || echo "None")

if [ "$BUILD_STATUS" != "Complete" ]; then
    echo -e "${YELLOW}No successful build found. Starting build...${NC}"
    echo -e "${YELLOW}This will take 3-5 minutes...${NC}"
    
    # Check if we're in the right directory
    if [ ! -f "Dockerfile" ]; then
        echo -e "${RED}Error: Dockerfile not found. Please run from project root.${NC}"
        exit 1
    fi
    
    # Start build
    oc start-build ${APP_NAME} --from-dir=. --follow
    echo -e "${GREEN}✓ Build completed${NC}"
else
    echo -e "${GREEN}✓ Build already complete${NC}"
fi

# Step 4: Get the correct image reference
echo -e "${BLUE}Step 4: Getting image reference...${NC}"
IMAGE_STREAM=$(oc get is/${APP_NAME} -o jsonpath='{.status.dockerImageRepository}')
if [ -z "$IMAGE_STREAM" ]; then
    echo -e "${RED}Error: ImageStream not ready. Waiting...${NC}"
    sleep 10
    IMAGE_STREAM=$(oc get is/${APP_NAME} -o jsonpath='{.status.dockerImageRepository}')
fi

echo -e "${GREEN}Image: ${IMAGE_STREAM}:latest${NC}"

# Step 5: Update deployment to use correct image
echo -e "${BLUE}Step 5: Updating deployment...${NC}"

# Check if deployment exists
if oc get deployment/${APP_NAME} &> /dev/null; then
    # Update existing deployment
    oc set image deployment/${APP_NAME} api=${IMAGE_STREAM}:latest
    echo -e "${GREEN}✓ Deployment image updated${NC}"
    
    # Restart deployment
    oc rollout restart deployment/${APP_NAME}
    echo -e "${GREEN}✓ Deployment restarted${NC}"
else
    echo -e "${YELLOW}Deployment not found. It should be created by the main script.${NC}"
    exit 1
fi

# Step 6: Wait for deployment
echo -e "${BLUE}Step 6: Waiting for deployment...${NC}"
oc rollout status deployment/${APP_NAME} --timeout=5m

# Step 7: Check pod status
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Pod Status:${NC}"
oc get pods -l app=${APP_NAME}

# Step 8: Get URLs
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Deployment URLs:${NC}"
echo -e "${BLUE}========================================${NC}"

OPENSHIFT_URL=$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not found")
NGROK_WEB=$(oc get route ${APP_NAME}-ngrok-web -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not found")

echo -e "${BLUE}OpenShift Route:${NC} https://${OPENSHIFT_URL}"
echo -e "${BLUE}Ngrok Web Interface:${NC} https://${NGROK_WEB}"

# Wait for ngrok tunnel
echo ""
echo -e "${BLUE}Waiting for ngrok tunnel...${NC}"
sleep 15

if [ "$NGROK_WEB" != "Not found" ]; then
    NGROK_URL=$(curl -s https://${NGROK_WEB}/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4 | head -1)
    if [ -n "$NGROK_URL" ]; then
        echo -e "${BLUE}Ngrok Public URL:${NC} ${NGROK_URL}"
    else
        echo -e "${YELLOW}Ngrok tunnel not ready yet. Check: https://${NGROK_WEB}${NC}"
    fi
fi

# Test health endpoint
echo ""
echo -e "${BLUE}Testing health endpoint...${NC}"
if curl -k -s "https://${OPENSHIFT_URL}/health" | grep -q "ok"; then
    echo -e "${GREEN}✓ API is responding!${NC}"
else
    echo -e "${YELLOW}⚠ API not responding yet. Check logs:${NC}"
    echo "  oc logs -f deployment/${APP_NAME} -c api"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fix Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Made with Bob
