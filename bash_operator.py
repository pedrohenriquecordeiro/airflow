from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',                      # Owner of the DAG
    'start_date': days_ago(1),               # DAG start date
    'depends_on_past': False,                # DAG runs don't depend on previous runs
    'retries': 1,                            # Number of retries if a task fails
    'retry_delay': timedelta(minutes=5)      # Time to wait before retrying a failed task
}

# Define the DAG
with DAG(
    dag_id='run_local_python_file',          # Unique identifier for the DAG
    default_args=default_args,               # Apply the default arguments to the DAG
    schedule_interval=None,                  # The DAG is triggered manually
    catchup=False                            # Don't run backfills
) as dag:

    # Task to run the Python file locally using BashOperator
    run_python_file = BashOperator(
        task_id='run_python_script',         # Unique ID for the task
        bash_command='python /path/to/your_script.py'  # Replace with the actual path to your Python file
    )

    run_python_file
