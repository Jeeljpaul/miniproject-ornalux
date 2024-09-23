from datetime import date
from django import forms
from .models import Tbl_login, Tbl_user, Product
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=10)

    class Meta:
        model = Tbl_user
        fields = ['name', 'dob', 'phone_number']

    # Name validation: only letters allowed
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.isalpha():
            raise forms.ValidationError("Invalid format.")
        return name

    # Date of birth validation: not current or future year, and age must be at least 18
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        current_date = date.today()
        current_year = current_date.year

        # Check if the date of birth is in the current year or a future year
        if dob.year >= current_year:
            raise forms.ValidationError("Cannot register.")
        
        # Calculate the user's age
        age = current_year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
        
        # Ensure the user is at least 18 years old
        if age < 18:
            raise forms.ValidationError("Cannot register.")
        
        return dob

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Check if the phone number contains only digits
        if not phone_number.isdigit():
            raise forms.ValidationError("Invalid format.")
            # Check if the phone number is exactly 10 digits long
            if len(phone_number) != 10:
                raise forms.ValidationError("Invalid format.")
                # Check if the phone number starts with either 6 or 9
                if phone_number[0] not in ['6', '9']:
                    raise forms.ValidationError("Invalid.")
                    return phone_number


    # Email validation: check for uniqueness and format
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        if Tbl_login.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        return email

    # Password validation: minimum 8 characters, must include letters, numbers, and special characters
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[@$!%*?&#]', password):
            raise forms.ValidationError("Password must include at least one letter, one number, and one special character.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)

        # Create the associated login entry
        login = Tbl_login(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']  # Normally you'd hash the password here
        )

        if commit:
            login.save()
            user.login_id = login  # Link the user to the login entry
            user.save()

        return user

# Password Reset Request Form should be outside the RegistrationForm class
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control'
    }))

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'product_name', 'product_description', 'category', 'subcategory', 'price',
            'discount', 'stock_quantity', 'weight', 'material', 'metal_type', 'gemstones',
            'gender', 'occasion', 'sku', 'try_at_home', 'delivery_options', 'return_policy', 'tags'
        ]

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if re.search(r'\d|[^a-zA-Z\s]', product_name):
            raise ValidationError("Product name cannot contain numbers or special characters.")
        return product_name

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        if re.search(r'\d|[^a-zA-Z\s]', subcategory):
            raise ValidationError("Subcategory cannot contain numbers or special characters.")
        return subcategory

    def clean_material(self):
        material = self.cleaned_data.get('material')
        if re.search(r'\d|[^a-zA-Z\s]', material):
            raise ValidationError("Material cannot contain numbers or special characters.")
        return material

    def clean_metal_type(self):
        metal_type = self.cleaned_data.get('metal_type')
        if re.search(r'\d|[^a-zA-Z\s]', metal_type):
            raise ValidationError("Metal type cannot contain numbers or special characters.")
        return metal_type

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity <= 0:
            raise ValidationError("Stock quantity must be a positive number.")
        return stock_quantity

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight <= 0:
            raise ValidationError("Weight must be greater than 0 grams.")
        return weight

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if re.search(r'[^a-zA-Z0-9]', sku):
            raise ValidationError("SKU can only contain letters and numbers.")
        return sku
