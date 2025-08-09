import logging

logger = logging.getLogger(__name__)


class DefaultFieldsExtractionService:
    def __init__(self, extractors):
        self.extractors = extractors

    def extract_fields(self, text):
        results = {}
        for extractor in self.extractors:
            try:
                extracted_data = extractor.extract_field(text)
                results[extractor.field_name] = extracted_data
            except Exception as e:
                logger.error(f"Error extracting field '{extractor.field_name}': {e}")
                # Provide default values for failed extractions
                if extractor.field_name == 'title':
                    results[extractor.field_name] = "Не вдалося витягнути заголовок"
                elif extractor.field_name == 'categories':
                    results[extractor.field_name] = []
                elif extractor.field_name == 'format':
                    results[extractor.field_name] = 'офлайн'
                elif extractor.field_name == 'asap':
                    results[extractor.field_name] = False
                else:
                    results[extractor.field_name] = None
        return results
