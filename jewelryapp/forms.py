from datetime import date
from django import forms
from .models import Tbl_login, Tbl_user, Product, Tbl_staff
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import EmailValidator
import re


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=10)

    class Meta:
        model = Tbl_user
        fields = ['name', 'dob', 'phone']

    # Name validation: only letters allowed
    def clean_name(self):
        name = self.cleaned_data.get('name')
    
    # Check if name contains only alphabetic characters and spaces
        if not all(char.isalpha() or char.isspace() for char in name):
            raise forms.ValidationError("Name can only contain letters")
    
    # Ensure name doesn't consist of just spaces
        if not name.strip():
            raise forms.ValidationError("Name cannot be empty or just spaces.")
    
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

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Check if the phone number contains only digits
        if not phone.isdigit():
            raise forms.ValidationError("Invalid format.")
            # Check if the phone number is exactly 10 digits long
            if len(phone) != 10:
                raise forms.ValidationError("Invalid format.")
                # Check if the phone number starts with either 6 or 9
                if phone[0] not in ['6', '9']:
                    raise forms.ValidationError("Invalid.")
                return phone


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
