# OpenShift Deployment with ngrok Tunneling

This guide explains how to deploy the CAFI Product API to OpenShift with ngrok tunneling for external access.

## 🎯 Overview

This deployment creates:
- **CAFI Product API**: Python Flask application running on port 8000
- **ngrok Tunnel**: Provides public HTTPS URL to access the API
- **Namespace**: Isolated environment `cafi-product`

## 📋 Prerequisites

1. **OpenShift CLI (oc)** installed
   ```bash
   # Download from: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html
   ```

2. **Access to OpenShift Cluster**
   - Login credentials
   - Cluster URL

3. **ngrok Account**
   - Auth token (already configured in deployment)
   - Free tier is sufficient

## 🚀 Quick Deployment

### Option 1: Using Deployment Script (Recommended)

```bash
# Make script executable
chmod +x deploy-to-openshift.sh

# Run deployment
./deploy-to-openshift.sh
```

### Option 2: Manual Deployment

```bash
# 1. Login to OpenShift
oc login <your-cluster-url>

# 2. Create namespace
oc create namespace cafi-product
oc project cafi-product

# 3. Create ConfigMap with application code
oc create configmap cafi-product-code \
  --from-file=app.py \
  --from-file=config/requirements.txt \
  --from-file=src/

# 4. Apply deployment
oc apply -f openshift-deployment.yaml

# 5. Wait for deployments
oc rollout status deployment/cafi-product-api
oc rollout status deployment/ngrok-tunnel
```

## 🔍 Getting the ngrok Public URL

After deployment, get the ngrok public URL:

```bash
# Get ngrok pod name
NGROK_POD=$(oc get pods -l app=ngrok -o jsonpath='{.items[0].metadata.name}')

# View ngrok logs to find the public URL
oc logs $NGROK_POD | grep "url="

# Or use this one-liner
oc logs -l app=ngrok | grep -o 'https://[a-z0-9-]*\.ngrok-free\.app'
```

Example output:
```
https://abc123def456.ngrok-free.app
```

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl https://<your-ngrok-url>/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-23T11:00:00Z"
}
```

### 2. Search Products
```bash
curl -X POST https://<your-ngrok-url>/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop",
    "top_k": 5
  }'
```

### 3. Get All Products
```bash
curl https://<your-ngrok-url>/products
```

## 📊 Monitoring and Logs

### View API Logs
```bash
# Follow API logs
oc logs -f deployment/cafi-product-api

# View recent logs
oc logs deployment/cafi-product-api --tail=100
```

### View ngrok Logs
```bash
# Follow ngrok logs
oc logs -f deployment/ngrok-tunnel

# View recent logs
oc logs deployment/ngrok-tunnel --tail=50
```

### Check Pod Status
```bash
# List all pods
oc get pods

# Describe a specific pod
oc describe pod <pod-name>

# Get pod events
oc get events --sort-by='.lastTimestamp'
```

## 🔧 Troubleshooting

### API Pod Not Starting

```bash
# Check pod status
oc get pods -l app=cafi-product

# View pod logs
oc logs -l app=cafi-product

# Describe pod for events
oc describe pod -l app=cafi-product
```

### ngrok Tunnel Not Connecting

```bash
# Check ngrok pod logs
oc logs -l app=ngrok

# Verify ngrok secret
oc get secret ngrok-secret -o yaml

# Restart ngrok deployment
oc rollout restart deployment/ngrok-tunnel
```

### Service Not Accessible

```bash
# Check service
oc get svc cafi-product-service

# Test internal connectivity
oc run test-pod --image=curlimages/curl --rm -it -- curl http://cafi-product-service:8000/health
```

## 🔄 Updating the Deployment

### Update Application Code

```bash
# Update ConfigMap with new code
oc create configmap cafi-product-code \
  --from-file=app.py \
  --from-file=config/requirements.txt \
  --from-file=src/ \
  --dry-run=client -o yaml | oc apply -f -

# Restart deployment to pick up changes
oc rollout restart deployment/cafi-product-api
```

### Update ngrok Token

```bash
# Update secret
oc create secret generic ngrok-secret \
  --from-literal=authtoken='<new-token>' \
  --dry-run=client -o yaml | oc apply -f -

# Restart ngrok
oc rollout restart deployment/ngrok-tunnel
```

## 📈 Scaling

### Scale API Replicas
```bash
# Scale to 3 replicas
oc scale deployment/cafi-product-api --replicas=3

# Verify scaling
oc get pods -l app=cafi-product
```

**Note**: Keep ngrok at 1 replica (multiple ngrok instances will create multiple tunnels)

## 🗑️ Cleanup

### Delete Entire Deployment
```bash
# Delete namespace (removes everything)
oc delete namespace cafi-product
```

### Delete Specific Resources
```bash
# Delete deployments only
oc delete deployment cafi-product-api ngrok-tunnel

# Delete service
oc delete service cafi-product-service

# Delete secrets
oc delete secret ngrok-secret

# Delete configmap
oc delete configmap cafi-product-code
```

## 🔐 Security Considerations

1. **ngrok Auth Token**: Stored as Kubernetes Secret
2. **Network Policies**: Consider adding network policies for production
3. **HTTPS**: ngrok provides HTTPS by default
4. **Rate Limiting**: ngrok free tier has rate limits
5. **Authentication**: Add API authentication for production use

## 📝 Architecture

```
┌─────────────────────────────────────────┐
│         OpenShift Cluster               │
│  ┌───────────────────────────────────┐  │
│  │  Namespace: cafi-product          │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐ │  │
│  │  │  cafi-product-api           │ │  │
│  │  │  (Python Flask App)         │ │  │
│  │  │  Port: 8000                 │ │  │
│  │  └──────────┬──────────────────┘ │  │
│  │             │                     │  │
│  │  ┌──────────▼──────────────────┐ │  │
│  │  │  cafi-product-service       │ │  │
│  │  │  (ClusterIP)                │ │  │
│  │  └──────────┬──────────────────┘ │  │
│  │             │                     │  │
│  │  ┌──────────▼──────────────────┐ │  │
│  │  │  ngrok-tunnel               │ │  │
│  │  │  (ngrok container)          │ │  │
│  │  └──────────┬──────────────────┘ │  │
│  └─────────────┼───────────────────┘  │
└────────────────┼──────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │  ngrok Cloud  │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  Public URL   │
         │  https://...  │
         └───────────────┘
```

## 🆘 Support

For issues or questions:
1. Check pod logs: `oc logs <pod-name>`
2. Check events: `oc get events`
3. Verify resources: `oc get all`
4. Review ngrok dashboard: https://dashboard.ngrok.com

## 📚 Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [ngrok Documentation](https://ngrok.com/docs)
- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)