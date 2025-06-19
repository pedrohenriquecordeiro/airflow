# Airflow Deployment on GKE

This repository contains scripts and manifests to deploy Apache Airflow on Google Kubernetes Engine (GKE) with NGINX Ingress, cert-manager and integration with Google Cloud services.

## Structure

- `deploy/airflow/` – Airflow deployment scripts, Dockerfile, and manifests
- `deploy/ingress/` – NGINX Ingress and cert-manager setup scripts and manifests
- `deploy/redis/` – Redis deployment scripts and manifests
- `deploy/spark-operator/` – Spark Operator deployment scripts and manifests

## Quick Start

1. **Clone the repository**
2. **Build the Airflow Docker image**
   ```sh
   cd deploy/airflow/docker
   docker build -t your-airflow-image:latest .
   ```
3. **Deploy Airflow and dependencies**
   ```sh
   cd ../../
   ./main.sh
   ```
4. **Set up Ingress and TLS**
   ```sh
   cd ../ingress
   ./main.sh
   ```

## Documentation

- See `deploy/airflow/docs/` for guides on logging, ingress, and Git sync.
- See `deploy/ingress/readme.md` for Ingress and cert-manager setup details.
- See `deploy/spark-operator/README.md` for Spark Operator integration.

## Requirements

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/)
- Access to a GKE cluster

## License

MIT License