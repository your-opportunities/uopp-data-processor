import logging
import subprocess
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

import spacy
from googletrans import Translator
from transformers import pipeline

from config import load_config
from service.field_extractor_service import DefaultFieldsExtractionService
from field_extractor.title_filed_extractor import TitleFieldExtractor
from field_extractor.category_field_extractor import CategoryFieldExtractor
from field_extractor.format_field_extractor import FormatFieldExtractor
from field_extractor.asap_field_extractor import AsapFieldExtractor
from message_processing.message_consumer import DefaultMessageConsumer
from message_processing.message_processor import DefaultMessageProcessor
from message_processing.message_producer import DefaultMessageProducer
from client.rabbitmq_client import DefaultRabbitMQClient


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Start a simple HTTP server for health checks"""
    try:
        with socketserver.TCPServer(("", 8080), HealthCheckHandler) as httpd:
            print("Health check server started on port 8080")
            httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start health server: {e}")

def setup_logging(log_level="INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging level set to: {log_level}")
    return logger

def download_models_if_needed():
    """Download NLP models if they don't exist."""
    logger = logging.getLogger(__name__)
    
    # Check if spaCy model exists
    try:
        nlp = spacy.load("uk_core_news_sm")
        logger.info("spaCy Ukrainian model already exists")
    except OSError:
        logger.info("Downloading spaCy Ukrainian model...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "spacy", "download", "uk_core_news_sm"
            ], check=True, capture_output=True, text=True, timeout=300)
            logger.info("spaCy Ukrainian model downloaded successfully")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to download spaCy model: {e}")
            return False
    
    # Check if transformers model exists (will download automatically if not)
    try:
        logger.info("Checking transformers model...")
        from transformers import pipeline
        # This will download the model if it doesn't exist
        test_pipeline = pipeline("text2text-generation", 
                               model="beogradjanka/bart_multitask_finetuned_for_title_and_keyphrase_generation", 
                               max_length=20)
        logger.info("Transformers model ready")
    except Exception as e:
        logger.error(f"Failed to load/download transformers model: {e}")
        return False
    
    return True

def main():
    try:
        # Start health check server in a separate thread
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        
        # Give the health server time to start
        time.sleep(2)
        
        # Setup logging initially
        logger = setup_logging("INFO")
        
        logger.info("Starting UOPP Data Processor...")
        
        # Load configuration
        logger.info("Loading configuration...")
        try:
            load_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return
        
        # Import config variables after loading
        try:
            from config import (
                RABBIT_RAW_QUEUE_NAME, RABBIT_DELIVERY_MODE, RABBIT_HOST,
                RABBIT_USERNAME, RABBIT_RETRY_DELAY, RABBIT_MAX_RETRIES,
                RABBIT_PASSWORD, RABBIT_PORT, RABBIT_PROCESSED_QUEUE_NAME,
                RABBIT_USE_SSL, RABBIT_VIRTUAL_HOST,
                HUGGING_FACE_MODEL_TASK, HUGGING_FACE_MODEL, HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH,
                SPACY_MODEL, CATEGORIES_CANDIDATES, ASAP_CANDIDATES,
                TITLE_LABEL, CATEGORIES_LABEL, FORMAT_LABEL, ASAP_LABEL, LOG_LEVEL
            )
        except Exception as e:
            logger.error(f"Failed to import configuration variables: {e}")
            return
        
        # Reconfigure logging with the actual log level from config
        logger = setup_logging(LOG_LEVEL)
        
        # Download models if needed (only once during startup)
        logger.info("Checking for required NLP models...")
        try:
            if not download_models_if_needed():
                logger.error("Failed to download required models. Exiting...")
                return
        except Exception as e:
            logger.error(f"Failed to download models: {e}")
            return
        
        # Load NLP models once during startup
        logger.info("Loading NLP models...")
        try:
            nlp = spacy.load(SPACY_MODEL)
            translator = Translator()
            pipeline_bart = pipeline(HUGGING_FACE_MODEL_TASK,
                                     model=HUGGING_FACE_MODEL,
                                     max_length=HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH)
            logger.info("NLP models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            return

        # Create instances of field extractors (using the loaded models)
        try:
            extractors = [
                TitleFieldExtractor(TITLE_LABEL, translator, pipeline_bart),
                CategoryFieldExtractor(CATEGORIES_LABEL, nlp, CATEGORIES_CANDIDATES),
                FormatFieldExtractor(FORMAT_LABEL),
                AsapFieldExtractor(ASAP_LABEL, nlp, ASAP_CANDIDATES)
            ]

            # Initialize extraction service with the extractors
            extraction_service = DefaultFieldsExtractionService(extractors)
        except Exception as e:
            logger.error(f"Failed to create field extractors: {e}")
            return

        # Configure and start the RabbitMQ client
        logger.info("Initializing RabbitMQ client...")
        try:
            rabbit_client = DefaultRabbitMQClient(RABBIT_RAW_QUEUE_NAME, RABBIT_DELIVERY_MODE, RABBIT_HOST, RABBIT_PORT,
                                                  RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_MAX_RETRIES, RABBIT_RETRY_DELAY,
                                                  RABBIT_USE_SSL, RABBIT_VIRTUAL_HOST)
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ client: {e}")
            return
        
        # Setup connection with retry logic
        logger.info("Establishing RabbitMQ connection...")
        try:
            if not rabbit_client.setup_connection():
                logger.error("Failed to establish initial connection to RabbitMQ. Exiting...")
                return
        except Exception as e:
            logger.error(f"Failed to setup RabbitMQ connection: {e}")
            return

        # Setup message processing instances
        try:
            message_producer = DefaultMessageProducer(rabbit_client, RABBIT_PROCESSED_QUEUE_NAME)
            message_processor = DefaultMessageProcessor(extraction_service, message_producer)
            message_consumer = DefaultMessageConsumer(message_processor)
        except Exception as e:
            logger.error(f"Failed to setup message processing: {e}")
            return

        logger.info("Starting continuous message consumption...")
        logger.info("Press Ctrl+C to stop the application.")
        
        try:
            # Register the message consumer and start consuming
            rabbit_client.register_message_consumer(message_consumer.consume_message, RABBIT_RAW_QUEUE_NAME)
            
            # This will run continuously until explicitly stopped
            rabbit_client.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down gracefully...")
        except Exception as e:
            logger.error(f"Unexpected error during message consumption: {e}")
            # Don't exit on unexpected errors - let the client handle reconnection
        finally:
            # Only cleanup when explicitly stopping
            try:
                rabbit_client.stop_consuming()
                rabbit_client.close_connection()
                logger.info("Application stopped.")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                
    except Exception as e:
        # Catch any unhandled exceptions to prevent crashes
        print(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
