from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the python path so we can import the producers
# In the Docker container, the dags are at /sources/dags (or /opt/airflow/dags)
# and the app code is at /opt/airflow/app if mounted, OR we need to adjust.
# Since we are mounting the whole repo into the container (assumed based on typical setup), 
# we need to find where 'app' is relative to this DAG file.
# 
# If this file is in <project_root>/dags/market_data_ingestion.py
# Then 'app' is in <project_root>/app
# In the container, if we mounted ./dags:/opt/airflow/dags, we might not have access to ../app 
# UNLESS we also mounted the root or app directory.
# 
# Checking docker-compose.yml:
# - ./dags:/opt/airflow/dags
# - ./logs:/opt/airflow/logs
# - ./plugins:/opt/airflow/plugins
# 
# ISSUE: The 'app' directory is NOT mounted into the Airflow container by default in the docker-compose we wrote.
# The 'PythonOperator' will fail to import 'app.kafka_services...' because the code isn't there.
# 
# SOLUTION (Temporary for this step, but needed for robustness):
# We must mount the 'app' directory into the Airflow container in docker-compose.yml.
# 
# However, since I cannot edit docker-compose and restart in the middle of this "write_file" tool call,
# I will write the DAG assuming the code IS available (or will be made available).
# 
# To make it work immediately without changing docker-compose AGAIN right now:
# I will use the BashOperator to run the scripts if they were mounted, but they aren't.
# 
# ALTERNATIVE: I will define the python functions INLINE in the DAG for now, 
# OR (Better) I will ask to update docker-compose to mount the 'app' folder.
# 
# Given the instructions, I will write the DAG to use a BashOperator that assumes the path exists,
# OR better, since we refactored the scripts to be importable, 
# I will write the DAG to import them, but I will need to add a step to mount the code.
# 
# Let's write the DAG to expect the code at /opt/airflow/app.

sys.path.append('/opt/airflow')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'market_data_ingestion',
    default_args=default_args,
    description='Fetches crypto and stock data every minute',
    schedule_interval='*/1 * * * *', # Every minute
    catchup=False,
)

def run_crypto_producer():
    # We need to import here to avoid top-level import errors if paths are wrong during parsing
    from app.kafka_services.producers.crypto_producer import run_producer, fetch_crypto_data
    # We can't easily pass command line args to the imported function unless we modify sys.argv
    # or the function itself.
    # Our refactored 'run_producer' uses argparse. 
    # A cleaner way is to just call the logic directly:
    
    import sys
    # Mock sys.argv so the producer sees the flag
    sys.argv = ["program", "--run-once"]
    run_producer()

def run_stock_producer():
    from app.kafka_services.producers.stock_producer import run_producer
    import sys
    sys.argv = ["program", "--run-once"]
    run_producer()

def run_binance_producer():
    from app.kafka_services.producers.binance_producer import run_producer
    import sys
    sys.argv = ["program", "--run-once"]
    run_producer()

with dag:
    fetch_crypto_task = PythonOperator(
        task_id='fetch_crypto_data',
        python_callable=run_crypto_producer,
    )

    fetch_stock_task = PythonOperator(
        task_id='fetch_stock_data',
        python_callable=run_stock_producer,
    )

    fetch_binance_task = PythonOperator(
        task_id='fetch_binance_data',
        python_callable=run_binance_producer,
    )

    # Run in parallel
    [fetch_crypto_task, fetch_stock_task, fetch_binance_task]
