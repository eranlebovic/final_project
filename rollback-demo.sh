#!/bin/bash

# Configuration
APP_NAME="frontend-prod"
NAMESPACE="devops-prod"
DEPLOYMENT_LABEL="app=frontend-ui"
VALUES_FILE="apps/frontend/frontend-chart/values.yaml"

echo "========================================="
echo "   ArgoCD GitOps Rollback Demo (Bonus 4) "
echo "========================================="
echo "Note: This environment runs on HDDs, so disk I/O, syncing,"
echo "and pod scheduling (ImagePull, ContainerCreating) may take extra time."
echo "Wait times have been adjusted accordingly."
echo ""

read -p "Press Enter to purposefully break the ${APP_NAME} deployment..."
echo ""
echo "[1/4] Injecting a broken image tag into the Helm values..."
# Replace the image tag with a nonexistent one
sed -i 's/tag: .*/tag: "v-broken-demo"/g' ${VALUES_FILE}

git add ${VALUES_FILE}
git commit -m "BREAKING CHANGE: Deploying non-existent image tag to frontend-prod"
git push

echo ""
echo "Triggering ArgoCD Sync to deploy the broken manifest..."
kubectl patch application ${APP_NAME} -n argocd --type merge -p '{"operation": {"sync": {"revision": "HEAD", "syncStrategy": {"hook": {}}}}}' > /dev/null 2>&1

echo "Waiting 45 seconds for the cluster to attempt pulling the broken image..."
echo "(Considering HDD speeds for scheduling and image pull attempts)"
sleep 45

echo ""
echo "Checking Pod status in ${NAMESPACE} namespace (Expected result: ImagePullBackOff / ErrImagePull)..."
kubectl get pods -n ${NAMESPACE} -l ${DEPLOYMENT_LABEL}

echo ""
read -p "Press Enter to perform a GitOps rollback..."

echo ""
echo "[2/4] Reverting the breaking commit in Git..."
git revert HEAD --no-edit
git push

echo ""
echo "Triggering ArgoCD Sync to apply the rollback..."
kubectl patch application ${APP_NAME} -n argocd --type merge -p '{"operation": {"sync": {"revision": "HEAD", "syncStrategy": {"hook": {}}}}}' > /dev/null 2>&1

echo "Waiting 60 seconds for the cluster to terminate broken pods and schedule healthy ones..."
echo "(Considering HDD speeds for container termination and creation)"
sleep 60

echo ""
echo "[3/4] Verifying the rollback succeeded..."
kubectl get pods -n ${NAMESPACE} -l ${DEPLOYMENT_LABEL}

echo ""
echo "========================================="
echo "          Rollback Demo Complete         "
echo "========================================="
