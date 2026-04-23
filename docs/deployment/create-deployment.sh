#!/bin/bash

##############################################################################
# Create OpenShift Deployment with Ngrok Sidecar
# Run this after the build completes successfully
##############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_NAME="cfai-project"
APP_NAME="product-catalog-api"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Creating Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if in correct project
oc project ${PROJECT_NAME}

# Get ngrok authtoken
echo -e "${BLUE}Enter your ngrok authtoken:${NC}"
read -s NGROK_AUTHTOKEN
echo ""

if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo -e "${RED}Ngrok authtoken is required${NC}"
    exit 1
fi

# Create or update secret
echo -e "${BLUE}Creating ngrok secret...${NC}"
oc delete secret ngrok-auth --ignore-not-found=true
oc create secret generic ngrok-auth --from-literal=NGROK_AUTHTOKEN="${NGROK_AUTHTOKEN}"
oc label secret ngrok-auth app=${APP_NAME}
echo -e "${GREEN}✓ Secret created${NC}"

# Create ConfigMap if not exists
echo -e "${BLUE}Creating ConfigMap...${NC}"
if ! oc get configmap product-catalog-config &> /dev/null; then
    oc create configmap product-catalog-config \
        --from-literal=APP_ENV=production \
        --from-literal=LOG_LEVEL=INFO \
        --from-literal=PORT=8000
    oc label configmap product-catalog-config app=${APP_NAME}
fi
echo -e "${GREEN}✓ ConfigMap ready${NC}"

# Get image reference
IMAGE=$(oc get is/${APP_NAME} -o jsonpath='{.status.dockerImageRepository}'):latest
echo -e "${BLUE}Using image: ${IMAGE}${NC}"

# Create deployment
echo -e "${BLUE}Creating deployment...${NC}"
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
        image: ${IMAGE}
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
echo -e "${GREEN}✓ Deployment created${NC}"

# Create Service
echo -e "${BLUE}Creating Service...${NC}"
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
echo -e "${GREEN}✓ Service created${NC}"

# Create Routes
echo -e "${BLUE}Creating Routes...${NC}"
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
echo -e "${GREEN}✓ Routes created${NC}"

# Wait for deployment
echo ""
echo -e "${BLUE}Waiting for deployment...${NC}"
oc rollout status deployment/${APP_NAME} --timeout=5m

# Get URLs
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

OPENSHIFT_URL=$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}')
NGROK_WEB=$(oc get route ${APP_NAME}-ngrok-web -o jsonpath='{.spec.host}')

echo -e "${BLUE}OpenShift Route:${NC} https://${OPENSHIFT_URL}"
echo -e "${BLUE}Ngrok Web Interface:${NC} https://${NGROK_WEB}"

# Wait for ngrok
echo ""
echo -e "${BLUE}Waiting for ngrok tunnel...${NC}"
sleep 15

NGROK_URL=$(curl -s https://${NGROK_WEB}/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4 | head -1)
if [ -n "$NGROK_URL" ]; then
    echo -e "${BLUE}Ngrok Public URL:${NC} ${NGROK_URL}"
else
    echo -e "${BLUE}Check ngrok web interface for public URL${NC}"
fi

# Test
echo ""
echo -e "${BLUE}Testing API...${NC}"
if curl -k -s "https://${OPENSHIFT_URL}/health" | grep -q "ok"; then
    echo -e "${GREEN}✓ API is responding!${NC}"
else
    echo -e "${BLUE}API starting up... check logs:${NC}"
    echo "  oc logs -f deployment/${APP_NAME} -c api"
fi

echo ""
echo -e "${GREEN}Done!${NC}"

# Made with Bob
