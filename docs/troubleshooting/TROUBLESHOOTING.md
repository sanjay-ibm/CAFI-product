# Troubleshooting Guide - Product Catalog API

## Image Pull Failures During OpenShift Build

### Problem
Build fails with error:
```
Failed to stream the build logs - to view the logs, run oc logs build/product-catalog-api-1
Copying blob sha256:... [fails partway through]
```

### Root Causes
1. **Network timeouts** - Transient network issues between OpenShift and Red Hat registry
2. **Insufficient build resources** - Build pod doesn't have enough CPU/memory
3. **Registry connectivity** - Temporary registry unavailability
4. **Image layer corruption** - Partial download of image layers

### Solutions Implemented

#### 1. Use Specific Image Version (Dockerfile)
Changed from `latest` tag to specific version `1-117`:
```dockerfile
FROM registry.access.redhat.com/ubi9/python-311:1-117
```
**Why**: Specific versions are more stable and cacheable than `latest` tags.

#### 2. Build Resource Limits (deploy.sh)
Added resource requests and limits to build config:
```yaml
resources:
  limits:
    cpu: "1"
    memory: "2Gi"
  requests:
    cpu: "500m"
    memory: "1Gi"
```
**Why**: Ensures build pod has sufficient resources to complete image pulls.

#### 3. Build Timeout Extension (deploy.sh)
Set `completionDeadlineSeconds: 1800` (30 minutes)
**Why**: Gives more time for slow image pulls to complete.

#### 4. Automatic Retry Logic (deploy.sh)
Build automatically retries once if it fails:
```bash
oc start-build ${APP_NAME} --from-dir=. --follow --wait || {
    echo "Build failed, attempting retry..."
    sleep 5
    oc start-build ${APP_NAME} --from-dir=. --follow --wait
}
```
**Why**: Handles transient network issues automatically.

### Manual Troubleshooting Steps

#### Check Build Logs
```bash
# List all builds
oc get builds

# View logs for specific build
oc logs build/product-catalog-api-1

# Follow logs in real-time
oc logs -f build/product-catalog-api-1
```

#### Check Build Config
```bash
# View build config
oc describe bc/product-catalog-api

# Check build pod resources
oc get pods | grep build
oc describe pod product-catalog-api-1-build
```

#### Manual Retry
```bash
# Cancel stuck build
oc cancel-build product-catalog-api-1

# Start new build
oc start-build product-catalog-api --from-dir=. --follow
```

#### Delete and Recreate Build Config
```bash
# Delete existing build config
oc delete bc/product-catalog-api

# Recreate (will be done automatically by deploy.sh)
./deploy.sh
```

### Alternative Solutions

#### Option 1: Use Different Base Image
If Red Hat registry continues to have issues, consider:
```dockerfile
# Python official image (Docker Hub)
FROM python:3.11-slim

# Or Alpine-based for smaller size
FROM python:3.11-alpine
```

#### Option 2: Pre-pull Image to Internal Registry
```bash
# Import image to OpenShift internal registry
oc import-image python-311 \
  --from=registry.access.redhat.com/ubi9/python-311:1-117 \
  --confirm

# Update Dockerfile to use internal registry
FROM image-registry.openshift-image-registry.svc:5000/cfai-project/python-311:1-117
```

#### Option 3: Use ImageStream
Create an ImageStream for better caching:
```yaml
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: python-311
spec:
  lookupPolicy:
    local: true
  tags:
  - name: "1-117"
    from:
      kind: DockerImage
      name: registry.access.redhat.com/ubi9/python-311:1-117
    importPolicy:
      scheduled: true
```

### Network-Related Issues

#### Check Registry Connectivity
```bash
# From build pod, test registry access
oc debug bc/product-catalog-api
curl -I https://registry.access.redhat.com/v2/
```

#### Configure Proxy (if behind corporate firewall)
Update build config with proxy settings:
```bash
oc set env bc/product-catalog-api \
  HTTP_PROXY=http://proxy.example.com:8080 \
  HTTPS_PROXY=http://proxy.example.com:8080 \
  NO_PROXY=.cluster.local,.svc,localhost,127.0.0.1
```

### Prevention Best Practices

1. **Use specific image versions** instead of `latest`
2. **Set appropriate resource limits** for build pods
3. **Implement retry logic** for transient failures
4. **Monitor build times** and adjust timeouts accordingly
5. **Cache base images** in internal registry when possible
6. **Test builds** in non-production environment first

### Getting Help

If issues persist:
1. Check OpenShift cluster status
2. Verify network connectivity to Red Hat registries
3. Review cluster-wide image pull policies
4. Contact OpenShift cluster administrators
5. Check Red Hat registry status: https://status.redhat.com/

### Related Documentation
- [OpenShift Build Configuration](https://docs.openshift.com/container-platform/latest/cicd/builds/build-configuration.html)
- [Red Hat Container Registry](https://access.redhat.com/containers/)
- [Troubleshooting Builds](https://docs.openshift.com/container-platform/latest/cicd/builds/troubleshooting-builds.html)