from airflow import DAG
from airflow.providers.google.cloud.operators.workflows import (
    WorkflowsCreateExecutionOperator,
    WorkflowsGetExecutionOperator,
)
from airflow.providers.google.cloud.sensors.workflows import WorkflowExecutionSensor
from datetime import timedelta
import pendulum
from typing import cast
from airflow.models.xcom_arg import XComArg

# === PARAMS ===
DAG_ID       = "<name_dag>"
PROJECT_ID   = ""
WORKFLOW_ID  = "<name-workflow>"
GCP_CONN_ID  = "
LOCATION     = "us-central1"
OWNER        = "Pedro Jesus"
OWNER_EMAIL  = ["pedro.jesus@pedro.com.br"]

# === DEFAULT ARGS ===
DEFAULT_ARGS = {
    "owner": OWNER,
    "start_date": pendulum.now("America/Sao_Paulo"),
    "email": OWNER_EMAIL,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}

# === DAG DEFINITION ===
with DAG(
    dag_id            = DAG_ID,
    description       = "Trigger and monitor a GCP Workflow execution",
    default_args      = DEFAULT_ARGS,
    schedule_interval = None,
    catchup           = False,
    max_active_runs   = 1,
    tags              = ["workflow"],
) as dag:

    create_execution = WorkflowsCreateExecutionOperator(
        task_id     = "create_execution",
        location    = LOCATION,
        project_id  = PROJECT_ID,
        workflow_id = WORKFLOW_ID,
        gcp_conn_id = GCP_CONN_ID,
        execution   = {"argument": ""}
    )

    create_execution_id = cast("str", XComArg(create_execution, key="execution_id"))

    wait_for_execution = WorkflowExecutionSensor(
        task_id           = "wait_for_execution",
        location          = LOCATION,
        project_id        = PROJECT_ID,
        workflow_id       = WORKFLOW_ID,
        gcp_conn_id       = GCP_CONN_ID,
        execution_id      = create_execution_id,
        mode              = 'poke',
        poke_interval     = 30,       #  Time in seconds that the job should wait in between each tries
        timeout           = 3600,     #  Time, in seconds before the task times out and fails.
        soft_fail         = True      #  Set to true to mark the task as SKIPPED on failure
    )

    get_execution = WorkflowsGetExecutionOperator(
        task_id      = "get_execution",
        location     = LOCATION,
        project_id   = PROJECT_ID,
        workflow_id  = WORKFLOW_ID,
        gcp_conn_id  = GCP_CONN_ID,
        execution_id = create_execution_id
    )

    create_execution >> wait_for_execution >> get_execution
