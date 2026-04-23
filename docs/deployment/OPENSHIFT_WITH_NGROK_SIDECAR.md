# OpenShift Deployment with Ngrok Sidecar

## Overview

This deployment configuration runs both your Product Catalog API and ngrok in the **same OpenShift pod** as separate containers. This provides:

- ✅ **Internal OpenShift Route**: For cluster-internal and IBM network access
- ✅ **External Ngrok URL**: For public internet access and external integrations
- ✅ **Single Pod**: Both containers share the same network namespace
- ✅ **Automatic Tunnel**: Ngrok automatically tunnels to the API container

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenShift Pod                         │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  API Container   │      │ Ngrok Container  │        │
│  │                  │      │                  │        │
│  │  Port: 8000      │◄────►│  Tunnel to       │        │
│  │  /health         │      │  localhost:8000  │        │
│  │  /products       │      │                  │        │
│  │  /docs           │      │  Port: 4040      │        │
│  └──────────────────┘      │  (Web Interface) │        │
│                             └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
           │                           │
           │                           │
           ▼                           ▼
  ┌─────────────────┐        ┌─────────────────┐
  │ OpenShift Route │        │  Ngrok Cloud    │
  │  (Internal)     │        │  (External)     │
  └─────────────────┘        └─────────────────┘
           │                           │
           ▼                           ▼
    Internal Users              External Users
```

## Quick Start

### Prerequisites

1. Access to OpenShift cluster (mcpX1 server)
2. `oc` CLI installed and logged in
3. Ngrok account and authtoken from https://dashboard.ngrok.com
4. Project files in correct structure

### One-Command Deployment

```bash
# On mcpX1 server
cd /path/to/CAFI-product
chmod +x docs/deployment/deploy-with-ngrok.sh
./docs/deployment/deploy-with-ngrok.sh
```

The script will:
1. ✅ Prompt for your ngrok authtoken
2. ✅ Create OpenShift project
3. ✅ Build Docker image
4. ✅ Deploy API + ngrok sidecar
5. ✅ Create routes for both
6. ✅ Display both URLs

### Expected Output

```
========================================
Deployment Successful!
========================================

📍 OpenShift Route (Internal):
   https://product-catalog-api-cfai-project.apps.cfai.cp.fyre.ibm.com

🌐 Ngrok Public URL (External):
   https://abc123def456.ngrok-free.app

📊 Ngrok Web Interface:
   https://product-catalog-api-ngrok-web-cfai-project.apps.cfai.cp.fyre.ibm.com

📚 API Documentation:
   https://product-catalog-api-cfai-project.apps.cfai.cp.fyre.ibm.com/docs
   https://abc123def456.ngrok-free.app/docs

💚 Health Check:
   https://product-catalog-api-cfai-project.apps.cfai.cp.fyre.ibm.com/health
   https://abc123def456.ngrok-free.app/health
```

## Manual Deployment

If you prefer manual deployment or need to customize:

### Step 1: Get Ngrok Authtoken

1. Go to https://dashboard.ngrok.com/signup
2. Sign up or log in
3. Go to https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your authtoken

### Step 2: Login to OpenShift

```bash
ssh your-username@mcpX1.cfai.cp.fyre.ibm.com
oc login https://api.cfai.cp.fyre.ibm.com:6443
```

### Step 3: Create Project

```bash
oc new-project cfai-project
```

### Step 4: Create Secret

```bash
# Replace YOUR_NGROK_AUTHTOKEN with your actual token
oc create secret generic ngrok-auth \
  --from-literal=NGROK_AUTHTOKEN="YOUR_NGROK_AUTHTOKEN"
```

### Step 5: Deploy Using YAML

```bash
cd /path/to/CAFI-product
oc apply -f docs/deployment/openshift-ngrok-sidecar.yaml
```

### Step 6: Build Image

```bash
# Create BuildConfig
oc new-build --name=product-catalog-api --binary --strategy=docker

# Start build
oc start-build product-catalog-api --from-dir=. --follow
```

### Step 7: Get URLs

```bash
# OpenShift route
OPENSHIFT_URL=$(oc get route product-catalog-api -o jsonpath='{.spec.host}')
echo "OpenShift URL: https://${OPENSHIFT_URL}"

# Ngrok web interface
NGROK_WEB=$(oc get route product-catalog-api-ngrok-web -o jsonpath='{.spec.host}')
echo "Ngrok Web: https://${NGROK_WEB}"

# Get ngrok public URL
curl -s https://${NGROK_WEB}/api/tunnels | grep public_url
```

## Accessing Your API

### Internal Access (OpenShift Route)

Use this for:
- Internal IBM network access
- Cluster-internal services
- Development and testing within the network

```bash
OPENSHIFT_URL="https://product-catalog-api-cfai-project.apps.cfai.cp.fyre.ibm.com"

