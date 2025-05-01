from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from .choices import STATUS_CHOICES
from .utils_img import process_image


class Product(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Author")
    category =models.ForeignKey("capybara_categories.Category", on_delete=models.PROTECT, db_index=True, related_name="products", verbose_name="Category")
    title = models.CharField(max_length=50, db_index=True, verbose_name="Title")
    description = models.TextField(max_length = 550, verbose_name = "Description")
    country = models.ForeignKey("capybara_countries.Country", on_delete=models.PROTECT, verbose_name="Country")
    city = models.ForeignKey("capybara_countries.City", on_delete=models.PROTECT, db_index=True, verbose_name="City")
    price = models.IntegerField(verbose_name="Price")
    currency = models.ForeignKey("capybara_currencies.Currency", on_delete=models.PROTECT, verbose_name="Currency")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="Status")
    is_premium = models.BooleanField(default=False, verbose_name="Is premium")
    create_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Date create")
    update_at = models.DateTimeField(auto_now=True, verbose_name="Date update")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-create_at"]

    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self) -> str:
        return reverse("product:product_detail", kwargs={"pk": self.pk})
    
    def get_author_url(self) -> str:
        return reverse("user-detail", kwargs={"pk": self.author.pk})
    
    def get_view_count(self) -> int:
        return self.views.count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", verbose_name="Image")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            processed = process_image(self.image, self.pk)

            if processed != self.image:
                self.image = processed
                super().save(update_fields=['image'])


class Favorite(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='favorites', verbose_name="User")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name='favorited_by', verbose_name="Product")
    create_at = models.DateTimeField(auto_now=True, verbose_name="Date create")

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_favorite')
        ]
        ordering = ["-create_at"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.product.title}"


class ProductView(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='views', verbose_name='Product')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='User')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    class Meta:
        verbose_name = 'Product View'
        verbose_name_plural = 'Product Views'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_product_user_view'
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product.title} - {self.user.username}"
    