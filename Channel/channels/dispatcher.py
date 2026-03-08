import uuid
import oba

from smartdjango import Error, Code, OK

from Channel.channels.bark import Bark
from Channel.channels.mail import Mail
from Channel.channels.sms import SMS
from Channel.channels.webhook import Webhook


@Error.register
class DispatchErrors:
    UNSUPPORTED_CHANNEL = Error("Unsupported channel [{channel}]", code=Code.BadRequest)


class ChannelDispatcher:
    channels = {
        SMS.get_key(): SMS,
        Mail.get_key(): Mail,
        Bark.get_key(): Bark,
        Webhook.get_key(): Webhook,
    }

    @classmethod
    def active_channels(cls):
        return [key for key, channel in cls.channels.items() if channel.active]

    @classmethod
    def send(cls, message, deliveries, account):
        message = oba.raw(message)
        # deliveries = oba.raw(deliveries)

        for delivery in deliveries:
            channel_key = delivery.channel
            channel = cls.channels.get(channel_key)
            if channel is None:
                raise DispatchErrors.UNSUPPORTED_CHANNEL(channel=channel_key)
            channel.run(
                target=delivery.target,
                message=message,
                options=oba.raw(delivery.options or {}),
                user=account,
            )

        return OK
        # return {
        #     'request_id': str(uuid.uuid4()),
        #     'message': message,
        #     'deliveries': deliveries,
        # }
