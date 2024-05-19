import spacy
from googletrans import Translator
from transformers import pipeline

from client.rabbitmq_client import DefaultRabbitMQClient
from config import RABBIT_RAW_QUEUE_NAME, RABBIT_DELIVERY_MODE, RABBIT_HOST, RABBIT_USERNAME, RABBIT_RETRY_DELAY, \
    RABBIT_MAX_RETRIES, RABBIT_PASSWORD, RABBIT_PORT, RABBIT_PROCESSED_QUEUE_NAME, HUGGING_FACE_MODEL_TASK, \
    HUGGING_FACE_MODEL, HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH, SPACY_MODEL, CATEGORIES_CANDIDATES, ASAP_CANDIDATES, \
    TITLE_LABEL, CATEGORIES_LABEL, FORMAT_LABEL, ASAP_LABEL
from field_extractor.asap_field_extractor import AsapFieldExtractor
from field_extractor.category_field_extractor import CategoryFieldExtractor
from field_extractor.format_field_extractor import FormatFieldExtractor
from field_extractor.title_filed_extractor import TitleFieldExtractor
from message_processing.message_consumer import DefaultMessageConsumer
from message_processing.message_processor import DefaultMessageProcessor
from message_processing.message_producer import DefaultMessageProducer
from service.field_extractor_service import DefaultFieldsExtractionService

if __name__ == "__main__":
    # Load necessary dependencies
    nlp = spacy.load(SPACY_MODEL)
    translator = Translator()
    pipeline_bart = pipeline(HUGGING_FACE_MODEL_TASK,
                             model=HUGGING_FACE_MODEL,
                             max_length=HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH)

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
    rabbit_client = DefaultRabbitMQClient(RABBIT_RAW_QUEUE_NAME, RABBIT_DELIVERY_MODE, RABBIT_HOST, RABBIT_PORT,
                                          RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_MAX_RETRIES, RABBIT_RETRY_DELAY)
    rabbit_client.setup_connection()

    # Setup message processing instances
    # TODO: consider event-driven approach (for sure will increase complexity, but reduce tight coupling)
    message_producer = DefaultMessageProducer(rabbit_client, RABBIT_PROCESSED_QUEUE_NAME)
    message_processor = DefaultMessageProcessor(extraction_service, message_producer)
    message_consumer = DefaultMessageConsumer(message_processor)

    # Register the message consumer and start consuming
    rabbit_client.register_message_consumer(message_consumer.consume_message, RABBIT_RAW_QUEUE_NAME)
    rabbit_client.start_consuming()
