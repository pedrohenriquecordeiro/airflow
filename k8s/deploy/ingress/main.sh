#!/bin/bash

set -e

# --- NGINX Ingress Controller Setup ---

# Create namespace for nginx
kubectl create namespace nginx || true

# Add ingress-nginx Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# Install or upgrade ingress-nginx controller
helm upgrade --install ingress-controller ingress-nginx/ingress-nginx \
    --version 4.12.1 \
    -f ingress/nginx-controller/manifest/helm/values-nginx-2-0-1.yaml \
    --namespace nginx

# --- Cert-Manager Setup ---

# Create namespace for cert-manager
kubectl create namespace cert-manager || true

# Apply cert-manager CRDs
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.1/cert-manager.crds.yaml

# Add cert-manager Helm repo
helm repo add cert-manager https://charts.jetstack.io

# Install or upgrade cert-manager
helm upgrade --install cert-manager cert-manager/cert-manager \
    --version 1.17.1 \
    -f ingress/cert-manager/manifest/helm/values-cert-manager-1-17-1.yaml \
    --namespace cert-manager

# Apply ClusterIssuer for Let's Encrypt
kubectl apply -f ingress/cert-manager/manifest/clusterissuer-letsencrypt.yaml -n cert-manager

# --- Airflow Ingress ---

kubectl apply -f ingress/nginx-controller/manifest/airflow-ingress.yaml -n airflow

# --- Cleanup Section (Uncomment to use) ---

# # Remove ClusterIssuer and uninstall cert-manager
# kubectl delete -f ingress/cert-manager/manifest/clusterissuer-letsencrypt.yaml -n cert-manager
# helm uninstall cert-manager --namespace cert-manager

# # Remove Airflow ingress and uninstall ingress controller
# kubectl delete -f ingress/nginx-controller/manifest/airflow-ingress.yaml -n airflow
# helm uninstall ingress-controller --namespace nginx

# --- Notes ---
# - HTTP-01 challenge happens after applying the Ingress with cert-manager.io/cluster-issuer annotation and TLS section.
# - Ensure DNS points to your Ingress IP and port 80 is open.
# - On GKE, LoadBalancer and firewall rules are usually created automatically, so make sure if the firewall rules are temporarily open.
# - Check certificate status: kubectl get certificate airflow-webserver-tls -n airflow
