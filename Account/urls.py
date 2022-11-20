from django.urls import path

from Account import views

urlpatterns = [
    path('', views.AccountView.as_view()),
]
