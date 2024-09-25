# Generated by Django 5.1 on 2024-09-24 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelryapp', '0006_product_status_tbl_login_last_login_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='product',
            name='gemstones',
        ),
        migrations.RemoveField(
            model_name='product',
            name='return_policy',
        ),
        migrations.RemoveField(
            model_name='product',
            name='status',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='product',
            name='try_at_home',
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='product',
            name='gender',
            field=models.CharField(choices=[('Men', 'Men'), ('Women', 'Women'), ('Unisex', 'Unisex')], default='Unisex', max_length=6),
        ),
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ImageField(default='', upload_to='pic/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
