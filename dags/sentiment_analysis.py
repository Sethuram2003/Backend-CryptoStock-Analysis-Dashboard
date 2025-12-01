from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime, timedelta
import json

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'sentiment_analysis_pipeline',
    default_args=default_args,
    description='Triggers sentiment analysis for crypto and stocks',
    schedule_interval='0 */6 * * *', # Every 6 hours
    catchup=False,
)

# Configuration
CRYPTO_ASSETS = ['bitcoin', 'ethereum', 'solana', 'cardano', 'dogecoin']
STOCK_TICKERS = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA']
CONNECTION_ID = 'fastapi_backend'

with dag:

    # Create tasks for each Crypto Asset
    for coin in CRYPTO_ASSETS:
        SimpleHttpOperator(
            task_id=f'sentiment_crypto_{coin}',
            http_conn_id=CONNECTION_ID,
            endpoint='/put-crypto-sentiment',
            method='PUT',
            data=json.dumps({"coin_id": coin, "days": 7}),
            headers={"Content-Type": "application/json"},
            response_check=lambda response: response.status_code == 200,
            dag=dag,
        )

    # Create tasks for each Stock Ticker
    for ticker in STOCK_TICKERS:
        SimpleHttpOperator(
            task_id=f'sentiment_stock_{ticker}',
            http_conn_id=CONNECTION_ID,
            endpoint='/put-stock-sentiment',
            method='PUT',
            data=json.dumps({"ticker": ticker, "days": 7}),
            headers={"Content-Type": "application/json"},
            response_check=lambda response: response.status_code == 200,
            dag=dag,
        )
