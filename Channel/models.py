from django.db import models

from Account.models import Account


class ChannelDeliveryLog(models.Model):
    request_id = models.CharField(max_length=36, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='channel_delivery_logs')
    channel = models.CharField(max_length=32)
    message = models.TextField()
    delivery = models.TextField()
    request_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'Channel_delivery_log'
