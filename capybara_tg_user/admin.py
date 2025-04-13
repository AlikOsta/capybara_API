from django.contrib import admin
from .models import TelegramUser, UserRating

admin.site.register(TelegramUser)
admin.site.register(UserRating)