from field_extractor.abstract_lemmatization_field_extractor import AbstractLemmatizationFieldExtractor


class AsapFieldExtractor(AbstractLemmatizationFieldExtractor):
    def __init__(self, field_name, nlp, labels):
        super().__init__(field_name, nlp, labels)

    def extract_field(self, text):
        found_asap_terms = []
        doc = self.nlp(text)
        for token in doc:
            lemma = token.lemma_
            if lemma in self.lemmatized_labels.values():
                found_asap_terms.append(lemma)
        return bool(found_asap_terms)
