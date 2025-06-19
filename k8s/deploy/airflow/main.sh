#!/bin/bash
# APACHE AIRFLOW - SETUP WITH KUBERNETES AND HELM

# Step 1: Create namespace
kubectl create namespace airflow

# Step 2: Create webserver secret (random key for Airflow webserver)
kubectl create secret generic webserver-secret \
  --from-literal="webserver-secret-key=$(python3 -c 'import secrets; print(secrets.token_hex(16))')" \
  -n airflow

# Step 3: Create GCS (service account key for GCS)
kubectl create secret generic data-stack-secret \
  --from-file=key.json=sa-data-stack-v3.json \
  -n airflow


# Step 4: GCS bucket IAM policy binding (run manually if needed)
# This command grants Airflow service account access to the GCS bucket
gcloud storage buckets add-iam-policy-binding gs://default-logs-apache-airflow \
  --member="principal://iam.googleapis.com/projects/247888593708/locations/global/workloadIdentityPools/dw-default-dev.svc.id.goog/subject/ns/airflow/sa/airflow-service-account" \
  --role="roles/storage.objectAdmin"

# Step 5: Apply additional Kubernetes secrets (e.g., GitLab SSH key)
kubectl apply -f airflow/manifest/k8s.yaml -n airflow

# Step 6: Build and push Docker image for Airflow with custom extensions
docker build -f airflow/docker/Dockerfile \
  -t phcjesus/apache-airflow-with-extensions:v0.1.2 \
  airflow/docker/ && \
docker push phcjesus/apache-airflow-with-extensions:v0.1.2

# Step 7: Helm setup

# Add (or update) Apache Airflow Helm repo
helm repo add apache-airflow https://airflow.apache.org/ --force-update

export $(grep -v '^#' airflow/.env | xargs) # Load environment variables from .env file (.env contains the Gmail app password)

# Install Airflow via Helm (initial install)
helm upgrade --install airflow apache-airflow/airflow \
  --version 1.16.0 \
  -f airflow/manifest/helm/values-airflow-1-16-0.yaml \
  --namespace airflow \
  --set config.smtp.smtp_password="$SMTP_MAILGUN_PASSWORD"