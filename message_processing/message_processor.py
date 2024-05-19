import json
import logging

from data.message_data import FullMessageData, ProcessedMessageData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DefaultMessageProcessor:
    def __init__(self, extraction_service, message_producer):
        self.extraction_service = extraction_service
        self.message_producer = message_producer

    def process_message(self, raw_message_data):
        try:
            message_text = raw_message_data.message_text.strip() if raw_message_data.message_text else ""
            if not message_text:
                logger.error("Field 'message_text' is empty or missing in the raw data.")
                return

            extraction_results = self.extraction_service.extract_fields(message_text)

            processed_data = ProcessedMessageData(
                title=extraction_results['title'],
                categories=extraction_results['categories'],
                format=extraction_results['format'],
                asap=extraction_results['asap']
            )

            full_message_data = FullMessageData(
                raw_message_data=raw_message_data,
                processed_message_data=processed_data
            )

            logger.info(f"Extracted from RawMessageData following fields: {extraction_results}")

            self.message_producer.produce_message(full_message_data)

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from message content.")
        except Exception as e:
            logger.error(f"Error during message processing: {str(e)}")
