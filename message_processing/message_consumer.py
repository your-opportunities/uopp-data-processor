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
            # Handle message decoding
            if not message:
                logger.warning("Received empty message, skipping...")
                return
                
            loaded_message_data = json.loads(message)
            raw_message_data = RawMessageData(
                post_creation_time=datetime.fromisoformat(loaded_message_data['post_creation_time']),
                scrapped_creation_time=datetime.fromisoformat(loaded_message_data['scrapped_creation_time']),
                channel_id=loaded_message_data['channel_id'],
                channel_name=loaded_message_data['channel_name'],
                message_text=loaded_message_data['message_text'].strip()
            )
            logger.info(f"Retrieved RawMessageDate from consumed message: {raw_message_data}")

            # Process message with error handling
            try:
                self.message_processor.process_message(raw_message_data)
            except Exception as e:
                logger.error(f"Error processing the message: {e}")
                # Don't re-raise to prevent application crash

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from message content: {e}")
        except KeyError as e:
            logger.error(f"Missing required field in message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing the message: {e}")
            # Don't re-raise to prevent application crash
