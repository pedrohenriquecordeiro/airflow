from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',                     # Owner of the DAG
    'start_date': days_ago(1),               # DAG start date
    'depends_on_past': False,                # DAG runs don't depend on previous runs
    'retries': 2,                            # Number of retries if a task fails
    'retry_delay': timedelta(minutes=5),     # Time to wait before retrying a failed task
}

# Define the DAG
with DAG(
    dag_id='bash_operator_example',          # Unique identifier for the DAG
    default_args=default_args,               # Apply default arguments
    schedule_interval='@daily',              # The DAG runs daily
    catchup=False                            # No backfilling for missed DAG runs
) as dag:

    # Task 1: Print the current date using BashOperator
    print_date = BashOperator(
        task_id='print_date',                # Unique ID for the task
        bash_command='date'                  # Bash command to print the current date
    )

    # Task 2: Sleep for 5 seconds using BashOperator
    sleep_task = BashOperator(
        task_id='sleep',                     # Unique ID for the task
        bash_command='sleep 5'               # Bash command to sleep for 5 seconds
    )

    # Task 3: Run a custom bash script (replace with the actual script path)
    run_custom_script = BashOperator(
        task_id='run_custom_script',         # Unique ID for the task
        bash_command='bash /path/to/your_script.sh'  # Replace with the path to your bash script
    )

    # Set task dependencies
    print_date >> sleep_task >> run_custom_script
