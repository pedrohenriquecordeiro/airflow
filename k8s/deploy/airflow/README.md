# Airflow Deployment on GKE

This directory contains scripts and manifests to deploy Apache Airflow on Google Kubernetes Engine (GKE) using Helm, with support for Google Cloud Storage (GCS) logging and integration with GCS Fuse CSI.

## Structure

- `main.sh` – Script to automate Airflow setup and secret creation
- `sa-data-stack-v3.json` – GCP service account key (used for secrets)
- `docker/` – Airflow Docker image and related files
- `manifest/` – Kubernetes manifests and Helm values

## Quick Start

1. **Build the Airflow Docker image**
   ```sh
   cd docker
   docker build -t your-airflow-image:latest .
   ```

2. **Run the setup script**
   ```sh
   cd ..
   ./main.sh
   ```

3. **Deploy Airflow using Helm**
   - Edit the values in `manifest/helm/values-airflow-1-16-0.yaml` as needed.
   - Deploy with:
     ```sh
     helm upgrade --install airflow manifest/helm \
       -n airflow \
       -f manifest/helm/values-airflow-1-16-0.yaml
     ```


<br><br><br><br><br>

# Git Sync Configuration (Git Sync Integration)

Follow these steps to configure Git synchronization with GitLab.

---

## Step 1: Create a New GitLab System User

This step is handled by the **Cybersecurity team**.

---

## Step 2: Generate a New SSH Key Pair

Run the following command to generate an SSH key pair:

```bash
ssh-keygen -t rsa -b 4096 -C "dados.git@default.com.br"
```

This will create two files:
- `id_rsa`: The private key  
- `id_rsa.pub`: The public key

---

## Step 3: Add the Public Key to GitLab

1. Navigate to **GitLab > User Menu > SSH Keys**.
2. Paste the contents of the `id_rsa.pub` file into the provided field.

---

## Step 4: Test the SSH Connection

1. Start the SSH agent:

  ```bash
  eval "$(ssh-agent -s)"
  ```

2. Add the private key to the agent:

  ```bash
  ssh-add id_rsa
  ```

3. Test the connection to GitLab:

  ```bash
  ssh -T git@gitlab.com
  ```

---

## Step 5: Encode the Private Key in Base64

Convert the private key to Base64 format:

```bash
cat id_rsa | base64 > base.txt
```

---

## Step 6: Create a Kubernetes Secret Using the Private Key

Create a Kubernetes secret to store the private key:

```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: gitlab-ssh-secret
  annotations:
  description: "Private key for GitLab repository - user dados.git@default.com.br"
data:
  gitSshKey: "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0..."
EOF
```

Replace the `gitSshKey` value with the Base64-encoded private key from `base.txt`.

---

## Step 7: Reference the Secret in the Airflow Manifest

Update your Airflow manifest to reference the Kubernetes secret:

```yaml
dags:
  gitSync:
  sshKeySecret: gitlab-ssh-secret
```

---

## Step 8: Add GitLab’s Public Key to Known Hosts

1. Retrieve GitLab’s public key:

  ```bash
  ssh-keyscan -t rsa gitlab.com > gitlab_public_key
  ```

2. Verify the key:

  ```bash
  ssh-keygen -lf gitlab_public_key
  ```

3. View the contents of the key:

  ```bash
  cat gitlab_public_key
  ```

4. Add the key to your Airflow manifest:

  ```yaml
  dags:
    gitSync:
    knownHosts: |
      [contents of gitlab_public_key]
  ```

Replace `[contents of gitlab_public_key]` with the actual contents of the `gitlab_public_key` file.

---

By following these steps, you will successfully configure Git synchronization with GitLab.

---

<br><br><br><br><br>

# GKE - GCS Fuse CSI Integration Guide (GCS Logging Integration)

**Reference**: [Cloud Storage FUSE CSI Driver - GCP Docs](https://cloud.google.com/kubernetes-engine/docs/how-to/persistent-volumes/cloud-storage-fuse-csi-driver?_gl=1*12gq1nf*_ga*MTk4NTcyODQ3OS4xNzM2OTYzNTMw*_ga_WH2QY8WWF5*MTc0MTMwMDM4Ny4xNTUuMS4xNzQxMzA2NDQ0LjYwLjAuMA..&hl=pt-br)

---

## 1. Create Kubernetes Service Account

Apply the Kubernetes service account manifest:

```yaml
kubectl apply -f infra/manifests/rbac/service-account-airflow.yaml
```

---

## 2. Link Kubernetes Service Account with GCP Service Account

> This step is usually done by the security (cyber) team.

- Ensure the GCP service account has the necessary roles.
- Example command to check roles:

```bash
gcloud storage buckets get-iam-policy gs://default-logs-apache-airflow --format=json
```

- Example to remove existing binding:

```bash
gcloud storage buckets remove-iam-policy-binding gs://default-logs-apache-airflow \
  --member "principal://iam.googleapis.com/projects/247888593708/locations/global/workloadIdentityPools/dw-default-dev.svc.id.goog/subject/ns/airflow/sa/airflow-service-account" \
  --role "roles/storage.objectAdmin"
```

- Command to add IAM binding:

```bash
gcloud storage buckets add-iam-policy-binding gs://BUCKET_NAME \
  --member "principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/NAMESPACE/sa/KSA_NAME" \
  --role "ROLE_NAME"
```

- Example:

```bash
gcloud storage buckets add-iam-policy-binding gs://default-logs-apache-airflow \
  --member "principal://iam.googleapis.com/projects/247888593708/locations/global/workloadIdentityPools/dw-default-dev.svc.id.goog/subject/ns/airflow/sa/airflow-service-account" \
  --role "roles/storage.objectAdmin"
```

---

## 3. Create Persistent Volume and Persistent Volume Claim

Apply the PV and PVC manifests:

```bash
kubectl apply -f infra/manifests/pv/pv-gcs-fuse.yaml
kubectl apply -f infra/manifests/pvc/pvc-gcs-fuse.yaml
```

---

## 4. Enable Pod Activation for GCS Fuse

Add the required annotation to your Helm chart components under `podAnnotations`.

**Example:**

```yaml
podAnnotations:
  gke-gcsfuse/volumes: "true"
```

---

## 5. Add Service Account to Your Services

Set the service account and add it to the Helm chart:

**Example:**

```yaml
serviceAccount:
  create: false
  name: airflow-service-account
```

---

## 6. Configure Logging to Use the PVC

In your Helm chart, point logging to the previously created PVC.

**Example:**

```yaml
logs:
  persistence:
    enabled: true
    size: 5Gi
    existingClaim: gcs-fuse-csi-pvc
```

