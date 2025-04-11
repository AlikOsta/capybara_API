from django.urls import path
from .views import UserAPIView


app_name = 'user'

urlpatterns = [
    path('api/v1/user/',  UserAPIView.as_view()), #'currencies/api/v1/currency_list/',
]
