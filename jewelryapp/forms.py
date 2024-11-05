from datetime import date
from django import forms
from .models import Tbl_login, Tbl_user, Product, Tbl_staff
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import EmailValidator
import re

# Password Reset Request Form should be outside the RegistrationForm class
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control'
    }))

from django import forms
from .models import Tbl_login, Tbl_staff

class StaffForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.CharField(max_length=100)
    contact_details = forms.CharField(max_length=255)
    
    def save(self):
        # Save login details
        login = Tbl_login.objects.create(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        # Save staff details
        Tbl_staff.objects.create(
            name=self.cleaned_data['name'],
            role=self.cleaned_data['role'],
            contact_details=self.cleaned_data['contact_details'],
            login=login
        )



from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter product description'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock quantity'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter weight'}),
            'metal_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter metal type'}),
            'stone_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stone type'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'occasion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter occasion'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'delivery_options': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter delivery options'}),
        }

        
from django import forms
from .models import Booking

class EditBookingForm(forms.ModelForm):
    phone = forms.CharField(label='Phone Number', max_length=15)  # Custom field for phone

    class Meta:
        model = Booking
        fields = ['address', 'phone']  # 'phone' is added here as a custom field

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass the user instance
        super().__init__(*args, **kwargs)
        if user:
            self.fields['phone'].initial = user.phone  # Set initial phone value from user
