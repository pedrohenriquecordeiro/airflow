## SPARK OPERATOR SETUP

# Create namespace for Spark (ignore error if it already exists)
kubectl create namespace spark || echo "Namespace 'spark' already exists."

# Create secret with service account credentials (replace with your actual key file)
kubectl create secret generic data-stack-secret \
  --from-file=key.json=sa-data-stack-v3.json \
  -n spark

# Apply RBAC for Airflow service account in Spark namespace
kubectl apply -f manifest/rbac/service-account-airflow.yaml -n spark

# Add Spark Operator Helm repo (force update to get latest charts)
helm repo add spark-operator https://kubeflow.github.io/spark-operator --force-update

# Install Spark Operator via Helm with custom values (wait for completion)
helm install spark-operator spark-operator/spark-operator \
  --wait \
  -f spark-operator/manifest/helm/values-spark-operator.yaml \
  --namespace spark

# Upgrade Spark Operator release with updated values if needed (wait for completion)
helm upgrade spark-operator spark-operator/spark-operator \
  --wait \
  -f spark-operator/manifest/helm/values-spark-operator.yaml \
  --namespace spark

# Apply ClusterRoleBinding so Airflow can run jobs in the Spark namespace
kubectl apply -f infra/manifests/kubernetes/rbac/cluster_role_binding_spark.yaml \
  -n spark

# (Optional) Configure Airflow UI to connect with the Kubernetes cluster
# This step depends on your Airflow deployment and is not automated here.

# (Optional) Develop your DAG to submit Spark jobs
# Place your DAG code in the appropriate Airflow DAGs directory.

