# Redis Deployment on GKE

This directory contains scripts and manifests to deploy Redis on Google Kubernetes Engine (GKE) using the Bitnami Helm chart.

## Structure

- `main.sh` – Script to install and upgrade Redis using Helm
- `redis.sh` – Helper script for retrieving the Redis password and basic Redis CLI commands
- `manifest/` – Contains Helm values and additional manifest files

## Quick Start

1. **Create the Redis namespace and deploy Redis:**
   ```sh
   ./main.sh
   ```

2. **Retrieve the Redis password:**
   ```sh
   export REDIS_PASSWORD=$(kubectl get secret --namespace redis redis -o jsonpath="{.data.redis-password}" | base64 -d)
   ```

3. **Access Redis CLI:**
   ```sh
   kubectl run -i --tty --rm redis-client --image=bitnami/redis --namespace redis --command -- redis-cli -h redis-master -a $REDIS_PASSWORD
   ```

## Configuration

- Helm values can be customized in `manifest/helm/values.yaml`.
- Default values are provided in `manifest/helm/default/default.yaml`.

## Useful Commands

- List all keys:
  ```
  KEYS *
  ```
- Set a value:
  ```
  SET mykey "some value"
  ```
- Get a value:
  ```
  GET mykey
  ```

## References

- [Bitnami Redis Helm Chart](https://artifacthub.io/packages/helm/bitnami/redis)
- [Redis Documentation](https://redis.io/documentation/)