from datetime import timedelta
from django.utils import timezone
from .models import Product

def archive_old_products():
    one_day_ago = timezone.now() - timedelta(days=28)
    
    old_products = Product.objects.filter(
        status=3, 
        updated_at__lt=one_day_ago 
    )
    
    count = old_products.update(status=4)
    
    return f"Archived {count} ads"
