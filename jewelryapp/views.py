from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import RegistrationForm, PasswordResetRequestForm  # Import both forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

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
                phone=form.cleaned_data['phone'],
                login=login
            )
            
            messages.success(request, 'Registration successful! You can now log in')
            return redirect('/login/')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Tbl_login, Tbl_user, Tbl_staff

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

        # Check if the user is admin (fetch from Tbl_login table)
        try:
            admin = Tbl_login.objects.get(email=email, password=password)
            if email == 'admin123@gmail.com':  # Assuming admin email is known
                # Admin login success
                request.session['user_type'] = 'admin'
                request.session['user_id'] = admin.login_id
                request.session['email'] = admin.email
                request.session['name'] = 'Admin'  # Static name for admin
                return redirect('/adminhome/')  # Redirect to admin home page
        except Tbl_login.DoesNotExist:
            pass
        
        # Check if the user is staff
        try:
            staff = Tbl_staff.objects.get(login__email=email, login__password=password)
            # Staff login success
            request.session['user_type'] = 'staff'
            request.session['staff_id'] = staff.staff_id
            request.session['email'] = staff.login.email
            request.session['name'] = staff.name  # Fetch the staff's name
            return redirect('/staff_home/')  # Redirect to staff dashboard
        except Tbl_staff.DoesNotExist:
            pass

        # Check if the user is a regular user
        try:
            user_login = Tbl_login.objects.get(email=email, password=password)
            # Fetch the corresponding user details from Tbl_user
            user = Tbl_user.objects.get(login_id=user_login.login_id)
            # Regular user login success
            request.session['user_type'] = 'user'
            request.session['user_id'] = user_login.login_id
            request.session['email'] = user_login.email
            request.session['name'] = user.name  # Fetch the user's name
            print(f"User found: {user.email}")
            print(f"Login ID: {user.login_id}")
            return redirect('/base_home/')  # Redirect to user dashboard
        except (Tbl_login.DoesNotExist, Tbl_user.DoesNotExist):
            messages.error(request, 'Invalid email or password')
            return redirect('/login/')

    return render(request, 'login.html')


def logout_view(request):
    # Clear the session to log the user out
    request.session.flush()  # This will remove all session data

    # Optionally, you can add a message to inform the user
    from django.contrib import messages
    messages.success(request, 'You have been logged out successfully.')

    # Redirect to the login page
    return redirect('/login/')

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
        # Fetch data from POST request
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        weight = request.POST.get('weight')
        metal_type = request.POST.get('metal_type')
        stone_type = request.POST.get('stone_type', '')  # Optional field
        gender = request.POST.get('gender')
        occasion = request.POST.get('occasion')
        delivery_options = request.POST.get('delivery_options', '')  # Optional field
        image = request.FILES.get('image')  # Single image upload

        # Basic validation
        if not all([product_name, product_description, category, price, stock_quantity, weight, metal_type, gender, occasion, image]):
            messages.error(request, 'Please fill in all required fields, including the image.')
            return render(request, 'admin/add_product.html')

        try:
            # Create the product object and save it to the database
            product = Product.objects.create(
                product_name=product_name,
                product_description=product_description,
                category=category,
                price=price,
                stock_quantity=stock_quantity,
                weight=weight,
                metal_type=metal_type,
                stone_type=stone_type,
                gender=gender,
                occasion=occasion,
                delivery_options=delivery_options,
                images=image  # Save the uploaded image
            )

            # Success message
            messages.success(request, 'Product has been added successfully!')
            return redirect('add_product')  # Redirect back to the form after successful submission

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return render(request, 'admin/add_product.html')

    # If it's a GET request, render the form
    return render(request, 'admin/add_product.html')

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
    product = get_object_or_404(Product, product_id=product_id)
    return render(request, 'admin/product_details.html', {'product': product})

# Delete a product
def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('view_products')
    return render(request, 'admin/view_products.html')

#update a product
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'update_product.html', {'form': form, 'product': product})

     #--------------------------------------------------------------------------------------#
def view_registered_users(request):
    users = Tbl_user.objects.all()  # Fetch all users
    return render(request, 'admin/view_registered_users.html', {'users': users})


def delete_user(request, user_id):
    user = get_object_or_404(Tbl_user, pk=user_id)
    
    if request.method == 'POST':  # Check if the form was submitted
        user.delete()
        return redirect('view_registered_users')  # Redirect back to the users list

    return render(request, 'confirm_delete_user.html', {'user': user})


 #---------------------------------------------------------------
from .forms import StaffForm

def add_staff(request):
    if request.method == 'POST':
        form = AddStaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin/view_staff')  # Redirect to a view after successful staff addition
    else:
        form = StaffForm()

    return render(request, 'admin/add_staff.html', {'form': form})


def view_staff(request):
    # Fetch all staff from the database
    staff_members = Tbl_staff.objects.all()
    # Pass the staff members to the template
    return render(request, 'admin/view_staff.html', {'staff_members': staff_members})




def update_staff(request, staff_id):
    staff = get_object_or_404(Tbl_staff, id=staff_id)

    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            # Update login details
            login = get_object_or_404(Tbl_login, id=staff.login.id)
            login.email = form.cleaned_data['email']
            login.save()

            # Update staff details
            staff.name = form.cleaned_data['name']
            staff.role = form.cleaned_data['role']
            staff.contact_details = form.cleaned_data['contact_details']
            staff.save()

            return redirect('view_staff')  # Redirect to the staff view page
    else:
        form = StaffForm(initial={
            'name': staff.name,
            'email': staff.login.email,
            'role': staff.role,
            'contact_details': staff.contact_details,
        })

    return render(request, 'admin/update_staff.html', {'form': form, 'staff': staff})


def delete_staff(request, staff_id):
    staff = get_object_or_404(Tbl_staff, id=staff_id)
    
    if request.method == 'POST':
        # Delete associated login details
        login = get_object_or_404(Tbl_login, id=staff.login.id)
        login.delete()  # Delete the login entry
        staff.delete()  # Delete the staff entry
        return redirect('view_staff')  # Redirect to the staff view page

    return render(request, 'confirm_delete.html', {'staff': staff})


#staff viws.py-------------------------------------------------------------------------------------------------

def staffhome(request):
    return render(request, 'staffhome.html')
