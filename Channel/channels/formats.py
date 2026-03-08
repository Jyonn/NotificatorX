class MessageFormats:
    TEXT = 'text'
    HTML = 'html'
    MARKDOWN = 'markdown'
    JSON = 'json'
    ALL = (TEXT, HTML, MARKDOWN, JSON)

    @classmethod
    def all(cls):
        return list(cls.ALL)
