# OpenShift Deployment Instructions

## Quick Deploy

Run this single command on **mcpX1** (where you have `oc` CLI access):

```bash
chmod +x openshift-deploy.sh && ./openshift-deploy.sh
```

That's it! The script will:
1. ✅ Create the project
2. ✅ Build the Docker image
3. ✅ Deploy the application
4. ✅ Create the service and route
5. ✅ Test the deployment

## What Gets Deployed

- **Project**: cfai-project
- **Application**: product-catalog-api
- **Replicas**: 2 pods
- **Resources**: 256Mi-512Mi memory, 100m-500m CPU
- **Port**: 8000
- **Health Checks**: Liveness and readiness probes on `/health`
- **TLS**: Automatic HTTPS via OpenShift route

## Prerequisites

1. You must be on **mcpX1** server (or any machine with `oc` CLI)
2. You must be logged in to OpenShift:
   ```bash
   oc login https://api.cfai.cp.fyre.ibm.com:6443
   ```

## After Deployment

The script will display:
- 🌐 Application URL
- 📚 API Documentation URL (`/docs`)
- 💚 Health Check URL (`/health`)

### Access Your API

```bash
# Get the URL
URL=$(oc get route product-catalog-api -o jsonpath='{.spec.host}')

# Test health endpoint
curl -k https://${URL}/health

# View API docs
open https://${URL}/docs  # or visit in browser
```

### Monitor Your Application

```bash
# View pods
oc get pods -l app=product-catalog-api

# View logs
oc logs -f deployment/product-catalog-api

# Check deployment status
oc get deployment product-catalog-api

# View all resources
oc get all -l app=product-catalog-api
```

### Scale Your Application

```bash
# Scale to 3 replicas
oc scale deployment/product-catalog-api --replicas=3

# Scale to 1 replica
oc scale deployment/product-catalog-api --replicas=1
```

### Update Your Application

```bash
# Rebuild and redeploy
oc start-build product-catalog-api --follow

# Or run the deployment script again
./openshift-deploy.sh
```

## Troubleshooting

### Build Fails

```bash
# Check build logs
oc logs -f bc/product-catalog-api

# Check build status
oc get builds

# Describe build
oc describe build product-catalog-api-1
```

### Pods Not Starting

```bash
# Check pod status
oc get pods -l app=product-catalog-api

# View pod logs
POD=$(oc get pods -l app=product-catalog-api -o jsonpath='{.items[0].metadata.name}')
oc logs $POD

# Describe pod
oc describe pod $POD
```

### Application Not Responding

```bash
# Check if pods are ready
oc get pods -l app=product-catalog-api

# Check service
oc get svc product-catalog-api

# Check route
oc get route product-catalog-api

# Test from inside cluster
oc run test --image=busybox --rm -it -- wget -O- http://product-catalog-api:8000/health
```

## Clean Up

To remove everything:

```bash
oc delete all,configmap,secret -l app=product-catalog-api
```

Or delete the entire project:

```bash
oc delete project cfai-project
```

## What the Script Does

1. **Validates** - Checks for `oc` CLI and login status
2. **Creates Project** - Sets up `cfai-project` namespace
3. **Cleans Up** - Removes any existing resources
4. **Creates ConfigMap** - Application configuration
5. **Creates ImageStream** - Container image registry
6. **Creates BuildConfig** - Build instructions
7. **Builds Image** - Compiles your FastAPI application
8. **Creates Deployment** - Runs 2 replicas with health checks
9. **Creates Service** - Internal cluster networking
10. **Creates Route** - External HTTPS access
11. **Tests** - Verifies health endpoint

## File Structure

```
CAFI-product/
├── openshift-deploy.sh          # Main deployment script
├── OPENSHIFT_DEPLOYMENT.md      # This file
├── src/                         # Your FastAPI application
├── config/requirements.txt      # Python dependencies
└── data/product_match_dictionary.json  # Application data
```

## Support

If you encounter issues:

1. Check the script output for error messages
2. View logs: `oc logs -f deployment/product-catalog-api`
3. Check events: `oc get events --sort-by='.lastTimestamp'`
4. Verify cluster health: `oc get nodes`

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Monitor application logs
3. ✅ Set up monitoring/alerting (optional)
4. ✅ Configure autoscaling (optional)
5. ✅ Set up CI/CD pipeline (optional)

---

**Ready to deploy?** Run on mcpX1:

```bash
chmod +x openshift-deploy.sh && ./openshift-deploy.sh