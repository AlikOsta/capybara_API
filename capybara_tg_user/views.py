from django.shortcuts import render
from rest_framework import generics

from .models import TelegramUser
from .serializers import UserSerializer


class CurrencyAPIView(generics.ListAPIView):
    queryset = TelegramUser.objects.all()
    serializer_class = UserSerializer
