# Generated by Django 5.1 on 2024-10-18 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelryapp', '0016_alter_wishlist_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='try_at_home',
            field=models.BooleanField(default=False),
        ),
    ]
