from django.urls import path

from Channel import views

urlpatterns = [
    path('', views.ChannelView.as_view()),
    path('send', views.SendView.as_view()),
    path('mail', views.MailSenderListView.as_view()),
    path('mail/<str:sender_id>', views.MailSenderItemView.as_view()),
]
