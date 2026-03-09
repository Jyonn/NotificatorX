import uuid
import oba
import json

from smartdjango import Error, Code, OK
from django.utils import timezone

from Channel.channels.bark import Bark
from Channel.channels.mail import Mail
from Channel.models import ChannelDeliveryLog
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
    def to_json_text(cls, value):
        return json.dumps(value, ensure_ascii=False, default=str)

    @classmethod
    def send(cls, message, deliveries, account):
        message = oba.raw(message)
        request_id = str(uuid.uuid4())

        for delivery in deliveries:
            delivery_data = oba.raw(delivery)
            channel_key = delivery_data['channel']
            channel = cls.channels.get(channel_key)
            if channel is None:
                raise DispatchErrors.UNSUPPORTED_CHANNEL(channel=channel_key)
            log = ChannelDeliveryLog.objects.create(
                request_id=request_id,
                account=account,
                channel=channel_key,
                message=cls.to_json_text(message),
                delivery=cls.to_json_text(delivery_data),
                success=False,
            )
            try:
                channel.run(
                    target=delivery_data['target'],
                    message=message,
                    options=oba.raw(delivery_data.get('options') or {}),
                    user=account,
                )
                log.success = True
                log.finish_time = timezone.now()
                log.save(update_fields=['success', 'finish_time'])
            except Exception as err:
                log.error = str(err)
                log.finish_time = timezone.now()
                log.save(update_fields=['error', 'finish_time'])
                raise

        return {
            'request_id': request_id,
        }
