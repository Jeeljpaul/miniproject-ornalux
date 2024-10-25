from django.db import models
from django.utils import timezone

class Tbl_login(models.Model):
    login_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=30, unique=True)  # Ensure email is unique
    password = models.CharField(max_length=30)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    def login(self):
        """ Logs the user in by updating the login timestamp, status, and login count. """
        self.status = True  # Set status to True on login
        self.last_login = timezone.now()
        self.login_count += 1
        self.save()


    def __str__(self):
        return self.email


class Tbl_user(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    dob = models.DateField()
    phone = models.CharField(max_length=15)
    login = models.OneToOneField(Tbl_login, on_delete=models.CASCADE)  # One-to-One relationship
    status = models.BooleanField(default=True)


    def __str__(self):
        return self.name


class Tbl_staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    contact_details = models.CharField(max_length=15)  # Assuming contact details like phone number
    login = models.ForeignKey(Tbl_login, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)


    def __str__(self):
        return self.name

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    

    def __str__(self):
        return self.name

class CategoryAttribute(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    datatype = models.CharField(max_length=50, choices=[
        ('string', 'String'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
    ],
     default='string'
    )



    def __str__(self):
        return f"{self.name} ({self.category.name}) ({self.datatype})"
    
class Metaltype(models.Model):
    metaltype_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Stonetype(models.Model):
    stonetype_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Model for Product
class Product(models.Model):
    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
        ('Kids', 'Kids'),
        ('Baby', 'Baby')
    ]

    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    product_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='Unisex')
    occasion = models.CharField(max_length=255)
    images = models.ImageField(upload_to='pic/', default='')
    metaltype = models.ForeignKey(Metaltype, on_delete=models.CASCADE, null=True, blank=True)
    stonetype = models.ForeignKey(Stonetype, on_delete=models.CASCADE, null=True, blank=True)
    home_delivery = models.BooleanField(default=False)
    store_pickup = models.BooleanField(default=False)
    try_at_home = models.BooleanField(default=False)
    bestselling = models.BooleanField(default=False)

    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product_name
    
    
class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute_name = models.CharField(max_length=100)
    attribute_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value} for {self.product.product_name}"
    

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    login = models.OneToOneField(Tbl_login, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.login.email}"

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

class CartItem(models.Model):
    cartitem_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in cart"
    


class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    login = models.ForeignKey(Tbl_login, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of User ID: {self.login.user_id}"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} in Wishlist ID: {self.wishlist.id}"


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Tbl_user, on_delete=models.CASCADE)  # User who makes the booking
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product being booked
    address = models.TextField()  # User's address for the booking
    booking_date = models.DateField()  # Date of the booking
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the booking was created
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending')
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"Booking {self.booking_id} by {self.user.name} for {self.product.product_name} on {self.booking_date}"
