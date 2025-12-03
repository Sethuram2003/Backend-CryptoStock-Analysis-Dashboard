from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the python path so we can import the producers
# The 'app' folder is mounted at /opt/airflow/app
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
    # Import inside the function to ensure sys.path is set
    from app.kafka_services.producers.crypto_producer import run_producer
    import sys
    import logging
    logging.info("Starting crypto producer")
    try:
        sys.argv = ["program", "--run-once"]
        run_producer()
    except Exception as e:
        logging.error(f"Error running crypto producer: {e}", exc_info=True)

def run_stock_producer():
    from app.kafka_services.producers.stock_producer import run_producer
    import sys
    import logging
    logging.info("Starting stock producer")
    try:
        sys.argv = ["program", "--run-once"]
        run_producer()
    except Exception as e:
        logging.error(f"Error running stock producer: {e}", exc_info=True)

def run_binance_producer():
    from app.kafka_services.producers.binance_producer import run_producer
    import sys
    import logging
    logging.info("Starting binance producer")

    try:
        sys.argv = ["program", "--run-once"]
        run_producer()
    except Exception as e:
        logging.error(f"Error running binance producer: {e}", exc_info=True)

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