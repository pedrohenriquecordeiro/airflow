# Spark Operator Deployment on GKE

This directory contains scripts and manifests to deploy the Spark Operator on Google Kubernetes Engine (GKE), enabling Airflow to submit and manage Spark jobs on your cluster.

## Structure

- `main.sh` – Script to automate Spark Operator setup and RBAC configuration
- `sa-data-stack-v3.json` – GCP service account key (used for secrets)
- `manifest/` – Kubernetes manifests and Helm values
  - `helm/` – Helm values for Spark Operator
  - `rbac/` – RBAC and service account manifests

## Quick Start

1. **Run the setup script to deploy Spark Operator:**
   ```sh
   ./main.sh
   ```

2. **What the script does:**
   - Creates the `spark` namespace
   - Creates a Kubernetes secret with GCP credentials
   - Applies service account and RBAC manifests
   - Installs or upgrades the Spark Operator using Helm
   - Applies cluster role bindings so Airflow can submit Spark jobs

3. **Customize Helm values:**
   - Edit `manifest/helm/values-spark-operator.yaml` as needed before running the script.

## RBAC and Permissions

- The Spark Operator and Airflow require appropriate permissions to manage Spark jobs.
- See [`manifest/rbac/cluster_role_binding_spark.yaml`](manifest/rbac/cluster_role_binding_spark.yaml) for cluster role bindings.

## References

- [Spark Operator Helm Chart](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator)
- [Apache Spark on Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html)