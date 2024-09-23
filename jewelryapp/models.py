from django.db import models

class Tbl_login(models.Model):
    login_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=30, unique=True)  # Ensure email is unique
    password = models.CharField(max_length=30)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.email


class Tbl_user(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    dob = models.DateField()
    phone = models.CharField(max_length=15)
    login = models.OneToOneField(Tbl_login, on_delete=models.CASCADE)  # One-to-One relationship

    def __str__(self):
        return self.name


class Tbl_staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    contact_details = models.CharField(max_length=15)  # Assuming contact details like phone number
    login = models.ForeignKey(Tbl_login, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Ring', 'Ring'),
        ('Earring', 'Earring'),
        ('Bracelet', 'Bracelet'),
        # Add more categories as needed
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
    subcategory = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Assuming a price with 2 decimal places
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Discount is optional
    stock_quantity = models.IntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)  # For weight in grams
    material = models.CharField(max_length=255)
    metal_type = models.CharField(max_length=255)
    gemstones = models.CharField(max_length=255, null=True, blank=True)  # Optional gemstones field
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    occasion = models.CharField(max_length=255)
    images = models.ImageField(upload_to='product_images/', null=True, blank=True)  # Image field, can store multiple images separately in DB
    sku = models.CharField(max_length=100, unique=True)
    try_at_home = models.BooleanField(default=False)  # Boolean for try at home option
    delivery_options = models.TextField()
    return_policy = models.TextField(null=True, blank=True)  # Optional return policy
    tags = models.CharField(max_length=255, null=True, blank=True)  # Optional tags

    def __str__(self):
        return self.product_name

 