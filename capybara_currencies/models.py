from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    code = models.CharField(max_length=8, db_index=True, verbose_name="Код")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"
        ordering = ['order']

    def __str__(self) -> str:
        return self.name


