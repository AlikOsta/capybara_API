from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from choices import STATUS_CHOICES
from .utils_img import process_image


class Product(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Author")
    category =models.ForeignKey("Category", on_delete=models.PROTECT, db_index=True, verbose_name="Category")
    title = models.CharField(max_length=50, db_index=True, verbose_name="Title")
    description = models.TextField(max_length = 350, verbose_name = "Description")
    price = models.IntegerField(verbose_name="Price")
    currency = models.ForeignKey("Currency", null=True, on_delite=models.PROTECT, verbose_name="Currency")
    country = models.ForeignKey("Country", null=True, on_delete=models.PROTECT, verbose_name="Country")
    city = models.ForeignKey("City", null=True, on_delete=models.PROTECT, db_index=True, verbose_name="City")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="Status")
    create_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name="Date create")
    update_at = models.DateTimeField(auto_now=True, verbose_name="Date update")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-create_at"]
        indexes = [
            models.Index(fields=["title", "status"]),
            models.Index(fields=["price", "status"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["country", "status"]),
        ]

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk})
    
    @property
    def main_image(self):
        """Возвращает главное изображение продукта (первое в списке)"""
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", verbose_name="Image")
    is_main = models.BooleanField(default=False, verbose_name="Main image")
    
    def save(self, *args, **kwargs):
        
        is_new = not self.id
        if is_new:
            super().save(*args, **kwargs)
        
        if self.image and (is_new or 'image' in self.__dict__):
            self.image = process_image(self.image, self.id)

        super().save(*args, **kwargs)
