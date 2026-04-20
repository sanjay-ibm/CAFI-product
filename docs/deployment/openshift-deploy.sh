#!/bin/bash
################################################################################
# OpenShift Deployment Script - Product Catalog API
# Run this script on mcpX1 where you have oc CLI access
################################################################################

set -e

PROJECT="cfai-project"
APP="product-catalog-api"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Product Catalog API - OpenShift Deployment               ║"
echo "╔════════════════════════════════════════════════════════════╝"
echo ""

# Verify oc CLI
if ! command -v oc &> /dev/null; then
    echo "❌ Error: oc CLI not found"
    exit 1
fi

# Verify login
if ! oc whoami &> /dev/null; then
    echo "❌ Error: Not logged in to OpenShift"
    echo "Run: oc login https://api.cfai.cp.fyre.ibm.com:6443"
    exit 1
fi

echo "✅ Logged in as: $(oc whoami)"
echo ""

# Create or use project
echo "📦 Setting up project..."
oc new-project ${PROJECT} 2>/dev/null || oc project ${PROJECT}
echo "✅ Using project: ${PROJECT}"
echo ""

# Clean up existing resources
echo "🧹 Cleaning up existing resources..."
oc delete all,configmap,secret -l app=${APP} --ignore-not-found=true
echo "✅ Cleanup complete"
echo ""

# Create ConfigMap
echo "⚙️  Creating ConfigMap..."
cat <<EOF | oc apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${APP}-config
  labels:
    app: ${APP}
data:
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
  API_TITLE: "Product Catalog API"
  API_VERSION: "1.0.0"
EOF
echo "✅ ConfigMap created"
echo ""

# Create ImageStream
echo "🖼️  Creating ImageStream..."
cat <<EOF | oc apply -f -
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: ${APP}
  labels:
    app: ${APP}
spec:
  lookupPolicy:
    local: true
EOF
echo "✅ ImageStream created"
echo ""

# Create BuildConfig
echo "🔨 Creating BuildConfig..."
cat <<EOF | oc apply -f -
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: ${APP}
  labels:
    app: ${APP}
spec:
  output:
    to:
      kind: ImageStreamTag
      name: ${APP}:latest
  source:
    type: Binary
  strategy:
    dockerStrategy:
      dockerfilePath: Dockerfile
  resources:
    limits:
      cpu: "2"
      memory: "2Gi"
    requests:
      cpu: "500m"
      memory: "1Gi"
EOF
echo "✅ BuildConfig created"
echo ""

# Create Dockerfile inline
echo "📝 Creating Dockerfile..."
cat > /tmp/Dockerfile <<'DOCKERFILE'
FROM registry.access.redhat.com/ubi9/python-311:latest

WORKDIR /opt/app-root/src

USER 0

# Copy and install requirements
COPY config/requirements.txt ./config/
RUN pip install --no-cache-dir -r config/requirements.txt

# Copy application
COPY src/ ./src/
COPY data/product_match_dictionary.json ./data/

# Set permissions
RUN chgrp -R 0 /opt/app-root && chmod -R g=u /opt/app-root

USER 1001

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE
echo "✅ Dockerfile created"
echo ""

# Prepare build context
echo "📦 Preparing build context..."
BUILD_DIR=$(mktemp -d)
trap "rm -rf ${BUILD_DIR}" EXIT

# Create directory structure
mkdir -p ${BUILD_DIR}/src
mkdir -p ${BUILD_DIR}/config
mkdir -p ${BUILD_DIR}/data

# Copy files with error checking
echo "  Copying source files..."
if [ -d "src" ]; then
    cp -r src/* ${BUILD_DIR}/src/
    echo "  ✓ Source files copied"
else
    echo "  ✗ src directory not found"
    exit 1
fi

if [ -f "config/requirements.txt" ]; then
    cp config/requirements.txt ${BUILD_DIR}/config/
    echo "  ✓ requirements.txt copied"
else
    echo "  ✗ config/requirements.txt not found"
    exit 1
fi

if [ -f "data/product_match_dictionary.json" ]; then
    cp data/product_match_dictionary.json ${BUILD_DIR}/data/
    echo "  ✓ product_match_dictionary.json copied"
else
    echo "  ✗ data/product_match_dictionary.json not found"
    exit 1
fi

cp /tmp/Dockerfile ${BUILD_DIR}/
echo "  ✓ Dockerfile copied"

# List build context contents for verification
echo ""
echo "Build context contents:"
ls -la ${BUILD_DIR}/
echo ""
echo "Config directory:"
ls -la ${BUILD_DIR}/config/ 2>/dev/null || echo "  (empty or missing)"
echo ""
echo "Build context size: $(du -sh ${BUILD_DIR} | cut -f1)"
echo ""

# Build image
echo "🏗️  Building image (this may take a few minutes)..."
if oc start-build ${APP} --from-dir=${BUILD_DIR} --follow --wait; then
    echo "✅ Build completed successfully"
else
    echo "❌ Build failed"
    echo "Check logs: oc logs -f bc/${APP}"
    exit 1
fi
echo ""

# Create Deployment
echo "🚀 Creating Deployment..."
cat <<EOF | oc apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP}
  labels:
    app: ${APP}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${APP}
  template:
    metadata:
      labels:
        app: ${APP}
    spec:
      containers:
      - name: ${APP}
        image: image-registry.openshift-image-registry.svc:5000/${PROJECT}/${APP}:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: ${APP}-config
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
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
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
EOF
echo "✅ Deployment created"
echo ""

# Create Service
echo "🌐 Creating Service..."
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ${APP}
  labels:
    app: ${APP}
spec:
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  selector:
    app: ${APP}
EOF
echo "✅ Service created"
echo ""

# Create Route
echo "🔗 Creating Route..."
cat <<EOF | oc apply -f -
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ${APP}
  labels:
    app: ${APP}
spec:
  to:
    kind: Service
    name: ${APP}
  port:
    targetPort: 8000
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
EOF
echo "✅ Route created"
echo ""

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
oc rollout status deployment/${APP} --timeout=5m
echo "✅ Deployment is ready"
echo ""

# Get route URL
URL=$(oc get route ${APP} -o jsonpath='{.spec.host}')

# Display results
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎉 Deployment Complete!                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Application URL:     https://${URL}"
echo "📚 API Documentation:   https://${URL}/docs"
echo "💚 Health Check:        https://${URL}/health"
echo ""
echo "📋 Useful Commands:"
echo "   View pods:    oc get pods -l app=${APP}"
echo "   View logs:    oc logs -f deployment/${APP}"
echo "   Scale app:    oc scale deployment/${APP} --replicas=3"
echo "   Rebuild:      oc start-build ${APP} --follow"
echo ""

# Test health endpoint
echo "🧪 Testing health endpoint..."
sleep 5
if curl -k -s https://${URL}/health | grep -q "status"; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check pending (app may still be starting)"
fi
echo ""

echo "✨ Deployment completed successfully!"

# Made with Bob
