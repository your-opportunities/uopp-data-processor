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
   RABBIT_URL=amqps://username:password@host:5671/vhost
   RABBIT_RAW_QUEUE_NAME=telegram_messages
   RABBIT_PROCESSED_QUEUE_NAME=processed_messages
   RABBIT_DELIVERY_MODE=2
   RABBIT_MAX_RETRIES=5
   RABBIT_RETRY_DELAY=5
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

## Railway Deployment

For production deployment with Railway (free tier, continuous running), see the [Railway Deployment Guide](RAILWAY_SETUP.md).

### Quick Deploy to Railway

1. **Fork/clone this repository** to your GitHub account
2. **Sign up for Railway** at https://railway.app
3. **Connect your GitHub repo** to Railway
4. **Set environment variables** in Railway dashboard
5. **Deploy automatically** - Railway will deploy on every push to master/main

### What Railway Provides

- **Free Tier**: 500 hours/month (enough for continuous running)
- **Automatic Deployments**: Deploys on every Git push
- **Environment Variables**: Secure management of secrets
- **Real-time Logs**: Monitor your application
- **SSL/HTTPS**: Automatic SSL certificates
- **Custom Domains**: Optional custom domain support

### Environment Variables for Railway

Set these in Railway dashboard:

```env
# Required Variables
RABBIT_URL=amqps://username:password@host:5671/vhost
RABBIT_PROCESSED_QUEUE_NAME=processed_messages

# Optional Variables (with defaults)
RABBIT_RAW_QUEUE_NAME=telegram_messages
RABBIT_DELIVERY_MODE=2
RABBIT_MAX_RETRIES=5
RABBIT_RETRY_DELAY=5
LOG_LEVEL=INFO
```

See [RAILWAY_SETUP.md](RAILWAY_SETUP.md) for detailed setup instructions.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `RABBIT_URL` | RabbitMQ connection URL (amqp:// or amqps://) | - |
| `RABBIT_RAW_QUEUE_NAME` | RabbitMQ queue name for raw messages | `telegram_messages` |
| `RABBIT_PROCESSED_QUEUE_NAME` | RabbitMQ queue name for processed messages | - |
| `RABBIT_DELIVERY_MODE` | RabbitMQ delivery mode | `2` |
| `RABBIT_MAX_RETRIES` | Maximum retry attempts | `5` |
| `RABBIT_RETRY_DELAY` | Retry delay in seconds | `5` |
