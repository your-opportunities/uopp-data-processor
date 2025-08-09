# UOPP: DATA PROCESSOR

## About

**Description**

to be added...

**Technologies**

Python, Hugging Face, Spacy, Googletrans, RabbitMQ, Docker

## Local setup

**Prerequisites**

- Python 3, pip
- Docker
- Launched uopp-telegram-scrapper

[//]: # (TODO: review part with docker setup, each service should be launched independetly)

**Installation**

1. Clone and open project
2. Create .env file as an example below (specify you configs)

   ```dotenv
   RABBIT_RAW_QUEUE_NAME=<RABBIT_RAW_QUEUE_NAME>
   RABBIT_PROCESSED_QUEUE_NAME=<RABBIT_PROCESSED_QUEUE_NAME>
   RABBIT_DELIVERY_MODE=<RABBIT_DELIVERY_MODE>
   RABBIT_HOST=<RABBIT_HOST>
   RABBIT_PORT=<RABBIT_PORT>
   RABBIT_UI_PORT=<RABBIT_UI_PORT>
   RABBIT_USERNAME=<RABBIT_USERNAME>
   RABBIT_PASSWORD=<RABBIT_PASSWORD>
   RABBIT_MAX_RETRIES=<RABBIT_MAX_RETRIES>
   RABBIT_RETRY_DELAY=<RABBIT_RETRY_DELAY>
   LOG_LEVEL=INFO
   ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Launch the program
    ```bash
    python main.py
    ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `RABBIT_RAW_QUEUE_NAME` | RabbitMQ queue name for raw messages | - |
| `RABBIT_PROCESSED_QUEUE_NAME` | RabbitMQ queue name for processed messages | - |
| `RABBIT_DELIVERY_MODE` | RabbitMQ delivery mode | - |
| `RABBIT_HOST` | RabbitMQ host | - |
| `RABBIT_PORT` | RabbitMQ port | - |
| `RABBIT_USERNAME` | RabbitMQ username | - |
| `RABBIT_PASSWORD` | RabbitMQ password | - |
| `RABBIT_MAX_RETRIES` | Maximum retry attempts | - |
| `RABBIT_RETRY_DELAY` | Retry delay in seconds | - |