# Health check
curl -k ${OPENSHIFT_URL}/health

# Search with confidence scoring
curl -k "${OPENSHIFT_URL}/products/search?query=IBM+Cloud+Pak"

# API documentation
open ${OPENSHIFT_URL}/docs
```

### External Access (Ngrok URL)

Use this for:
- Public internet access
- External integrations
- Webhooks
- Third-party services

```bash
NGROK_URL="https://abc123def456.ngrok-free.app"

# Health check
curl ${NGROK_URL}/health

# Search endpoint
curl "${NGROK_URL}/products/search?query=watson"

# API documentation
open ${NGROK_URL}/docs
```

### Ngrok Web Interface

Monitor all traffic through ngrok:

```bash
NGROK_WEB="https://product-catalog-api-ngrok-web-cfai-project.apps.cfai.cp.fyre.ibm.com"

# Open in browser
open ${NGROK_WEB}
```

Features:
- View all requests/responses
- Replay requests
- Inspect headers and body
- Traffic statistics

## Testing Confidence Scoring

Both URLs support the new confidence scoring system:

### Test Exact Match (High Confidence)

```bash
# Via OpenShift
curl -k "${OPENSHIFT_URL}/products/search?query=IBM+Cloud+Pak+for+Data"

# Via Ngrok
curl "${NGROK_URL}/products/search?query=IBM+Cloud+Pak+for+Data"

# Expected response:
{
  "results": [{
    "score": 1.0,
    "confidence": 0.95,
    "product_code": "5737-H33",
    ...
  }]
}
```

### Test Fuzzy Match (Medium Confidence)

```bash
curl "${NGROK_URL}/products/search?query=cloud+database"

# Expected confidence: 0.50-0.70
```

### Test Multiple Products (Lower Confidence)

```bash
curl "${NGROK_URL}/products/search?query=watson"

# Expected confidence: 0.65-0.75 (penalty for multiple products)
```

## Monitoring

### View Logs

```bash
# API container logs
oc logs -f deployment/product-catalog-api -c api

# Ngrok container logs
oc logs -f deployment/product-catalog-api -c ngrok

# Both containers
oc logs -f deployment/product-catalog-api --all-containers=true
```

### Check Pod Status

```bash
# View pods
oc get pods -l app=product-catalog-api

# Describe pod
POD=$(oc get pods -l app=product-catalog-api -o jsonpath='{.items[0].metadata.name}')
oc describe pod $POD

# Check both containers
oc get pod $POD -o jsonpath='{.spec.containers[*].name}'
```

### Monitor Resources

```bash
# Resource usage
oc top pods -l app=product-catalog-api

# Events
oc get events --sort-by='.lastTimestamp' | grep product-catalog
```

### Get Ngrok Public URL

```bash
# Method 1: Via web interface route
NGROK_WEB=$(oc get route product-catalog-api-ngrok-web -o jsonpath='{.spec.host}')
curl -s https://${NGROK_WEB}/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4

# Method 2: From ngrok container logs
oc logs deployment/product-catalog-api -c ngrok | grep "url="
```

## Scaling Considerations

### Important: Ngrok Free Tier Limitation

⚠️ **Keep replicas at 1** when using ngrok free tier:

```bash
# This is already set in the deployment
oc get deployment product-catalog-api -o jsonpath='{.spec.replicas}'
# Output: 1
```

**Why?**
- Ngrok free tier allows only 1 tunnel per account
- Multiple replicas = multiple ngrok instances = connection conflicts
- OpenShift route handles load balancing internally

### If You Need Scaling

**Option 1: Upgrade Ngrok**
- Get ngrok paid plan
- Supports multiple tunnels
- Then scale: `oc scale deployment/product-catalog-api --replicas=3`

**Option 2: Use Only OpenShift Route**
- Remove ngrok sidecar
- Scale freely: `oc scale deployment/product-catalog-api --replicas=5`
- Use OpenShift route for all access

## Troubleshooting

### Ngrok Container Not Starting

```bash
# Check ngrok logs
oc logs deployment/product-catalog-api -c ngrok

# Common issues:
# 1. Invalid authtoken
oc get secret ngrok-auth -o jsonpath='{.data.NGROK_AUTHTOKEN}' | base64 -d

# 2. Update authtoken
oc delete secret ngrok-auth
oc create secret generic ngrok-auth --from-literal=NGROK_AUTHTOKEN="NEW_TOKEN"
oc rollout restart deployment/product-catalog-api
```

### API Container Not Starting

```bash
# Check API logs
oc logs deployment/product-catalog-api -c api

