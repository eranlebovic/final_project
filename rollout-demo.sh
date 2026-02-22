#!/bin/bash

# Configuration
APP_NAME="frontend-prod"
NAMESPACE="devops-prod"
ROLLOUT_NAME="frontend-ui"
VALUES_FILE="apps/frontend/frontend-chart/values.yaml"

echo "========================================="
echo " Argo Rollouts Progressive Delivery Demo "
echo "========================================="
echo "This scripts demonstrates a Canary deployment strategy,"
echo "pausing at 20% traffic before manual promotion."
echo ""

read -p "Press Enter to start a Canary Rollout for ${APP_NAME}..."
echo ""
echo "[1/4] Updating the Helm values with a new image tag..."
# Replace the image tag with a new tag to trigger a rollout
sed -i 's/tag: .*/tag: "v-canary-demo"/g' ${VALUES_FILE}

git add ${VALUES_FILE}
git commit -m "feat: Deploying new canary image tag to frontend-prod"
git push

echo ""
echo "Triggering ArgoCD Sync to start the Rollout..."
kubectl patch application ${APP_NAME} -n argocd --type merge -p '{"operation": {"sync": {"revision": "HEAD", "syncStrategy": {"hook": {}}}}}' > /dev/null 2>&1

echo "Waiting 30 seconds for ArgoCD to sync and the Rollout to reach the first pause state..."
sleep 30

echo ""
echo "[2/4] Checking Rollout status (Expected: Paused at 20% Weight)..."
kubectl argo rollouts get rollout ${ROLLOUT_NAME} -n ${NAMESPACE}

echo ""
echo "Notice the Rollout is paused. Only a fraction of the pods are running the new version."
read -p "Press Enter to promote the Rollout to 100%..."

echo ""
echo "[3/4] Promoting the Rollout manually..."
kubectl argo rollouts promote ${ROLLOUT_NAME} -n ${NAMESPACE}

echo "Waiting 30 seconds for the Rollout to fully scale up..."
sleep 30

echo ""
echo "[4/4] Verifying the Rollout succeeded..."
kubectl argo rollouts get rollout ${ROLLOUT_NAME} -n ${NAMESPACE}

echo ""
echo "========================================="
echo "          Rollout Demo Complete          "
echo "========================================="
