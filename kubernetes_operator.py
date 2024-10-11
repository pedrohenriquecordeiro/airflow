from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s
from datetime import timedelta

schedule_interval = "0 1 * * *"

# Define your DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes = 5)
}

with DAG(
    dag_id='k8s_pod_operator_with_secrets',
    default_args=default_args,
    schedule_interval=schedule_interval,
    max_active_runs=1,
    catchup=False,
) as dag:

    # Define the start task using EmptyOperator
    start = EmptyOperator(
        task_id='start'
    )
  
    # Define the task using KubernetesPodOperator
    kubernetes_task = KubernetesPodOperator(
        task_id='run_pod',
        namespace='default',  # Namespace where the Pod will run
        name='k8s_pod',  # Name of the Pod
        image='YOUR_ECR_IMAGE_URL',  # The Docker image to use, from AWS ECR
        cmds=["bash", "-c"],  # Command to run inside the Pod
        arguments=["echo 'Hello, Airflow!'"],  # Arguments to pass to the command
        is_delete_operator_pod=True,  # Delete the Pod after it finishes executing
        in_cluster=True,  # Set to True if Airflow is running inside a Kubernetes cluster
        get_logs=True,  # Fetch and display the logs from the Pod in Airflow
        startup_timeout_seconds=300,  # Timeout for Pod startup
        resources=k8s.V1ResourceRequirements(
            limits={"cpu": "500m", "memory": "512Mi"},  # CPU and memory limits for the Pod
            requests={"cpu": "200m", "memory": "256Mi"}  # CPU and memory requests for the Pod
        ),
        secrets = [
          Secret(
            deploy_type = "env",
            deploy_target = "AWS_ACCESS_KEY_ID",
            secret = "aws_secret",
            key = "awsAccessKeyId",
          ),
          Secret(
            deploy_type = "env",
            deploy_target = "AWS_SECRET_KEY_ID",
            secret = "aws_secret",
            key = "awsSecretAcessKey",
          ),
          
        ] # Inject the Kubernetes secret by AWS Secrets
    )

    # Define the end task using EmptyOperator
    end = EmptyOperator(
        task_id='end'
    )

    # Set the task dependencies
    start >> kubernetes_task >> end
