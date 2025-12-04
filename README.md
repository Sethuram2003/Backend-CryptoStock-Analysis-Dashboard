# 📊 Crypto & Stock Analysis - Data Engineering & AI Agent Platform

A comprehensive real-time financial analysis platform that combines data engineering, sentiment analysis, and AI-powered market insights. This system leverages **FastAPI**, **Apache Kafka**, **Apache Airflow**, **LangGraph**, and **MCP (Model Context Protocol)** to deliver intelligent market analysis.

## 🌐 Live Deployments

- **FastAPI Backend (Vercel):** [https://crypto-and-stock-analysis-da-and-ag.vercel.app/docs](https://crypto-and-stock-analysis-da-and-ag.vercel.app/docs)
- **Airflow Dashboard (Hetzner):** [http://178.156.209.160:8080](http://178.156.209.160:8080)
  - Username: `airflow`
  - Password: `airflow`

## 👥 Authors

- **Sethuram** - [@Sethuram2003](https://github.com/Sethuram2003)
- **Sanjay** - [@Sanjay-RK-27](https://github.com/Sanjay-RK-27)
- **Praveen** - [@apraveen001](https://github.com/apraveen001)
- **Sriram** - [@SriramV1212](https://github.com/SriramV1212)
- **Abby** - [@AdebayoBraimah](https://github.com/AdebayoBraimah)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
│  CoinGecko API  │  Yahoo Finance  │  Binance API  │  News API   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Apache Airflow (Orchestration)                │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │ Market Data DAG      │    │ Sentiment Analysis DAG       │  │
│  │ (Every 1 minute)     │    │ (Every 6 hours)              │  │
│  └──────────────────────┘    └──────────────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Apache Kafka (Streaming)                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ crypto_market    │  │ stock_market     │  │ binance      │  │
│  │ _data topic      │  │ _data topic      │  │ _data topic  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kafka Consumers                               │
│  ┌──────────────────┐           ┌──────────────────┐           │
│  │ Crypto Consumer  │           │ Stock Consumer   │           │
│  └──────────────────┘           └──────────────────┘           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MongoDB (Storage)                           │
│  Collections: Crypto, Stock_Market, Crypto_News,                │
│               Stock_Market_News                                  │
└─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend + AI Agent                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LangGraph Sentiment Analysis Pipeline                    │  │
│  │  (Search → Scrape → Filter → Analyze → Aggregate)        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  MCP Servers (Crypto & Stock Tools)                       │  │
│  │  - Real-time data fetching                                │  │
│  │  - Sentiment analysis                                      │  │
│  │  - Web scraping capabilities                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
.
├── app/                              # Main application directory
│   ├── main.py                       # FastAPI application entry point
│   ├── api/                          # API routes
│   │   └── routes/
│   │       ├── health_check.py       # Health check endpoint
│   │       ├── chat.py               # AI chat agent endpoint
│   │       ├── crypto/               # Cryptocurrency endpoints
│   │       │   ├── get_crypto_data.py           # Real-time crypto prices
│   │       │   ├── get_crypto_historical.py     # Historical price data
│   │       │   └── get_current_sentiment.py     # Crypto sentiment analysis
│   │       └── stock/                # Stock market endpoints
│   │           ├── get_stock_data.py            # Real-time stock prices
│   │           ├── get_stock_historical.py      # Historical stock data
│   │           └── get_stock_sentiment.py       # Stock sentiment analysis
│   ├── core/                         # Core business logic
│   │   ├── Agent.py                  # AI agent with MCP integration
│   │   ├── prompt.py                 # System prompts for AI agent
│   │   ├── CryptoData.py             # Crypto data fetching logic
│   │   ├── StockData.py              # Stock data fetching logic
│   │   ├── mongodb.py                # MongoDB connection handler
│   │   ├── lang_graph/               # LangGraph sentiment pipeline
│   │   │   ├── builder.py            # Graph workflow builder
│   │   │   ├── nodes.py              # Pipeline nodes (search, scrape, analyze)
│   │   │   ├── schema.py             # Pydantic schemas for state management
│   │   │   └── workflow_diagram.png  # Visual workflow representation
│   │   ├── CryptoMcpServer/          # MCP server for crypto tools
│   │   │   └── main.py               # Crypto MCP tool definitions
│   │   └── StockMcpServer/           # MCP server for stock tools
│   │       └── main.py               # Stock MCP tool definitions
│   └── kafka_services/               # Kafka producers and consumers
│       ├── producers/
│       │   ├── crypto_producer.py    # Publishes crypto data to Kafka
│       │   ├── stock_producer.py     # Publishes stock data to Kafka
│       │   └── binance_producer.py   # Publishes Binance data to Kafka
│       └── consumers/
│           ├── crypto_consumer.py    # Consumes crypto data, writes to MongoDB
│           └── stock_consumer.py     # Consumes stock data, writes to MongoDB
├── dags/                             # Airflow DAG definitions
│   ├── market_data_ingestion.py      # Schedules data fetching (every 1 min)
│   └── sentiment_analysis.py         # Schedules sentiment analysis (every 6 hrs)
├── docker/                           # Docker configurations
│   └── airflow/
│       └── Dockerfile                # Custom Airflow image with dependencies
├── Dockerfile                        # FastAPI backend Docker image
├── docker-compose.yml                # Multi-container orchestration
├── requirements.txt                  # Python dependencies
├── vercel.json                       # Vercel deployment configuration
└── .env                              # Environment variables (API keys, DB URIs)
```

## 🔧 Core Components

### 1. **FastAPI Backend** (`app/main.py`)
- RESTful API serving market data and sentiment analysis
- CORS-enabled for cross-origin requests
- Swagger UI documentation at `/docs`
- Health check endpoint for monitoring

### 2. **Data Fetching Modules**

#### `app/core/CryptoData.py`
- Fetches real-time cryptocurrency data from CoinGecko API
- Retrieves historical price data (prices, market caps, volumes)
- Supports multiple cryptocurrencies (Bitcoin, Ethereum, Cardano, Solana, Dogecoin)

#### `app/core/StockData.py`
- Fetches real-time stock market data using yfinance
- Retrieves historical stock prices
- Supports major stocks (AAPL, MSFT, AMZN, GOOGL, TSLA)
- Handles edge cases with fallback mechanisms

### 3. **MongoDB Integration** (`app/core/mongodb.py`)
- Serverless-friendly connection pooling
- TLS/SSL support with certifi
- Collections:
  - `Crypto`: Real-time crypto market data
  - `Stock_Market`: Real-time stock market data
  - `Crypto_News`: Crypto sentiment analysis results
  - `Stock_Market_News`: Stock sentiment analysis results

### 4. **LangGraph Sentiment Analysis Pipeline** (`app/core/lang_graph/`)

A sophisticated multi-stage pipeline for news sentiment analysis:

#### **Workflow Stages:**
1. **Search** (`search_news`): Queries News API for recent articles
2. **Scrape** (`scrape_articles`): Parallel web scraping with BeautifulSoup
3. **Filter** (`filter_articles`): Filters relevant articles by keyword matching
4. **Sentiment** (`analyze_sentiment`): LLM-based sentiment scoring (-1 to 1)
5. **Aggregate** (`aggregate_results`): Compiles top 3 articles with average sentiment

#### **Key Features:**
- Parallel processing with ThreadPoolExecutor for performance
- Automatic title generation using Groq LLM when missing
- Sentiment trend detection (increasing/decreasing)
- Pydantic schemas for type safety

### 5. **AI Chat Agent** (`app/core/Agent.py`)

An intelligent financial analysis assistant powered by:
- **LangChain** for agent orchestration
- **Groq LLM** (Llama 4 Scout 17B) for reasoning
- **MCP (Model Context Protocol)** for tool integration
- **InMemorySaver** for conversation checkpointing

#### **Capabilities:**
- Real-time market data retrieval
- Sentiment analysis with article extraction
- Web scraping for news content
- Evidence-based financial reasoning

### 6. **MCP Servers** (Model Context Protocol)

#### `app/core/CryptoMcpServer/main.py`
**Tools:**
- `get_crypto_data(coin_id)`: Fetch real-time crypto prices
- `put_crypto_sentiment(coin_id, days)`: Get sentiment analysis
- `get_data_url(url)`: Scrape and extract readable text from URLs

#### `app/core/StockMcpServer/main.py`
**Tools:**
- `get_stock_data(ticker)`: Fetch real-time stock prices
- `put_stock_sentiment(ticker, days)`: Get sentiment analysis

### 7. **Apache Kafka Streaming**

#### **Producers:**
- `crypto_producer.py`: Publishes crypto data to `crypto_market_data` topic
- `stock_producer.py`: Publishes stock data to `stock_market_data` topic
- `binance_producer.py`: Publishes Binance data to `binance_data` topic

#### **Consumers:**
- `crypto_consumer.py`: Consumes crypto data and writes to MongoDB
- `stock_consumer.py`: Consumes stock data and writes to MongoDB

### 8. **Apache Airflow Orchestration**

#### `dags/market_data_ingestion.py`
- **Schedule:** Every 1 minute
- **Tasks:**
  - `fetch_crypto_data`: Runs crypto producer
  - `fetch_stock_data`: Runs stock producer
  - `fetch_binance_data`: Runs Binance producer
- **Execution:** Parallel task execution

#### `dags/sentiment_analysis.py`
- **Schedule:** Every 6 hours
- **Tasks:**
  - Triggers sentiment analysis for 5 cryptocurrencies
  - Triggers sentiment analysis for 5 stocks
- **HTTP Operator:** Calls FastAPI backend endpoints

## 🚀 Getting Started

### Prerequisites

- **Docker Desktop** (with Docker Compose)
- **Git**
- **API Keys** (see below)

### Required API Keys

Create a `.env` file in the root directory with the following:

```bash
# MongoDB Atlas (Database)
# Sign up at: https://www.mongodb.com/cloud/atlas
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/RawData?retryWrites=true&w=majority"
MONGODB_DATABASE="RawData"

# Groq API (LLM for sentiment analysis)
# Get your key at: https://console.groq.com/keys
GROQ_API_KEY="your_groq_api_key_here"

# News API (News article fetching)
# Get your key at: https://newsapi.org/register
NEWS_API="your_news_api_key_here"

# LangSmith (Optional - for LLM tracing)
# Sign up at: https://smith.langchain.com/
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY="your_langsmith_api_key_here"
LANGSMITH_PROJECT="crypto_stock"

# Airflow Configuration
AIRFLOW_UID=0
```

### API Key Sources

| Service | Purpose | Sign Up Link |
|---------|---------|--------------|
| **MongoDB Atlas** | Database storage | [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register) |
| **Groq** | LLM inference (free tier available) | [https://console.groq.com/keys](https://console.groq.com/keys) |
| **News API** | News article fetching | [https://newsapi.org/register](https://newsapi.org/register) |
| **LangSmith** | LLM observability (optional) | [https://smith.langchain.com/](https://smith.langchain.com/) |

### Installation & Running

1. **Clone the repository:**
```bash
git clone <repository-url>
cd <repository-name>
```

2. **Create `.env` file** with your API keys (see above)

3. **Start all services:**
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
<!-- *   **FastAPI Backend:** [http://178.156.209.160:8080/docs](http://178.156.209.160:8080/docs) (Swagger UI)
*   **Kafka Broker:** `localhost:29092` (External access) -->

## 📡 API Endpoints

### Health Check
- `GET /health` - Service health status

### Cryptocurrency Endpoints
- `GET /get-crypto-data?coin_id=bitcoin` - Real-time crypto data
- `GET /get-crypto-historical?coin_id=bitcoin&days=7` - Historical prices
- `PUT /put-crypto-sentiment?coin_id=bitcoin&days=7` - Sentiment analysis

### Stock Market Endpoints
- `GET /get-stock-data?ticker=AAPL` - Real-time stock data
- `GET /get-stock-historical?ticker=AAPL&days=7` - Historical prices
- `PUT /put-stock-sentiment?ticker=AAPL&days=7` - Sentiment analysis

### AI Chat Agent
- `POST /chat?query=<your_question>` - Ask the AI agent about markets

## 🔍 Monitoring & Troubleshooting

### Check Container Logs
```bash
# FastAPI Backend
docker-compose logs -f backend

# Airflow Scheduler
docker-compose logs -f airflow-scheduler

# Kafka Consumers
docker-compose logs -f consumers

# Kafka Broker
docker-compose logs -f broker
```

### Stop All Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Access Airflow DAGs
1. Navigate to [http://localhost:8080](http://localhost:8080)
2. Login with `airflow` / `airflow`
3. Toggle DAGs to activate them
4. Monitor execution in Grid/Graph view

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | FastAPI, Python 3.12 |
| **AI/ML** | LangChain, LangGraph, Groq (Llama 4), MCP |
| **Data Streaming** | Apache Kafka, Confluent Kafka |
| **Orchestration** | Apache Airflow |
| **Database** | MongoDB Atlas, PostgreSQL |
| **Data Sources** | CoinGecko API, Yahoo Finance, Binance API, News API |
| **Web Scraping** | BeautifulSoup4, httpx |
| **Deployment** | Docker, Docker Compose, Vercel, Hetzner |
| **Monitoring** | LangSmith (optional) |

## 🌟 Key Features

- ✅ Real-time cryptocurrency and stock market data ingestion
- ✅ Automated sentiment analysis using LLM-powered pipeline
- ✅ AI chat agent with financial analysis capabilities
- ✅ Scalable Kafka-based streaming architecture
- ✅ Airflow-orchestrated data pipelines
- ✅ MCP integration for extensible tool ecosystem
- ✅ Parallel processing for performance optimization
- ✅ Comprehensive API documentation with Swagger UI
- ✅ Production-ready Docker deployment
- ✅ Cloud deployment on Vercel and Hetzner

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please reach out to the authors listed above.
