from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import RegistrationForm, PasswordResetRequestForm  # Import both forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .forms import ProductForm

def index(request):
    return render(request, 'index.html')

def base(request):
    return render(request, 'base.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create a new Tbl_login instance
            login = Tbl_login.objects.create(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']  # Assuming the password is already validated and hashed
            )
            
            # Create a new Tbl_user instance linked to the Tbl_login instance
            Tbl_user.objects.create(
                name=form.cleaned_data['name'],
                dob=form.cleaned_data['dob'],
                phone=form.cleaned_data['phone_number'],
                login=login
            )
            
            messages.success(request, 'Registration successful! You can now log in')
            return redirect('/login/')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Server-side email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address')
            return redirect('/login/')
        
        # Server-side password validation
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('/login/')

        # Check if the user is admin
        if email == 'admin123@gmail.com' and password == 'admin123':
            # Admin login success
            request.session['user_type'] = 'admin'
            request.session['email'] = email
            return redirect('/adminhome/')  # Redirect to admin home page

        # Check if the user is staff
        try:
            staff = Staff.objects.get(login__email=email, login__password=password)
            # Staff login success
            request.session['user_type'] = 'staff'
            request.session['staff_id'] = staff.staff_id
            request.session['email'] = staff.login.email
            return redirect('/staff_home/')  # Redirect to staff dashboard
        except Staff.DoesNotExist:
            pass

        # Check if the user is a regular user
        try:
            user = Tbl_login.objects.get(email=email, password=password)
            # Set session data after successful login
            request.session['user_id'] = user.login_id
            request.session['email'] = user.email
            return redirect('/base_home/')  # Redirect to user home page or dashboard
        except Tbl_login.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('/login/')
    
    return render(request, 'login.html')


def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Tbl_login.objects.get(email=email)
                # Generate a random token (you can customize this)
                reset_token = get_random_string(30)
                user.reset_token = reset_token
                user.save()
                
                # Send reset email (for now, let's print the link)
                reset_link = f"http://http://localhost:8000/reset-password/{reset_token}/"
                # Send the email
                subject = "Password Reset Request"
                message = f"Hi, please click the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email."
                from_email = 'jeeljpaul2025@mca.ajce.in'
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list)
                
                messages.success(request, 'A password reset link has been sent to your email.')
                return redirect('/login/')
            except Tbl_login.DoesNotExist:
                messages.error(request, 'Email address not found')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'password_reset_request.html', {'form': form})

def reset_password(request, token):
    try:
        user = Tbl_login.objects.get(reset_token=token)
    except Tbl_login.DoesNotExist:
        messages.error(request, 'Invalid or expired reset token')
        return redirect('/login/')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password and len(password) >= 8:
            user.password = password  # Hash the password in a real-world scenario
            user.reset_token = ''  # Clear the reset token
            user.save()
            messages.success(request, 'Your password has been reset successfully')
            return redirect('/login/')
        else:
            messages.error(request, 'Passwords do not match or are not long enough')
    
    return render(request, 'password_reset.html')





# admin views.py--------------------------------------------------------------------------------------------

def adminhome(request):
    return render(request, 'admin/adminhome.html')

def add_product(request):
    if request.method == 'POST':
        # Handle the form submission
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Do not save to DB yet
            product.save()  # Save the product first
            images = request.FILES.getlist('images')  # Handle multiple image uploads
            
            # Save each image in the `ProductImage` model
            for image in images:
                Product.objects.create(product=product, image=image)
                
            messages.success(request, 'Product has been added successfully!')
            return redirect('add_product')  # Redirect back to the form after successful submission
        else:
            messages.error(request, 'There was an error in the form. Please check the details.')
    else:
        # If the request is GET, display the form
        form = ProductForm()
    
    return render(request, 'admin/add_product.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.db.models import Q

# View products and filter by category
def view_products(request):
    query = request.GET.get('category', '')  # Get the category from search input
    if query:
        products = Product.objects.filter(Q(category__icontains=query))  # Search by category
    else:
        products = Product.objects.all()  # Display all products if no search query

    return render(request, 'admin/view_products.html', {'products': products})

# View product details
def view_product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'admin/product_details.html', {'product': product})

# Delete a product
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('view_products')
    return render(request, 'admin/view_products.html')



#staff viws.py-------------------------------------------------------------------------------------------------

def staffhome(request):
    return render(request, 'staffhome.html')
