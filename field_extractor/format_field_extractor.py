from field_extractor.abstract_field_extractor import AbstractFieldExtractor


class FormatFieldExtractor(AbstractFieldExtractor):
    ONLINE = 'онлайн'
    OFFLINE = 'офлайн'

    def __init__(self, field_name):
        super().__init__(field_name)

    def extract_field(self, text):
        """
        Based on superficial analysis, this approach assumes that the explicit presence of 'online' is a definitive
        indicator of an 'online' event, absence - an indicator of an "offline" event.

        TODO: The approach was efficient during testing, but it should be revised.
        Possible inconsistencies in the future:
            - 'offline' and 'online' are mentioned together
            - the text has a complex and ambiguous meaning
        """
        if self.ONLINE in text.lower():
            return self.ONLINE
        else:
            return self.OFFLINE
