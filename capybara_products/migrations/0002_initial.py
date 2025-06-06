# Generated by Django 5.2 on 2025-05-04 18:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('capybara_categories', '0001_initial'),
        ('capybara_countries', '0001_initial'),
        ('capybara_currencies', '0001_initial'),
        ('capybara_products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='product',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='capybara_categories.category', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='product',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products_by_city', to='capybara_countries.city', verbose_name='City'),
        ),
        migrations.AddField(
            model_name='product',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products_by_country', to='capybara_countries.country', verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='product',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='capybara_currencies.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='capybara_categories.subcategory', verbose_name='Subcategory'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='capybara_products.product', verbose_name='Product'),
        ),
        migrations.AddField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='capybara_products.product'),
        ),
        migrations.AddField(
            model_name='productview',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='capybara_products.product', verbose_name='Product'),
        ),
        migrations.AddField(
            model_name='productview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='unique_user_favorite'),
        ),
        migrations.AddConstraint(
            model_name='productview',
            constraint=models.UniqueConstraint(fields=('product', 'user'), name='unique_product_user_view'),
        ),
    ]
