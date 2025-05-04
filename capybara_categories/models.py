from django.db import models
from django.urls import reverse
from slugify import slugify


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Catogory")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Order")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to='images/cat_img/')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order']
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'slug': self.slug})
    
    def get_count_products(self):
        products = self.products.filter(status=3)
        return products.count()
    

class SubCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Subcategory")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Order")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="Category")
    image = models.ImageField(upload_to='images/subcat_img/')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('subcategory-detail', kwargs={'slug': self.slug})

    def get_count_products(self):
        products = self.products.filter(status=3)
        return products.count()
    
    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ['order']


