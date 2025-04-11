from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Catogory")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Order")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to='media/images/cat_img/', blank=True, null=True, verbose_name="Image")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order']
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = self.name.lower().replace(' ', '-')
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category:category_detail", kwargs={"pk": self.pk})
    
