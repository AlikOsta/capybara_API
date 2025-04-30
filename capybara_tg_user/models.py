from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator


class TelegramUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    photo_url = models.URLField(blank=True, null=True, verbose_name='Photo URL')
    language =  models.CharField(max_length=5, default='en', verbose_name='Language')
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
    
    @property
    def average_rating(self):
        """Возвращает средний рейтинг пользователя"""
        return self.received_ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    @property
    def ratings_count(self):
        """Возвращает количество полученных оценок"""
        return self.received_ratings.count()


class UserRating(models.Model):
    from_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='given_ratings', verbose_name='Rated User')
    to_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_ratings', verbose_name='Rating User')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Rating')
    comment = models.TextField(max_length=50, blank=True, null=True, verbose_name='Comment')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name = 'User Rating'
        verbose_name_plural = 'User Ratings'
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                name='unique_user_rating'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}: {self.rating}"
    
    def clean(self):
        """Проверка, что пользователь не оценивает сам себя"""
        from django.core.exceptions import ValidationError
        
        if self.from_user == self.to_user:
            raise ValidationError("Пользователь не может оценить сам себя")


