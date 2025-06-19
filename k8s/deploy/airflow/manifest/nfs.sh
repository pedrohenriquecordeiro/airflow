# 1 provide a compute engines instance ( set to use the same VPC network as the Airflow instance )

# 2 install NFS server and criate exports for postgres and airflow logs
sudo apt-get update
sudo apt-get install -y nfs-kernel-server nfs-common
sudo mkdir -p /exports/postgres
sudo mkdir -p /exports/airflow-logs
sudo chown -R nobody:nogroup /exports/postgres /exports/airflow-logs
sudo chmod -R 777 /exports/postgres /exports/airflow-logs


echo "/exports/postgres 10.0.0.0/24(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports      ## 10.0.0.0/24 => this is the CIDR notation for the VPC network range
echo "/exports/airflow-logs 10.0.0.0/24(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports

sudo exportfs -rav

sudo systemctl restart nfs-kernel-server
sudo systemctl status nfs-kernel-server

# 3 Create a rule to allow TCP/UDP on port 2049 (NFS) and 111 (RPC binder) from your cluster’s network range
# source range must be the same as the VPC network range

# 4 create the storageclasse, PVs and PVCs for postgres and airflow logs
kubectl apply -f airflow/manifests/nfs.yaml

# 5 deploy the external postgreSQL
kubectl apply -f postgre/postgres.yaml

# 6 create a database called "airflow" in the external postgreSQL instance
kubectl exec -n airflow -it $(kubectl get pod -n airflow -l app=airflow-postgresql -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U admin -c "CREATE DATABASE airflow OWNER admin;"

# 7 deploy the Airflow instance with helm chart