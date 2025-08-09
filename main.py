import logging
import spacy
from googletrans import Translator
from transformers import pipeline

from client.rabbitmq_client import DefaultRabbitMQClient
from config import load_config
from field_extractor.asap_field_extractor import AsapFieldExtractor
from field_extractor.category_field_extractor import CategoryFieldExtractor
from field_extractor.format_field_extractor import FormatFieldExtractor
from field_extractor.title_filed_extractor import TitleFieldExtractor
from message_processing.message_consumer import DefaultMessageConsumer
from message_processing.message_processor import DefaultMessageProcessor
from message_processing.message_producer import DefaultMessageProducer
from service.field_extractor_service import DefaultFieldsExtractionService

# Configure logging
def setup_logging(log_level="INFO"):
    """Setup centralized logging configuration"""
    # Convert string log level to logging constant
    log_level_constant = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level_constant,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger for the main application
    logger = logging.getLogger(__name__)
    logger.info(f"Logging level set to: {log_level}")
    return logger

def main():
    # Setup logging initially
    logger = setup_logging("INFO")
    
    logger.info("Starting UOPP Data Processor...")
    
    # Load configuration
    logger.info("Loading configuration...")
    load_config()
    
    # Import config variables after loading
    from config import (
        RABBIT_RAW_QUEUE_NAME, RABBIT_DELIVERY_MODE, RABBIT_HOST,
        RABBIT_USERNAME, RABBIT_RETRY_DELAY, RABBIT_MAX_RETRIES,
        RABBIT_PASSWORD, RABBIT_PORT, RABBIT_PROCESSED_QUEUE_NAME,
        HUGGING_FACE_MODEL_TASK, HUGGING_FACE_MODEL, HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH,
        SPACY_MODEL, CATEGORIES_CANDIDATES, ASAP_CANDIDATES,
        TITLE_LABEL, CATEGORIES_LABEL, FORMAT_LABEL, ASAP_LABEL, LOG_LEVEL
    )
    
    # Reconfigure logging with the actual log level from config
    logger = setup_logging(LOG_LEVEL)
    
    # Load necessary dependencies
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

    # Create instances of field extractors
    extractors = [
        TitleFieldExtractor(TITLE_LABEL, translator, pipeline_bart),
        CategoryFieldExtractor(CATEGORIES_LABEL, nlp, CATEGORIES_CANDIDATES),
        FormatFieldExtractor(FORMAT_LABEL),
        AsapFieldExtractor(ASAP_LABEL, nlp, ASAP_CANDIDATES)
    ]

    # Initialize extraction service with the extractors
    extraction_service = DefaultFieldsExtractionService(extractors)

    # Configure and start the RabbitMQ client
    logger.info("Initializing RabbitMQ client...")
    rabbit_client = DefaultRabbitMQClient(RABBIT_RAW_QUEUE_NAME, RABBIT_DELIVERY_MODE, RABBIT_HOST, RABBIT_PORT,
                                          RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_MAX_RETRIES, RABBIT_RETRY_DELAY)
    
    # Setup connection with retry logic
    if not rabbit_client.setup_connection():
        logger.error("Failed to establish initial connection to RabbitMQ. Exiting...")
        return

    # Setup message processing instances
    message_producer = DefaultMessageProducer(rabbit_client, RABBIT_PROCESSED_QUEUE_NAME)
    message_processor = DefaultMessageProcessor(extraction_service, message_producer)
    message_consumer = DefaultMessageConsumer(message_processor)

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
        logger.error(f"Unexpected error: {e}")
        # Don't exit on unexpected errors - let the client handle reconnection
    finally:
        # Only cleanup when explicitly stopping
        rabbit_client.stop_consuming()
        rabbit_client.close_connection()
        logger.info("Application stopped.")

if __name__ == "__main__":
    main()
