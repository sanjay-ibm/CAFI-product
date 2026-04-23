#!/bin/bash

##############################################################################
# OpenShift Deployment Script with Ngrok Sidecar
# 
# This script deploys the Product Catalog API to OpenShift with ngrok running
# as a sidecar container in the same pod.
#
# Prerequisites:
# - oc CLI installed and logged in
# - Ngrok authtoken from https://dashboard.ngrok.com
# - Run from project root directory
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cfai-project"
APP_NAME="product-catalog-api"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}OpenShift Deployment with Ngrok Sidecar${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if oc CLI is installed
if ! command -v oc &> /dev/null; then
    print_error "oc CLI not found. Please install OpenShift CLI."
    exit 1
fi
print_success "oc CLI found"

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    print_error "Not logged in to OpenShift. Please run: oc login"
    exit 1
fi
print_success "Logged in to OpenShift as $(oc whoami)"

# Check if running from project root
if [ ! -d "src" ] || [ ! -f "config/requirements.txt" ]; then
    print_error "Must run from project root directory (where src/ and config/ exist)"
    print_info "Current directory: $(pwd)"
    exit 1
fi
print_success "Running from project root"

# Prompt for ngrok authtoken
echo ""
print_info "Get your ngrok authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
echo -n "Enter your ngrok authtoken: "
read -s NGROK_AUTHTOKEN
echo ""

if [ -z "$NGROK_AUTHTOKEN" ]; then
    print_error "Ngrok authtoken is required"
    exit 1
fi
print_success "Ngrok authtoken provided"

# Create or switch to project
echo ""
print_info "Setting up OpenShift project: ${PROJECT_NAME}"
if oc get project ${PROJECT_NAME} &> /dev/null; then
    print_warning "Project ${PROJECT_NAME} already exists, switching to it"
    oc project ${PROJECT_NAME}
else
    oc new-project ${PROJECT_NAME} --display-name="CAFI Product Catalog" --description="Product Catalog API with Confidence Scoring"
    print_success "Project ${PROJECT_NAME} created"
fi

# Clean up existing resources
echo ""
print_info "Cleaning up existing resources..."
oc delete all,configmap,secret -l app=${APP_NAME} --ignore-not-found=true
print_success "Cleanup complete"

# Create ConfigMap
echo ""
print_info "Creating ConfigMap..."
oc create configmap product-catalog-config \
    --from-literal=APP_ENV=production \
    --from-literal=LOG_LEVEL=INFO \
    --from-literal=PORT=8000
oc label configmap product-catalog-config app=${APP_NAME}
print_success "ConfigMap created"

# Create Secret for ngrok authtoken
echo ""
print_info "Creating Secret for ngrok authtoken..."
oc create secret generic ngrok-auth \
    --from-literal=NGROK_AUTHTOKEN="${NGROK_AUTHTOKEN}"
oc label secret ngrok-auth app=${APP_NAME}
print_success "Secret created"

# Create ImageStream
echo ""
print_info "Creating ImageStream..."
oc create imagestream ${APP_NAME} || true
print_success "ImageStream ready"

# Create BuildConfig
echo ""
print_info "Creating BuildConfig..."
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
print_success "BuildConfig created"

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    print_info "Creating Dockerfile..."
    cat > Dockerfile <<'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
DOCKERFILE
    print_success "Dockerfile created"
fi

# Start build
echo ""
print_info "Starting build (this may take a few minutes)..."
oc start-build ${APP_NAME} --from-dir=. --follow
print_success "Build completed"

# Deploy application with ngrok sidecar
echo ""
print_info "Deploying application with ngrok sidecar..."
cat <<EOF | oc apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${APP_NAME}
  template:
    metadata:
      labels:
        app: ${APP_NAME}
    spec:
      containers:
      # Main API Container
      - name: api
        image: image-registry.openshift-image-registry.svc:5000/${PROJECT_NAME}/${APP_NAME}:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: product-catalog-config
              key: APP_ENV
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: product-catalog-config
              key: LOG_LEVEL
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: product-catalog-config
              key: PORT
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      
      # Ngrok Sidecar Container
      - name: ngrok
        image: ngrok/ngrok:latest
        ports:
        - containerPort: 4040
          name: ngrok-web
        env:
        - name: NGROK_AUTHTOKEN
          valueFrom:
            secretKeyRef:
              name: ngrok-auth
              key: NGROK_AUTHTOKEN
        command:
        - /bin/sh
        - -c
        - |
          echo "Starting ngrok tunnel..."
          ngrok http http://localhost:8000 --log=stdout --log-level=info
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /api/tunnels
            port: 4040
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/tunnels
            port: 4040
          initialDelaySeconds: 5
          periodSeconds: 5
EOF
print_success "Deployment created"

# Create Service
echo ""
print_info "Creating Service..."
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
spec:
  selector:
    app: ${APP_NAME}
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: ngrok-web
    port: 4040
    targetPort: 4040
  type: ClusterIP
EOF
print_success "Service created"

# Create Routes
echo ""
print_info "Creating Routes..."

# Route for API
cat <<EOF | oc apply -f -
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
spec:
  to:
    kind: Service
    name: ${APP_NAME}
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
EOF

# Route for ngrok web interface
cat <<EOF | oc apply -f -
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ${APP_NAME}-ngrok-web
  labels:
    app: ${APP_NAME}
spec:
  to:
    kind: Service
    name: ${APP_NAME}
  port:
    targetPort: ngrok-web
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
EOF
print_success "Routes created"

# Wait for deployment
echo ""
print_info "Waiting for deployment to be ready..."
oc rollout status deployment/${APP_NAME} --timeout=5m
print_success "Deployment is ready"

# Get URLs
echo ""
API_URL=$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}')
NGROK_WEB_URL=$(oc get route ${APP_NAME}-ngrok-web -o jsonpath='{.spec.host}')

