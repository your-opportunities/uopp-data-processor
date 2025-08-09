import os
import logging
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

def get_required_env_var(name: str) -> str:
    """Get required environment variable or exit with helpful message."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: Required environment variable '{name}' is not set.")
        print(f"Please set {name} in Railway dashboard under Variables tab")
        print(f"To set in Railway:")
        print(f"1. Go to Railway dashboard")
        print(f"2. Select your project")
        print(f"3. Go to Variables tab")
        print(f"4. Add {name} with your value")
        sys.exit(1)
    return value

def get_required_int_env_var(name: str) -> int:
    """Get required integer environment variable or exit with helpful message."""
    value = get_required_env_var(name)
    try:
        return int(value)
    except ValueError:
        print(f"Error: Environment variable '{name}' must be an integer, got '{value}'")
        sys.exit(1)

def get_optional_env_var(name: str, default: str = None) -> str:
    """Get optional environment variable with default."""
    return os.environ.get(name, default)

def get_optional_int_env_var(name: str, default: int) -> int:
    """Get optional integer environment variable with default."""
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        print(f"Warning: Environment variable '{name}' must be an integer, using default {default}")
        return default

def parse_rabbitmq_url(url: str) -> dict:
    """Parse RabbitMQ URL (AMQP or AMQPS) and return connection parameters."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['amqps', 'amqp']:
            raise ValueError(f"Unsupported scheme: {parsed.scheme}. Use 'amqp://' or 'amqps://'")
        
        # Extract credentials from netloc
        if '@' in parsed.netloc:
            credentials, host_port = parsed.netloc.split('@', 1)
            username, password = credentials.split(':', 1)
        else:
            username = password = None
            host_port = parsed.netloc
        
        # Extract host and port
        if ':' in host_port:
            host, port_str = host_port.split(':', 1)
            port = int(port_str)
        else:
            host = host_port
            port = 5671 if parsed.scheme == 'amqps' else 5672
        
        # Extract virtual host from path
        virtual_host = parsed.path.lstrip('/') if parsed.path else '/'
        
        return {
            'username': username,
            'password': password,
            'host': host,
            'port': port,
            'virtual_host': virtual_host,
            'use_ssl': parsed.scheme == 'amqps'
        }
    except Exception as e:
        print(f"Error parsing RabbitMQ URL '{url}': {e}")
        sys.exit(1)

# Global config variables
RABBIT_URL = None
RABBIT_RAW_QUEUE_NAME = None
RABBIT_PROCESSED_QUEUE_NAME = None
RABBIT_DELIVERY_MODE = None
RABBIT_HOST = None
RABBIT_PORT = None
RABBIT_USERNAME = None
RABBIT_PASSWORD = None
RABBIT_VIRTUAL_HOST = None
RABBIT_USE_SSL = None
RABBIT_MAX_RETRIES = None
RABBIT_RETRY_DELAY = None
LOG_LEVEL = None

# Model and extractor configurations
SPACY_MODEL = "uk_core_news_sm"
HUGGING_FACE_MODEL = "beogradjanka/bart_multitask_finetuned_for_title_and_keyphrase_generation"
HUGGING_FACE_MODEL_TASK = "text2text-generation"
HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH = 20

TITLE_LABEL = "title"
CATEGORIES_LABEL = "categories"
FORMAT_LABEL = "format"
ASAP_LABEL = "asap"

CATEGORIES_CANDIDATES = ["вебінар", "волонтерство", "грант", "конкурс", "конференція", "курс", "лекція",
                     "майстер-клас", "хакатон", "обмін", "вакансія", "проєкт", "стажування",
                     "стипендія", "табір", "турнір", "тренінг"]
ASAP_CANDIDATES = ["asap", "терміново"]

def load_config():
    """Load configuration from environment variables."""
    global RABBIT_URL, RABBIT_RAW_QUEUE_NAME, RABBIT_PROCESSED_QUEUE_NAME
    global RABBIT_DELIVERY_MODE, RABBIT_HOST, RABBIT_PORT, RABBIT_USERNAME, RABBIT_PASSWORD
    global RABBIT_VIRTUAL_HOST, RABBIT_USE_SSL, RABBIT_MAX_RETRIES, RABBIT_RETRY_DELAY, LOG_LEVEL
    
    print("Loading configuration from environment variables...")
    print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
    
    # Check if we're in Railway
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("Running in Railway environment")
        
        # Debug: Show all environment variables that might be our custom ones
        custom_vars = [key for key in os.environ.keys() if any(prefix in key.upper() for prefix in ['RABBIT'])]
        if custom_vars:
            print(f"Found custom variables: {custom_vars}")
        else:
            print("No custom variables found!")
    
    # Required RabbitMQ configs
    print("Loading required RabbitMQ configs...")
    RABBIT_URL = get_required_env_var("RABBIT_URL")
    RABBIT_PROCESSED_QUEUE_NAME = get_required_env_var("RABBIT_PROCESSED_QUEUE_NAME")

    # Optional RabbitMQ configs with defaults
    print("Loading optional RabbitMQ configs with defaults...")
    RABBIT_RAW_QUEUE_NAME = get_optional_env_var("RABBIT_RAW_QUEUE_NAME", "telegram_messages")
    RABBIT_DELIVERY_MODE = get_optional_int_env_var("RABBIT_DELIVERY_MODE", 2)
    RABBIT_MAX_RETRIES = get_optional_int_env_var("RABBIT_MAX_RETRIES", 5)
    RABBIT_RETRY_DELAY = get_optional_int_env_var("RABBIT_RETRY_DELAY", 5)

    # Parse RabbitMQ URL (AMQP or AMQPS)
    print("Parsing RabbitMQ URL...")
    rabbit_config = parse_rabbitmq_url(RABBIT_URL)
    RABBIT_HOST = rabbit_config['host']
    RABBIT_PORT = rabbit_config['port']
    RABBIT_USERNAME = rabbit_config['username']
    RABBIT_PASSWORD = rabbit_config['password']
    RABBIT_VIRTUAL_HOST = rabbit_config.get('virtual_host', '/')
    RABBIT_USE_SSL = rabbit_config['use_ssl']

    # Logging configs
    LOG_LEVEL = get_optional_env_var("LOG_LEVEL", "INFO").upper()
    
    print("Configuration loaded successfully!")
    print(f"Using defaults for optional variables:")
    print(f"  RABBIT_RAW_QUEUE_NAME: {RABBIT_RAW_QUEUE_NAME}")
    print(f"  RABBIT_DELIVERY_MODE: {RABBIT_DELIVERY_MODE}")
    print(f"  RABBIT_MAX_RETRIES: {RABBIT_MAX_RETRIES}")
    print(f"  RABBIT_RETRY_DELAY: {RABBIT_RETRY_DELAY}")
