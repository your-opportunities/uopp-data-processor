import json
import logging
from datetime import datetime

from data.message_data import RawMessageData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DefaultMessageConsumer:
    def __init__(self, message_processor):
        self.message_processor = message_processor

    def consume_message(self, message):
        try:
            loaded_message_data = json.loads(message)
            raw_message_data = RawMessageData(
                post_creation_time=datetime.fromisoformat(loaded_message_data['post_creation_time']),
                scrapped_creation_time=datetime.fromisoformat(loaded_message_data['scrapped_creation_time']),
                channel_id=loaded_message_data['channel_id'],
                channel_name=loaded_message_data['channel_name'],
                message_text=loaded_message_data['message_text'].strip()
            )
            logger.info(f"Retrieved RawMessageDate from consumed message: {raw_message_data}")

            self.message_processor.process_message(raw_message_data)

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from message content.")
        except Exception as e:
            logger.error(f"Error processing the message: {e}")
