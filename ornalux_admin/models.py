from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Ring', 'Ring'),
        ('Earring', 'Earring'),
        ('Bracelet', 'Bracelet'),
    ]

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
    ]

    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.CharField(max_length=100)
    metal_type = models.CharField(max_length=100)
    gemstones = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    occasion = models.CharField(max_length=100)
    sku = models.CharField(max_length=100, unique=True)
    try_at_home = models.BooleanField(default=False)
    delivery_options = models.TextField()
    return_policy = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)
    images = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.product_name
