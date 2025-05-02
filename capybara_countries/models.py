from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="Country")
    currencies = models.ManyToManyField("capybara_currencies.Currency", related_name="countries", verbose_name="Валюты")
    
    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="City")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities", verbose_name="Country")

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
    


class Local(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Local")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Order")
    slug = models.SlugField(max_length=30, verbose_name="Slug")
    super_Local = models.ForeignKey(
        'SuperLocal',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='sub_local',
        verbose_name="Super Local"
    )

    def __str__(self):
        return self.name


class SuperLocalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_Local__isnull=True)


class SuperLocal(Local):
    objects = SuperLocalManager()

    class Meta:
        proxy = True
        ordering = ['order', 'name']
        verbose_name = 'Super Local'
        verbose_name_plural = 'Super Locals'


class SubLocalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_Local__isnull=False)


class SubLocal(Local):
    objects = SubLocalManager()

    class Meta:
        proxy = True
        ordering = ['super_Local__order', 'super_Local__name', 'order', 'name']
        verbose_name = 'Sub Local'
        verbose_name_plural = 'Sub Locals'