from datetime import timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

# Constants for container images
IMAGE_BRONZE = "us-central1-docker.pkg.dev/dw-dev/data-pipeline-v3/bronze/data-pipeline:v0.0.9"
IMAGE_SILVER = "us-central1-docker.pkg.dev/dw-dev/data-pipeline-v3/silver/data-pipeline:v0.0.9"

# Databases to process
DATABASES = [
  'traveler' , 'backoffice'  ,  'purchase' , 
  'booking'  , 'quote'       ,  'cashflow' , 
  'ticket'   , 'customfield' ,  'chat'     , 
  'credit'   , 'payment'     ,  'pricing'
]

# Node Poll Type
NODE_POLL_TYPE = 'node-spot-c2-standard-60'

# Affinity configuration for bronze task nodes
affinity_bronze = k8s.V1Affinity(
    node_affinity=k8s.V1NodeAffinity(
        required_during_scheduling_ignored_during_execution=k8s.V1NodeSelector(
            node_selector_terms=[
                k8s.V1NodeSelectorTerm(
                    match_expressions=[
                        k8s.V1NodeSelectorRequirement(
                            key      = "node-pool-name",
                            operator = "In",
                            values   = [ NODE_POLL_TYPE ]
                        )
                    ]
                )
            ]
        )
    )
)

# Base SparkApplication manifest (as a template string)
SPARK_APPLICATION_TEMPLATE = f'''
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: <<database>>-silver-spark-job
  namespace: spark
spec:
  type: Python
  pythonVersion: "3"
  sparkVersion: "3.5.3"
  mode: cluster
  image: {IMAGE_SILVER}
  imagePullPolicy: IfNotPresent
  imagePullSecrets:
    - data-stack-secret
  mainApplicationFile: local:///app/main.py
  restartPolicy:
    type: Never
  driver:
    serviceAccount: default
    coreRequest: 1000m
    coreLimit: 2000m
    memory: 4000m
    labels:
      app: spark-driver
    env:
      - name: SOURCE_FOLDER
        value: version_3_databases/bronze/<<database>>
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
            - matchExpressions:
                - key: node-pool-name
                  operator: In
                  values:
                    - {NODE_POLL_TYPE}
  executor:
    serviceAccount: default
    instances: 3
    coreRequest: 1000m
    coreLimit: 2000m
    memory: 4000m
    labels:
      app: spark-executor
    env:
      - name: SOURCE_FOLDER
        value: version_3_databases/bronze/<<database>>
    affinity:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
            - matchExpressions:
                - key: node-pool-name
                  operator: In
                  values:
                    - {NODE_POLL_TYPE}
'''

# Default arguments for the DAG
DEFAULT_ARGS = {
    "owner"            : "Pedro Jesus",
    "start_date"       : days_ago(1),
    "email"            : ["pedro.jesus@.com.br"],
    "email_on_failure" : True,
    "email_on_retry"   : False,
    "max_active_runs"  : 1,
    "retries"          : 0
}

# DAG definition
with DAG(
    dag_id            = "data-pipeline-databases",
    default_args      = DEFAULT_ARGS,
    schedule_interval = "0 6,11,16 * * 1-5",
    catchup           = False,
    tags              = ["spark", "v3", ""],
    description       = "Extracts v3 database data from S3 and loads into Delta Lake"
) as dag:

    start = DummyOperator(task_id="start")

    # Task groups for each database
    for database in DATABASES:
        with TaskGroup(group_id=f"{database}") as db_group:

            # Bronze task: extract raw data from source
            bronze_task = KubernetesPodOperator(
                task_id                 = f"bronze_task",
                namespace               = "airflow",
                image                   = IMAGE_BRONZE,
                image_pull_secrets      = [k8s.V1LocalObjectReference("data-stack-secret")],
                get_logs                = True,
                in_cluster              = True,
                startup_timeout_seconds = 300,
                service_account_name    = "airflow-service-account",
                container_resources     = k8s.V1ResourceRequirements(
                    requests = {"memory": "1000M", "cpu": "1"},
                    limits   = {"memory": "2000M", "cpu": "2"},
                ),
                env_vars                = {"SOURCE_FOLDER": database},
                affinity                = affinity_bronze
            )

            # Silver task: transform and load data using Spark
            silver_task = SparkKubernetesOperator(
                task_id                   = f"silver_task",
                namespace                 = "spark",
                get_logs                  = True,
                startup_timeout_seconds   = 300,
                application_file          = SPARK_APPLICATION_TEMPLATE.replace("<<database>>", database),
                kubernetes_conn_id        = "in_cluster_configuration_kubernetes_cluster",
                delete_on_termination     = True,
                success_run_history_limit = 0
            )

            bronze_task >> silver_task  # Define task dependency

        # Start triggers each database group
        start >> db_group
