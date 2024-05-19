from field_extractor.abstract_lemmatization_field_extractor import AbstractLemmatizationFieldExtractor


class CategoryFieldExtractor(AbstractLemmatizationFieldExtractor):
    def __init__(self, field_name, nlp, labels):
        super().__init__(field_name, nlp, labels)

        """
        TODO: Drawback: no context considered during extraction 
        """

    def extract_field(self, text):
        found_categories = []
        doc = self.nlp(text)
        for token in doc:
            lemma = token.lemma_
            if lemma in self.lemmatized_labels.values():
                found_categories.append(lemma)
        return list(set(found_categories))
