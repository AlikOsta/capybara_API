from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

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
    # end_date = models.DateTimeField(verbose_name='End date')

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
    
    @property
    def main_image(self):
        """Возвращает первое изображение из списка"""
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None
    
    @property
    def premium_info(self):
        """Возвращает информацию о премиум-статусе, если он есть"""
        try:
            return self.is_premium
        except:
            return None
    

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


class ProductComment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='comments', verbose_name='Product')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='User')
    text = models.TextField(max_length=500, verbose_name='Comment')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name = 'Product Comment'
        verbose_name_plural = 'Product Comments'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], 
                name='unique_user_product_comment'
            )
        ]

    def __str__(self):
        return f'Comment by {self.user.username} on {self.product.title}'
    

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

        if self.end_date <= timezone.now():
            self.is_active = False
        
        super().save(*args, **kwargs)