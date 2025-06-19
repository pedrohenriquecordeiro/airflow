kubectl create namespace redis


helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install redis bitnami/redis \
    --version 20.13.3\
    -f redis/manifest/helm/values.yaml \
    --namespace redis


helm upgrade redis bitnami/redis \
    --version 20.13.3\
    -f redis/manifest/helm/values.yaml \
    --namespace redis

helm uninstall redis --namespace redis
kubectl delete namespace redis