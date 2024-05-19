from abc import ABC

from field_extractor.abstract_field_extractor import AbstractFieldExtractor


class AbstractLemmatizationFieldExtractor(AbstractFieldExtractor, ABC):
    def __init__(self, field_name, nlp, labels):
        super().__init__(field_name)
        self.nlp = nlp
        self.lemmatized_labels = self.lemmatize_labels(labels)

    def lemmatize_labels(self, labels):
        """Lemmatize a list of labels using the loaded NLP model."""
        return {label: self.nlp(label)[0].lemma_ for label in labels}
