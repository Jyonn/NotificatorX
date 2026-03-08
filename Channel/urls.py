from django.urls import path

from Channel import views

urlpatterns = [
    path('', views.ChannelView.as_view()),
    path('send', views.SendView.as_view()),
    path('bark', views.BarkView.as_view()),
    path('sms', views.SMSView.as_view()),
    path('mail', views.MailView.as_view()),
    path('webhook', views.WebhookView.as_view()),
    path('mail-senders', views.MailSenderListView.as_view()),
    path('mail-senders/<str:sender_id>', views.MailSenderItemView.as_view()),
]
