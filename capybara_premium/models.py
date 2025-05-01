from django.db import models
from django.utils import timezone


class PremiumPlan(models.Model):
    name = models.CharField(max_length=30, verbose_name="Name")
    duration_days = models.IntegerField(verbose_name="Duration (days)")
    price = models.ImageField(default=0, verbose_name="Price")
    description = models.TextField(verbose_name="Description")
    is_active = models.BooleanField(default=False, verbose_name="Is active")

    class Meta:
        verbose_name = "Premium plan"
        verbose_name_plural = "Premium plans"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} ({self.duration_days} дней, {self.price})"
    

class ProductPremium(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='premium_product', verbose_name='Product')
    plan = models.ForeignKey('PremiumPlan', on_delete=models.CASCADE, verbose_name='Premium plan')
    start_date = models.DateTimeField(default=timezone.now, verbose_name='Start date')
    end_date = models.DateTimeField(verbose_name='End date')
    is_active = models.BooleanField(default=False, verbose_name='Is active')
    payment_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='Payment ID')

    class Meta:
        verbose_name = "Product premium"
        verbose_name_plural = "Product premiums"
        ordering = ["-end_date"]

    def __str__(self):
        return f"Премиум для {self.product.title} до {self.end_date.strftime('%d.%m.%Y')}"
    
    def save(self, *args, **kwargs):

        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=self.plan.duration_days)
