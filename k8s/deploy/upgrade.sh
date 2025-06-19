kubectl apply -f postgres/postgres.yaml

helm upgrade --install ingress-controller ingress-nginx/ingress-nginx \
    --version 4.12.1 \
    -f ingress/nginx-controller/manifest/helm/values-nginx-2-0-1.yaml \
    --namespace nginx


helm upgrade --install cert-manager cert-manager/cert-manager \
    --version 1.17.1 \
    -f ingress/cert-manager/manifest/helm/values-cert-manager-1-17-1.yaml \
    --namespace cert-manager


helm upgrade --install spark-operator spark-operator/spark-operator \
  --wait \
  -f spark-operator/manifest/helm/values-spark-operator.yaml \
  --namespace spark


export $(grep -v '^#' airflow/.env | xargs)
helm upgrade --install airflow apache-airflow/airflow \
  --version 1.16.0 \
  -f airflow/manifest/helm/values-airflow-1-16-0.yaml \
  --namespace airflow \
  --set config.smtp.smtp_password="$SMTP_MAILGUN_PASSWORD"