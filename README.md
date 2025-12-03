# Crypto & Stock Analysis - Data Engineering & Aggregation Platform

This repository contains the backend infrastructure, data ingestion pipelines, and analysis services for the Crypto & Stock Analysis project. It leverages **FastAPI** for the application layer, **Apache Kafka** for decoupled data streaming, and **Apache Airflow** for workflow orchestration.

## System Architecture

*   **FastAPI Backend:** Serves market data and triggers sentiment analysis via REST endpoints.
*   **Apache Kafka:** Buffers real-time market data from producers (CoinGecko, Binance, yfinance) to consumers.
*   **Apache Airflow:** Orchestrates periodic data fetching and sentiment analysis jobs.
*   **MongoDB:** Stores raw market data and analysis results.
*   **PostgreSQL:** Metadata database for Airflow.

## Getting Started

### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose) installed and running.
*   **Git** to clone the repository.

<!-- ### 1. Environment Setup

Create a `.env` file in the root directory. You can use the following template:

```bash
# MongoDB Connection (Required)
# Replace with your actual MongoDB Atlas URI or local instance
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/RawData?retryWrites=true&w=majority
MONGODB_DATABASE=RawData

# Airflow User ID (Required for Linux/macOS)
AIRFLOW_UID=501
```

**Note:** To find your correct `AIRFLOW_UID`, run:
```bash
id -u
``` -->

### 1. Start the Infrastructure

Build and start all services (Kafka, Airflow, Backend, Postgres) using Docker Compose:

```bash
docker-compose up -d --build
```

This may take a few minutes the first time as it downloads images and builds the custom Airflow/Backend containers.

### 2. Accessing the Services

Once the containers are running, you can access the following interfaces:

<!-- *   **Airflow UI:** [http://localhost:8080](http://localhost:8080) -->
*   **Airflow UI:** [http://178.156.209.160:8080](http://178.156.209.160:8080)
    *   **Username:** `airflow`
    *   **Password:** `airflow`
<!-- *   **FastAPI Backend:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) -->
*   **FastAPI Backend:** [http://http://178.156.209.160:8080/docs](hhttp://178.156.209.160:8080/docs) (Swagger UI)
*   **Kafka Broker:** `localhost:29092` (External access)

## Running the Pipeline

The data pipelines are managed automatically by Airflow.

1.  **Login to Airflow** at [http://localhost:8080](http://localhost:8080).
2.  You will see two main DAGs:
    *   `market_data_ingestion`: Runs **every minute**. Fetches real-time data from CoinGecko, Binance, and Yahoo Finance via Kafka.
    *   `sentiment_analysis_pipeline`: Runs **every 6 hours**. Triggers the backend to perform sentiment analysis on the collected data.
3.  **Activate the DAGs:**
    *   Click the toggle switch (ON/OFF) to the left of the DAG name to **Unpause** them.
    *   The `market_data_ingestion` DAG will start running immediately.
4.  **Monitor Progress:**
    *   Click on a DAG name to see its Grid/Graph view.
    *   Green squares indicate successful runs.
    *   Red squares indicate failures (check logs by clicking the square -> Log).

## Development & Troubleshooting

*   **Check Container Logs:**
    ```bash
    docker-compose logs -f backend       # Check FastAPI logs
    docker-compose logs -f airflow-scheduler # Check Airflow scheduler
    ```
*   **Stop Services:**
    ```bash
    docker-compose down
    ```
*   **Rebuild after Code Changes:**
    If you modify the `app/` code or `requirements.txt`:
    ```bash
    docker-compose up -d --build
    ```