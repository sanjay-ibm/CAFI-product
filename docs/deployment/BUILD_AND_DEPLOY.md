# Build and Deploy to OpenShift Internal Registry

This guide shows how to build images locally and push them to OpenShift's internal registry to avoid Docker Hub rate limits.

## 🎯 Overview

The deployment uses OpenShift's internal registry to host:
1. **cafi-product** - Your Python Flask API
2. **ngrok** - ngrok tunnel for external access

## 📋 Prerequisites

1. OpenShift CLI (`oc`) installed and logged in
2. Docker or Podman installed locally
3. Access to OpenShift internal registry

## 🔧 Step 1: Enable Internal Registry Access

```bash
# Login to OpenShift
oc login <your-cluster-url>

# Create namespace
oc create namespace cafi-product
oc project cafi-product

# Expose the internal registry (if not already exposed)
oc patch configs.imageregistry.operator.openshift.io/cluster --patch '{"spec":{"defaultRoute":true}}' --type=merge

# Get the registry route
REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')
echo "Registry: $REGISTRY"

# Login to the registry
oc registry login
```

## 🏗️ Step 2: Build and Push CAFI Product Image

### Option A: Using Docker

```bash
# Build the image
docker build -t cafi-product:latest -f Dockerfile .

# Tag for OpenShift registry
docker tag cafi-product:latest $REGISTRY/cafi-product/cafi-product:latest

# Push to registry
docker push $REGISTRY/cafi-product/cafi-product:latest
```

### Option B: Using Podman

```bash
# Build the image
podman build -t cafi-product:latest -f Dockerfile .

# Tag for OpenShift registry
podman tag cafi-product:latest $REGISTRY/cafi-product/cafi-product:latest

# Push to registry
podman push $REGISTRY/cafi-product/cafi-product:latest
```

### Option C: Using OpenShift BuildConfig (Recommended)

```bash
# Create BuildConfig from Dockerfile
oc new-build --name=cafi-product \
  --binary=true \
  --strategy=docker \
  -n cafi-product

# Start build from current directory
oc start-build cafi-product \
  --from-dir=. \
  --follow \
  -n cafi-product

# The image will be automatically available at:
# image-registry.openshift-image-registry.svc:5000/cafi-product/cafi-product:latest
```

## 🌐 Step 3: Build and Push ngrok Image

### Option A: Pull and Push ngrok

```bash
# Pull ngrok image locally (on a machine without rate limits)
docker pull ngrok/ngrok:3

# Tag for OpenShift registry
docker tag ngrok/ngrok:3 $REGISTRY/cafi-product/ngrok:3

# Push to registry
docker push $REGISTRY/cafi-product/ngrok:3
```

### Option B: Create ngrok BuildConfig

Create a file `ngrok-build.yaml`:

```yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: ngrok
  namespace: cafi-product
spec:
  output:
    to:
      kind: ImageStreamTag
      name: ngrok:3
  source:
    dockerfile: |
      FROM ngrok/ngrok:3
      USER 1001
  strategy:
    dockerStrategy:
      from:
        kind: DockerImage
        name: ngrok/ngrok:3
    type: Docker
```

Apply and build:

```bash
oc apply -f ngrok-build.yaml
oc start-build ngrok -n cafi-product --follow
```

## 📦 Step 4: Create ConfigMap with Application Code

```bash
# From project root directory
oc create configmap cafi-product-code \
  --from-file=app.py \
  --from-file=config/requirements.txt \
  --from-file=src/ \
  -n cafi-product
```

## 🚀 Step 5: Deploy the Application

```bash
# Apply the deployment
oc apply -f docs/deployment/openshift-deployment.yaml

# Wait for deployments
oc rollout status deployment/cafi-product-api -n cafi-product
oc rollout status deployment/ngrok-tunnel -n cafi-product

# Check pods
oc get pods -n cafi-product
```

## 🔍 Step 6: Get ngrok Public URL

