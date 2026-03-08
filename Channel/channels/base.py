import abc

from smartdjango import Error, Code, OK

from Channel.channels.formats import MessageFormats


@Error.register
class ChannelErrors:
    INACTIVE = Error("Channel Inactive", code=Code.Forbidden)
    INVALID_FORMAT = Error("Invalid message format", code=Code.BadRequest)
    FORMAT_UNSUPPORTED = Error(
        "Format [{format}] is not supported by channel [{channel}]",
        code=Code.BadRequest
    )


class BaseChannel(abc.ABC):
    key = ''
    active = False
    supported_formats = {MessageFormats.TEXT}

    @classmethod
    def get_key(cls):
        return cls.key or cls.__name__.lower()

    @classmethod
    def get_effective_format(cls, message: dict, options: dict):
        format_ = (
            (options or {}).get('format')
            or (message or {}).get('format')
            or MessageFormats.TEXT
        )
        if not isinstance(format_, str):
            raise ChannelErrors.INVALID_FORMAT
        format_ = format_.strip().lower()
        if not format_:
            raise ChannelErrors.INVALID_FORMAT
        return format_

    @classmethod
    def supports_format(cls, format_: str):
        return format_ in cls.supported_formats

    @classmethod
    def handler(cls, target: str, message: dict, options: dict, user, format_: str):
        raise NotImplementedError

    @classmethod
    def run(cls, target: str, message: dict, options: dict, user):
        if not cls.active:
            raise ChannelErrors.INACTIVE
        format_ = cls.get_effective_format(message, options)
        if not cls.supports_format(format_):
            raise ChannelErrors.FORMAT_UNSUPPORTED(
                format=format_,
                channel=cls.get_key(),
            )
        cls.handler(target, message, options or {}, user, format_)

        return OK
