import json
import logging

logger = logging.getLogger(__name__)


class DefaultMessageProducer:
    def __init__(self, rabbit_client, queue_name):
        self.rabbit_client = rabbit_client
        self.queue_name = queue_name

    def produce_message(self, full_message):
        try:
            full_message_json = json.dumps(full_message.as_dict())
            self.rabbit_client.produce_message(full_message_json, self.queue_name)
            logger.info(f"Produced message to queue '{self.queue_name}': {full_message_json}")
        except Exception as e:
            logger.error(f"Failed to send message to queue '{self.queue_name}': {str(e)}")
