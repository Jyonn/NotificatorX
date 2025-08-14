import abc

from pydantic import BaseModel
from smartdjango import Error, Code


@Error.register
class ChannelErrors:
    INACTIVE = Error("Channel Inactive", code=Code.Forbidden)


class BaseChannel(abc.ABC):
    active = True

    @classmethod
    def handler(cls, body: BaseModel, user):
        raise NotImplementedError

    @classmethod
    def run(cls, body: BaseModel, user):
        if not cls.active:
            raise ChannelErrors.INACTIVE
        return cls.handler(body, user)
