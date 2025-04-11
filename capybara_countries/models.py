from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="Country")
    currencies = models.ManyToManyField("capybara_currencies.Currency", related_name="countries", verbose_name="Валюты")
    
    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="City")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities", verbose_name="Country")

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self):
        return self.name