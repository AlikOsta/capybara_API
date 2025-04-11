from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Name")
    code = models.CharField(max_length=8, db_index=True, verbose_name="Code")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Order')

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ['order']

    def __str__(self) -> str:
        return self.name