# Check build logs
oc logs -f bc/product-catalog-api

# Rebuild if needed
oc start-build product-catalog-api --from-dir=. --follow
```

### Can't Access Ngrok URL

```bash
# 1. Check if ngrok tunnel is established
oc logs deployment/product-catalog-api -c ngrok | grep "started tunnel"

# 2. Check ngrok web interface
NGROK_WEB=$(oc get route product-catalog-api-ngrok-web -o jsonpath='{.spec.host}')
curl -s https://${NGROK_WEB}/api/tunnels

# 3. Restart deployment
oc rollout restart deployment/product-catalog-api
```

### Ngrok URL Changes

Ngrok free tier generates a new URL on each restart:

```bash
# Get current URL
NGROK_WEB=$(oc get route product-catalog-api-ngrok-web -o jsonpath='{.spec.host}')
NEW_URL=$(curl -s https://${NGROK_WEB}/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4)
echo "New ngrok URL: ${NEW_URL}"

# Update your OpenAPI spec with this URL
```

## Configuration

### Environment Variables

Edit the ConfigMap to change settings:

```bash
oc edit configmap product-catalog-config

# Available settings:
# - APP_ENV: production/development
# - LOG_LEVEL: DEBUG/INFO/WARNING/ERROR
# - PORT: 8000 (default)
```

### Resource Limits

Edit deployment to adjust resources:

```bash
oc edit deployment product-catalog-api

# API container:
# - Memory: 256Mi-512Mi
# - CPU: 100m-500m

# Ngrok container:
# - Memory: 64Mi-128Mi
# - CPU: 50m-100m
```

## Security

### OpenShift Route
- ✅ TLS/HTTPS enabled
- ✅ Certificate managed by OpenShift
- ✅ Internal network only (by default)

### Ngrok Tunnel
- ⚠️ Public internet access
- ⚠️ Free tier shows warning page
- ⚠️ URL changes on restart
- ✅ HTTPS encryption
- 💡 Consider adding API authentication

### Best Practices

1. **Use OpenShift route for internal access**
2. **Use ngrok URL only when needed**
3. **Add authentication to sensitive endpoints**
4. **Monitor ngrok web interface for suspicious traffic**
5. **Rotate ngrok authtoken periodically**
6. **Use secrets for sensitive data**

## Cleanup

### Remove Deployment

```bash
# Delete all resources
oc delete all,configmap,secret -l app=product-catalog-api

# Or delete entire project
oc delete project cfai-project
```

## Advanced Configuration

### Custom Ngrok Domain (Paid Plan)

If you have ngrok paid plan with custom domain:

```bash
# Edit deployment
oc edit deployment product-catalog-api

# Update ngrok container command:
command:
- /bin/sh
- -c
- |
  ngrok http http://localhost:8000 \
    --domain=your-custom-domain.ngrok.app \
    --log=stdout
```

### Add Basic Auth to Ngrok

```bash
# Edit deployment
oc edit deployment product-catalog-api

# Update ngrok container command:
command:
- /bin/sh
- -c
- |
  ngrok http http://localhost:8000 \
    --basic-auth="username:password" \
    --log=stdout
```

## Summary

### What You Get

✅ **Two URLs for your API:**
- Internal: `https://product-catalog-api-cfai-project.apps.cfai.cp.fyre.ibm.com`
- External: `https://random-subdomain.ngrok-free.app`

✅ **Confidence Scoring:**
- All endpoints return confidence scores
- Scores range from 0.00 to 1.00
- Based on match quality and context

✅ **Monitoring:**
- OpenShift logs and metrics
- Ngrok web interface for traffic inspection

✅ **Flexibility:**
- Use internal URL for IBM network
- Use external URL for public access
- Both point to the same API

### Quick Reference

```bash
# Deploy
./docs/deployment/deploy-with-ngrok.sh

# Get URLs
oc get routes

# View logs
oc logs -f deployment/product-catalog-api -c api
oc logs -f deployment/product-catalog-api -c ngrok

# Get ngrok URL
NGROK_WEB=$(oc get route product-catalog-api-ngrok-web -o jsonpath='{.spec.host}')
curl -s https://${NGROK_WEB}/api/tunnels | grep public_url

# Restart
oc rollout restart deployment/product-catalog-api

# Delete
oc delete all,configmap,secret -l app=product-catalog-api
```

---

**Need Help?**
- OpenShift: See `docs/deployment/OPENSHIFT_DEPLOYMENT.md`
- Ngrok: See `NGROK_HOSTING_GUIDE.md`
- Confidence Scoring: See `docs/CONFIDENCE_SCORING.md`

**Made with Bob**