from setuptools import setup, find_packages

setup(
    name='market-data-pipeline',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'apache-airflow',
        'confluent-kafka',
        'yfinance',
    ],
    entry_points={
        'console_scripts': [
            'stock_producer = app.kafka_services.producers.stock_producer:run_producer',
            'crypto_producer = app.kafka_services.producers.crypto_producer:run_producer',
            'binance_producer = app.kafka_services.producers.binance_producer:run_producer',
        ],
    },
)
