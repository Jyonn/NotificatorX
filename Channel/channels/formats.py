class MessageFormats:
    TEXT = 'text'
    HTML = 'html'
    MARKDOWN = 'markdown'
    JSON = 'json'
    VERIFICATION = 'verification'
    ALL = (TEXT, HTML, MARKDOWN, JSON, VERIFICATION)

    @classmethod
    def all(cls):
        return list(cls.ALL)
