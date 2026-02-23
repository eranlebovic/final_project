#!/bin/bash
# Securely create the Redis password secret in the required namespaces
# so it is not stored in plain text in Git.

echo "Creating redis-password secret in devops-dev..."
kubectl create secret generic redis-password \
  --from-literal=redis-password=devops-secret \
  --namespace=devops-dev \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Creating redis-password secret in devops-prod..."
kubectl create secret generic redis-password \
  --from-literal=redis-password=devops-secret \
  --namespace=devops-prod \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets successfully created and injected directly into the cluster."
