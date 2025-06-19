import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
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

# Function to be executed by PythonOperator
def greet(name, age):
    print(f"Hello, {name}! You are {age} years old.")
    return f"Greeted {name}"

# Function to make an API call
def make_api_call(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        print(f"API Response: {response.json()}")
        return response.json()
    else:
        raise Exception(f"Failed API call with status code {response.status_code}")

# Define the DAG
with DAG(
    dag_id='python_operator_api_call_example',        # Unique identifier for the DAG
    default_args=default_args,                        # Apply default arguments
    schedule_interval='@daily',                       # The DAG runs daily
    catchup=False                                     # No backfilling for missed DAG runs
) as dag:

    # Task 1: Greet a user using PythonOperator
    greet_task = PythonOperator(
        task_id='greet_user',                         # Unique ID for the task
        python_callable=greet,                        # Python function to call
        op_kwargs={'name': 'John', 'age': 30}         # Pass arguments to the Python function
    )

    # Task 2: Make an API call using PythonOperator
    api_call_task = PythonOperator(
        task_id='make_api_call',                      # Unique ID for the task
        python_callable=make_api_call,                # Python function to call
        op_kwargs={'api_url': 'https://jsonplaceholder.typicode.com/todos/1'}  # Pass the API URL as an argument
    )

    # Set task dependencies
    greet_task >> api_call_task
