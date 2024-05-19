from transformers import pipeline

from field_extractor.abstract_field_extractor import AbstractFieldExtractor


class TitleFieldExtractor(AbstractFieldExtractor):
    def __init__(self, field_name, translator, pipeline):
        super().__init__(field_name)
        self.translator = translator
        self.pipeline = pipeline

    def translate_text(self, text, src, dest):
        translation = self.translator.translate(text, src=src, dest=dest)
        return translation.text


    def extract_field(self, text):
        '''
        The model used in title generation is specified in English,
        which is why there is logic with translating processed language (Ukrainian)

        TODO: The approach is bad because of the risk of losing info/meaning during translation.
        Possible solutions are to find a Ukrainian model specified on title generation or create a new one
        '''
        # Translate text to English
        text_en = self.translate_text(text, src='uk', dest='en')

        # Generate title in English
        result = self.pipeline(text_en)
        title_en = result[0]['generated_text']

        # Translate the title back to Ukrainian
        title_uk = self.translate_text(title_en, src='en', dest='uk')
        return title_uk
