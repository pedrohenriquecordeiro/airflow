from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import timedelta
from airflow.hooks.base import BaseHook

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',                      # Owner of the DAG
    'start_date': days_ago(1),                # DAG start date
    'depends_on_past': False,                 # DAG runs don't depend on previous runs
    'retries': 2,                             # Number of retries if a task fails
    'retry_delay': timedelta(minutes=5),      # Time to wait before retrying a failed task
}

# Define the DAG
with DAG(
    dag_id='docker_operator_ecr_artifact_example',  # Unique identifier for the DAG
    default_args=default_args,                      # Apply default arguments
    schedule_interval='@daily',                     # The DAG runs daily
    catchup=False                                   # No backfilling for missed DAG runs
) as dag:

    # Task: Run a Docker container from AWS ECR or Google Artifact Registry
    run_docker_task = DockerOperator(
        task_id='run_docker_container',               # Unique ID for the task
        image='your_ecr_or_artifact_registry_image',  # Docker image in AWS ECR or Artifact Registry
        api_version='auto',                           # API version to use
        auto_remove=True,                             # Remove the container after it finishes
        network_mode="bridge",                        # Docker network mode (default bridge)
        repository_credentials={"username": "your_username", "password": "your_password"}  # Credentials for pulling the image
    )

    run_docker_task
