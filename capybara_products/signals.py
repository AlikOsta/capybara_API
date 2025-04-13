from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductComment
from .utils import moderate_goods


@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    if created or instance.status == 0:
        goods_text = f"{instance.title}\n{instance.description}"
        
        if moderate_goods(goods_text):
            instance.status = 1
        else:
            instance.status = 2
            
        type(instance).objects.filter(pk=instance.pk).update(status=instance.status)


@receiver(post_save, sender=ProductComment)
def product_post_save(sender, instance, created, **kwargs):
    if created or instance.is_active == False:
        goods_text = f"{instance.text}"
        
        if moderate_goods(goods_text):
            instance.is_active == True
        else:
            instance.is_active == False
            
        type(instance).objects.filter(pk=instance.pk)