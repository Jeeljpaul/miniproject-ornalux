# Generated by Django 5.1 on 2024-10-27 04:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelryapp', '0021_cartitem_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house_name', models.CharField(max_length=255)),
                ('postal_address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=50)),
                ('district', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=6)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jewelryapp.tbl_user')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('billing', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jewelryapp.billing')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jewelryapp.cart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jewelryapp.tbl_user')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='jewelryapp.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jewelryapp.product')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=100, null=True)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jewelryapp.order')),
            ],
        ),
    ]