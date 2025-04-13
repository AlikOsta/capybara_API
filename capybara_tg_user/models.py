from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


class TelegramUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    photo_url = models.URLField(blank=True, null=True, verbose_name='Photo URL')
    country = models.ForeignKey('capybara_countries.Country', on_delete=models.PROTECT, verbose_name='Country', null=True, blank=True)
    city = models.ForeignKey('capybara_countries.City', on_delete=models.PROTECT, verbose_name='City', null=True, blank=True)
    average_rating = models.FloatField(default=0, verbose_name='Average Rating')
    rating_count = models.PositiveIntegerField(default=0, verbose_name='Rating Count')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'telegram_id']

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return self.get_full_name() or self.username or str(self.telegram_id)
    
    def det_absolute_url(self):
        return reverse('user:user-profile', kwargs={'pk': self.pk})


class UserRating(models.Model):
    rated_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='rated_by', verbose_name='Rated User')
    rating_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='rating_by', verbose_name='Rating User')
    rating = models.PositiveSmallIntegerField(verbose_name='Rating')
    comment = models.TextField(blank=True, null=True, verbose_name='Comment')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name = 'User Rating'
        verbose_name_plural = 'User Ratings'
        unique_together = ('rated_user', 'rating_user')

