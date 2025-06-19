
# airflow dag that runs in a airflow build in a cluster kubernetes

# Import the required Airflow modules for DAGs and operators
from airflow import DAG                                                    # DAG is used to define the structure and logic of a workflow
from airflow.operators.empty import EmptyOperator                          # EmptyOperator is used to create no-op tasks
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # KubernetesPodOperator runs tasks inside a Kubernetes pod
from airflow.utils.dates import days_ago                                   # Utility for defining dynamic start dates
from kubernetes.client import models as k8s                                # Kubernetes client models to define resources such as CPU and memory limits for pods
from datetime import timedelta                                             # Used to define time durations like retry delays
from airflow.kubernetes.secret import Secret                               # Used to inject Kubernetes secrets into a pod

# Schedule interval for the DAG (in cron format: "0 1 * * *" runs at 1 AM every day)
schedule_interval = "0 1 * * *"

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',                                                     # Owner of the DAG
    'start_date': days_ago(1),                                              # DAG start date; runs from 1 day ago
    'depends_on_past': False,                                               # DAG runs don't depend on previous runs
    'retries': 1,                                                           # Number of retries if a task fails
    'retry_delay': timedelta(minutes=5)                                     # Time to wait before retrying a failed task
}

# Define the DAG (Directed Acyclic Graph)
with DAG(
    dag_id='k8s_pod_operator_with_secrets',                                 # Unique identifier for the DAG
    default_args=default_args,                                              # Apply the default arguments to the DAG
    schedule_interval=schedule_interval,                                    # Define when the DAG should run (cron expression)
    max_active_runs=1,                                                      # Limit to one active run of this DAG at a time
    catchup=False,                                                          # Do not backfill the DAG runs if start_date is in the past
) as dag:

    # Define the start task using EmptyOperator (acts as a starting point in the workflow)
    start = EmptyOperator(
        task_id='start' # Unique ID for the task
    )

    # Define the task using KubernetesPodOperator to run a pod on Kubernetes
    kubernetes_task = KubernetesPodOperator(
        task_id='run_pod',                                                  # Unique ID for the task
        namespace='default',                                                # Namespace where the Pod will be created
        name='k8s_pod',                                                     # Name of the Pod inside Kubernetes
        image_pull_policy="Always",                                         # Always pull the image before starting the pod
        node_selector={"app": "airflow"},                                   # Select the node that matches this label to run the pod
        do_xcom_push=True,                                                  # Enable pushing data (XCom) between tasks
        image='YOUR_ECR_IMAGE_URL',                                         # The container image to use (from AWS ECR in this case)
        cmds=["bash", "-c"],                                                # Command to run inside the pod (in this case, bash)
        arguments=["echo 'Hello, Airflow!'"],                               # Arguments for the command (echoes a message)
        is_delete_operator_pod=True,                                        # Delete the pod after the task is finished
        in_cluster=True,                                                    # Indicates that Airflow is running inside the Kubernetes cluster
        get_logs=True,                                                      # Capture and display pod logs in the Airflow UI
        startup_timeout_seconds=600,                                        # Maximum time to wait for pod startup
        env_vars={},                                                        # Placeholder for any environment variables that need to be passed into the pod
        resources=k8s.V1ResourceRequirements(                               # Define resource requirements for the pod
            limits={"cpu": "500m", "memory": "512Mi"},                      # Limit for CPU and memory usage
            requests={"cpu": "200m", "memory": "256Mi"}                     # Minimum required CPU and memory
        ),
        secrets=[
            Secret(                                                          # Inject AWS credentials from Kubernetes secrets
                deploy_type="env",                                           # Pass the secret as an environment variable
                deploy_target="AWS_ACCESS_KEY_ID",                           # Environment variable name inside the container
                secret="aws_secret",                                         # Name of the Kubernetes Secret
                key="awsAccessKeyId",                                        # Key in the Kubernetes Secret to retrieve
            ),
            Secret(
                deploy_type="env",                                           # Pass the secret as an environment variable
                deploy_target="AWS_SECRET_KEY_ID",                           # Environment variable name inside the container
                secret="aws_secret",                                         # Name of the Kubernetes Secret
                key="awsSecretAcessKey",                                     # Key in the Kubernetes Secret to retrieve
            ),
        ]  # Inject the Kubernetes secret for AWS credentials into the pod
    )

    # Define the end task using EmptyOperator (acts as the endpoint of the workflow)
    end = EmptyOperator(
        task_id='end' # Unique ID for the task
    )

    # Set the task dependencies (start -> kubernetes_task -> end)
    start >> kubernetes_task >> end
