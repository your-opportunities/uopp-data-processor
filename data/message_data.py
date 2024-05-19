from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class RawMessageData:
    post_creation_time: datetime
    scrapped_creation_time: datetime
    channel_id: int
    channel_name: str
    message_text: str

    def as_dict(self):
        return {
            "post_creation_time": self.post_creation_time.isoformat(),
            "scrapped_creation_time": self.scrapped_creation_time.isoformat(),
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "message_text": self.message_text
        }


@dataclass
class ProcessedMessageData:
    title: str
    categories: list[str]
    format: str
    asap: bool

    def as_dict(self):
        return asdict(self)


@dataclass
class FullMessageData:
    raw_message_data: RawMessageData
    processed_message_data: ProcessedMessageData

    def as_dict(self):
        return {
            "raw_message_data": self.raw_message_data.as_dict(),
            "processed_message_data": self.processed_message_data.as_dict()
        }
