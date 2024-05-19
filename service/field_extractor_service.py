class DefaultFieldsExtractionService:
    def __init__(self, extractors):
        self.extractors = extractors

    def extract_fields(self, text):
        results = {}
        for extractor in self.extractors:
            extracted_data = extractor.extract_field(text)
            results[extractor.field_name] = extracted_data
        return results
