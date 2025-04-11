from django.contrib.auth.models import AbstractUser
from django.db import models


class TelegramUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    photo_url   = models.URLField(blank=True, null=True, verbose_name='Photo URL')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'telegram_id']

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return self.get_full_name() or self.username or str(self.telegram_id)