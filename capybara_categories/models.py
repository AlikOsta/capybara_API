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
    


class Rubric(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Rubric")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Order")
    slug = models.SlugField(max_length=30, verbose_name="Slug")
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True, related_name='sub_rubrics', verbose_name="Super Rubric")
    image = models.ImageField(upload_to='images/rubric_img/')


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)
    

class SuperRubric(Rubric):
    objects = SuperRubricManager()
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        proxy = True
        ordering = ['order', 'name']
        verbose_name = 'Super Rubric'
        verbose_name_plural = 'Super Rubrics'


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)
    

class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self)-> str:
        return f'{self.super_rubric.name} - {self.name}'

    class Meta:
        proxy = True
        ordering = ['super_rubric__order', 'super_rubric__name', 'order', 'name']
        verbose_name = 'Sub Rubric'
        verbose_name_plural = 'Sub Rubrics'