# Wait a bit for ngrok to establish tunnel
echo ""
print_info "Waiting for ngrok tunnel to establish..."
sleep 10

# Get ngrok public URL
echo ""
print_info "Fetching ngrok public URL..."
NGROK_PUBLIC_URL=$(curl -s https://${NGROK_WEB_URL}/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4 | head -1)

# Display results
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📍 OpenShift Route (Internal):${NC}"
echo -e "   https://${API_URL}"
echo ""
echo -e "${BLUE}🌐 Ngrok Public URL (External):${NC}"
if [ -n "$NGROK_PUBLIC_URL" ]; then
    echo -e "   ${NGROK_PUBLIC_URL}"
else
    echo -e "   ${YELLOW}Fetching... Check ngrok web interface${NC}"
fi
echo ""
echo -e "${BLUE}📊 Ngrok Web Interface:${NC}"
echo -e "   https://${NGROK_WEB_URL}"
echo ""
echo -e "${BLUE}📚 API Documentation:${NC}"
echo -e "   https://${API_URL}/docs"
echo -e "   ${NGROK_PUBLIC_URL}/docs"
echo ""
echo -e "${BLUE}💚 Health Check:${NC}"
echo -e "   https://${API_URL}/health"
echo -e "   ${NGROK_PUBLIC_URL}/health"
echo ""

# Test endpoints
echo -e "${BLUE}Testing endpoints...${NC}"
echo ""

# Test OpenShift route
print_info "Testing OpenShift route..."
if curl -k -s "https://${API_URL}/health" | grep -q "ok"; then
    print_success "OpenShift route is working"
else
    print_warning "OpenShift route test failed (may need a moment to start)"
fi

# Test ngrok URL
if [ -n "$NGROK_PUBLIC_URL" ]; then
    print_info "Testing ngrok public URL..."
    if curl -s "${NGROK_PUBLIC_URL}/health" | grep -q "ok"; then
        print_success "Ngrok public URL is working"
    else
        print_warning "Ngrok URL test failed (may need a moment to start)"
    fi
fi

# Display monitoring commands
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "  oc logs -f deployment/${APP_NAME} -c api"
echo "  oc logs -f deployment/${APP_NAME} -c ngrok"
echo ""
echo -e "${YELLOW}Get ngrok URL:${NC}"
echo "  curl -s https://${NGROK_WEB_URL}/api/tunnels | grep public_url"
echo ""
echo -e "${YELLOW}View pods:${NC}"
echo "  oc get pods -l app=${APP_NAME}"
echo ""
echo -e "${YELLOW}Scale deployment:${NC}"
echo "  oc scale deployment/${APP_NAME} --replicas=2"
echo ""
echo -e "${YELLOW}Delete deployment:${NC}"
echo "  oc delete all,configmap,secret -l app=${APP_NAME}"
echo ""

print_success "Deployment complete!"

# Made with Bob
