from django.urls import path, include

from NotificatorX import views

urlpatterns = [
    path('auth', views.AuthView.as_view()),
    path('account/', include('Account.urls')),
    path('channel/', include('Channel.urls')),
    path('error', views.ErrorView.as_view()),
]