```bash
# Get ngrok pod name
NGROK_POD=$(oc get pods -l app=ngrok -o jsonpath='{.items[0].metadata.name}' -n cafi-product)

# View logs to find public URL
oc logs $NGROK_POD -n cafi-product | grep "url="

# Or use this one-liner
oc logs -l app=ngrok -n cafi-product | grep -o 'https://[a-z0-9-]*\.ngrok-free\.app'
```

## 🧪 Step 7: Test the Deployment

```bash
# Get the ngrok URL
NGROK_URL=$(oc logs -l app=ngrok -n cafi-product | grep -o 'https://[a-z0-9-]*\.ngrok-free\.app' | head -1)

# Test health endpoint
curl $NGROK_URL/health

# Test search endpoint
curl -X POST $NGROK_URL/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop", "top_k": 5}'
```

## 🔄 Updating the Application

### Update Code

```bash
# Update ConfigMap
oc create configmap cafi-product-code \
  --from-file=app.py \
  --from-file=config/requirements.txt \
  --from-file=src/ \
  --dry-run=client -o yaml | oc apply -f -

# Restart deployment
oc rollout restart deployment/cafi-product-api -n cafi-product
```

### Rebuild Image

```bash
# Using BuildConfig
oc start-build cafi-product --from-dir=. --follow -n cafi-product

# Or rebuild and push with Docker/Podman
docker build -t cafi-product:latest .
docker tag cafi-product:latest $REGISTRY/cafi-product/cafi-product:latest
docker push $REGISTRY/cafi-product/cafi-product:latest

# Restart deployment to pull new image
oc rollout restart deployment/cafi-product-api -n cafi-product
```

## 📊 Monitoring

### View Logs

```bash
# API logs
oc logs -f deployment/cafi-product-api -n cafi-product

# ngrok logs
oc logs -f deployment/ngrok-tunnel -n cafi-product

# All pods
oc logs -f -l app=cafi-product -n cafi-product
```

### Check Status

```bash
# Pod status
oc get pods -n cafi-product

# Deployment status
oc get deployments -n cafi-product

# Service status
oc get svc -n cafi-product

# Events
oc get events -n cafi-product --sort-by='.lastTimestamp'
```

## 🗑️ Cleanup

```bash
# Delete everything
oc delete namespace cafi-product

# Or delete specific resources
oc delete deployment cafi-product-api ngrok-tunnel -n cafi-product
oc delete svc cafi-product-service -n cafi-product
oc delete configmap cafi-product-code -n cafi-product
oc delete secret ngrok-secret -n cafi-product
```

## 🔧 Troubleshooting

### Image Pull Errors

```bash
# Check if image exists in registry
oc get imagestream -n cafi-product

# Describe image stream
oc describe imagestream cafi-product -n cafi-product

# Check registry access
oc registry info
```

### Pod Not Starting

```bash
# Describe pod
oc describe pod <pod-name> -n cafi-product

# Check logs
oc logs <pod-name> -n cafi-product

# Check events
oc get events -n cafi-product
```

### ngrok Not Connecting

```bash
# Check ngrok logs
oc logs -l app=ngrok -n cafi-product

# Verify secret
oc get secret ngrok-secret -n cafi-product -o yaml

# Test ngrok auth token
oc exec -it <ngrok-pod> -n cafi-product -- ngrok config check
```

## 📝 Notes

- **Internal Registry**: Images are stored in OpenShift's internal registry
- **No Docker Hub**: Avoids rate limits by using internal registry
- **ngrok Auth Token**: Already configured in the deployment YAML
- **Security**: Uses OpenShift security contexts and non-root containers
- **Persistence**: ConfigMap stores application code, can be updated without rebuilding

## 🎯 Quick Reference

```bash
# Complete deployment in one go
oc create namespace cafi-product
oc project cafi-product
oc new-build --name=cafi-product --binary=true --strategy=docker
oc start-build cafi-product --from-dir=. --follow
oc create configmap cafi-product-code --from-file=app.py --from-file=config/requirements.txt --from-file=src/
oc apply -f docs/deployment/openshift-deployment.yaml
oc logs -l app=ngrok | grep "url="