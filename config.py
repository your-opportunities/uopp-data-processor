import os

from dotenv import load_dotenv

load_dotenv()

# RabbitMQ configs
RABBIT_RAW_QUEUE_NAME = os.environ.get("RABBIT_RAW_QUEUE_NAME")
RABBIT_PROCESSED_QUEUE_NAME = os.environ.get("RABBIT_PROCESSED_QUEUE_NAME")
RABBIT_DELIVERY_MODE = int(os.environ.get("RABBIT_DELIVERY_MODE"))
RABBIT_HOST = os.environ.get("RABBIT_HOST")
RABBIT_PORT = int(os.environ.get("RABBIT_PORT"))
RABBIT_USERNAME = os.environ.get("RABBIT_USERNAME")
RABBIT_PASSWORD = os.environ.get("RABBIT_PASSWORD")
RABBIT_MAX_RETRIES = int(os.environ.get("RABBIT_MAX_RETRIES"))
RABBIT_RETRY_DELAY = int(os.environ.get("RABBIT_RETRY_DELAY"))

# TODO: consider moving strs to some project properties file (but not to .env)
# Models
SPACY_MODEL = "uk_core_news_sm"
HUGGING_FACE_MODEL = "beogradjanka/bart_multitask_finetuned_for_title_and_keyphrase_generation"
HUGGING_FACE_MODEL_TASK = "text2text-generation"
HUGGING_FACE_MODEL_MAX_TOKEN_LENGTH = 20

# Extractor Configurations
TITLE_LABEL = "title"
CATEGORIES_LABEL = "categories"
FORMAT_LABEL = "format"
ASAP_LABEL = "asap"

CATEGORIES_CANDIDATES = ["вебінар", "волонтерство", "грант", "конкурс", "конференція", "курс", "лекція",
                     "майстер-клас", "хакатон", "обмін", "вакансія", "проєкт", "стажування",
                     "стипендія", "табір", "турнір", "тренінг"]
ASAP_CANDIDATES = ["asap", "терміново"]
