# Generated by Django 5.1 on 2024-10-09 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jewelryapp', '0002_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='category',
            new_name='category_id',
        ),
    ]