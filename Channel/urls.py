from django.urls import path

from Channel import views

urlpatterns = [
    path('', views.ChannelView.as_view()),
    path('bark', views.BarkView.as_view()),
    path('sms', views.SMSView.as_view()),
    path('mail', views.MailView.as_view()),
]
