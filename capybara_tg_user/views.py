from django.shortcuts import render
from rest_framework import generics

from .models import TelegramUser
from .serializers import UserSerializer


class UserAPIView(generics.ListAPIView):
    queryset = TelegramUser.objects.prefetch_related("groups").all()
    serializer_class = UserSerializer
