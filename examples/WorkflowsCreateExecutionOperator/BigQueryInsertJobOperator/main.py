from airflow import DAG
import pendulum
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime
from airflow.utils.task_group import TaskGroup

# === PARAMS ===
DAG_ID       = "v3_silver_quotes"
PROJECT_ID   = "dw-dev"
GCP_CONN_ID  = "google-cloud-connection-sa-data-stack-v3-gserviceaccount"
LOCATION     = "us-central1"
OWNER        = "Pedro Jesus"
OWNER_EMAIL  = ["pedro.jesus@pedro.com.br"]

# === DEFAULT ARGS ===
DEFAULT_ARGS = {
    "owner"           : OWNER,
    "start_date"      : pendulum.now("America/Sao_Paulo"),
    "email"           : OWNER_EMAIL,
    "email_on_failure": False,
    "email_on_retry"  : False,
    "retries"         : 0,
}

with DAG(
    dag_id            = DAG_ID,
    description       = "",
    default_args      = DEFAULT_ARGS,
    schedule_interval = None,
    catchup           = False,
    max_active_runs   = 1,
    tags              = ["workflow" , "bigquery"],
) as dag:

    start = DummyOperator(task_id="start")

    with TaskGroup("Gold_User_Quotes_Auto") as auto_group:
        Gold_User_Quotes_Auto_Insert = BigQueryInsertJobOperator(
            task_id       = "Gold_User_Quotes_Auto_Insert",
            location      = LOCATION,
            gcp_conn_id   = GCP_CONN_ID,
            configuration = {
                "query": {
                    "query": """
                        CREATE OR REPLACE TABLE `dw-dev.v3_silver.auto_quotes`
                        PARTITION BY DATE_TRUNC(created_at, MONTH)
                        CLUSTER BY company_id
                        AS
                        SELECT 
                            q.id,
                            q.user_id,
                            q.organization_id AS company_id,
                            aq.status,
                            withdraw.name AS withdraw,
                            deposit.name AS deposit,
                            DATE(aq.withdraw_date) AS withdraw_date,
                            DATE(aq.deposit_date) AS deposit_date,
                            DATE(aq.created_at) AS created_at
                        FROM `dw-dev.v3_quote.rental_car_quotes` aq
                        INNER JOIN `dw-dev.v3_quote.quotes` q
                            ON q.id = aq.quote_id
                        LEFT JOIN `dw-dev.luna_destination.destinations` withdraw
                            ON withdraw.place_id = aq.withdraw_city_place_id
                        LEFT JOIN `dw-dev.luna_destination.destinations` deposit
                            ON deposit.place_id = aq.deposit_city_place_id
                    """,
                    "useLegacySql": False,
                    "useQueryCache": False,
                }
            }
        )

    with TaskGroup("Gold_User_Quotes_Bus") as bus_group:
        Gold_User_Quotes_Bus_Insert = BigQueryInsertJobOperator(
            task_id       ="Gold_User_Quotes_Bus_Insert",
            location      = LOCATION,
            gcp_conn_id   = GCP_CONN_ID,
            configuration = {
                "query": {
                    "query": """
                        CREATE OR REPLACE TABLE `dw-dev.v3_silver.bus_quotes`
                        PARTITION BY DATE_TRUNC(created_at, MONTH)
                        CLUSTER BY company_id
                        AS
                        SELECT 
                            q.id,
                            q.user_id,
                            q.organization_id AS company_id,
                            bq.status,
                            bq.type,
                            origin.display_name AS origin,
                            bq.from_type AS origin_type,
                            return.display_name AS return,
                            bq.to_type AS return_type,
                            DATE(bq.departure) AS origin_date,
                            DATE(bq.return) AS return_date,
                            DATE(bq.created_at) AS created_at
                        FROM `dw-dev.v3_quote.bus_quotes` bq
                        INNER JOIN `dw-dev.v3_quote.quotes` q
                            ON q.id = bq.quote_id
                        LEFT JOIN `dw-dev.luna_destination.bus_destinations` origin
                            ON origin.id = bq.from
                        LEFT JOIN `dw-dev.luna_destination.bus_destinations` return
                            ON return.id = bq.to
                    """,
                    "useLegacySql": False,
                    "useQueryCache": False,
                }
            }
        )

    start >> [auto_group , bus_group]
