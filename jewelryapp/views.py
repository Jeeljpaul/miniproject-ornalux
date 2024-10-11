from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import PasswordResetRequestForm  # Import both forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

def index(request):
    return render(request, 'index.html')

def base(request):
    return render(request, 'base.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Tbl_login, Tbl_user
from django.core.exceptions import ValidationError
from django.db import transaction
import datetime

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Basic server-side validations
        errors = []

        # Name validation - only letters and spaces
        if not name.replace(" ", "").isalpha():
            errors.append("Name should only contain letters and spaces.")
        
        # Date of birth validation - age 18+
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        current_date = datetime.date.today()
        age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
        
        if age < 18:
            errors.append("You must be at least 18 years old.")
        elif dob_date >= current_date:
            errors.append("Please enter a valid date of birth.")

        # Phone number validation - 10 digits
        if not phone.isdigit() or len(phone) != 10:
            errors.append("Phone number must be exactly 10 digits.")
        
        # Email validation
        if Tbl_login.objects.filter(email=email).exists():
            errors.append("Email is already registered.")

        # Password validation
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password) or not any(char in '@$!%*#?&' for char in password):
            errors.append("Password must be at least 8 characters long, include a letter, a number, and a special character.")
        
        # Confirm password validation
        if password != confirm_password:
            errors.append("Passwords do not match.")

        # Check for errors
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html', {'form': request.POST})

        # If no errors, save user data
        try:
            with transaction.atomic():
                # Create login entry
                login = Tbl_login.objects.create(
                    email=email,
                    password=password,
                    status=True,
                    last_login=None,
                    login_count=0
                )

                # Create user entry
                Tbl_user.objects.create(
                    name=name,
                    dob=dob_date,
                    phone=phone,
                    login=login,
                    status=True
                )

                messages.success(request, "Account created successfully. Please login.")
                return redirect('login')  # Redirect to login page after successful registration

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'register.html', {'form': request.POST})

    else:
        return render(request, 'register.html')

    
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
                request.session['login_id'] = admin.login_id  # Store login_id in session
                request.session['email'] = admin.email
                request.session['name'] = 'Admin'  # Static name for admin
                   # Increment login count and update login timestamp
                admin.login()  # Call the method to update login info
                return redirect('/adminhome/')  # Redirect to admin home page
        except Tbl_login.DoesNotExist:
            pass
        
        # Check if the user is staff
        try:
            staff = Tbl_staff.objects.get(login_email=email, login_password=password)
            # Staff login success
            request.session['user_type'] = 'staff'
            request.session['login_id'] = staff.login.login_id  # Store login_id in session
            request.session['staff_id'] = staff.staff_id
            request.session['email'] = staff.login.email
            request.session['name'] = staff.name  # Fetch the staff's name

            # Increment login count and update login timestamp for staff
            staff.login.login()  # Increment login count for staff's login

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
            request.session['login_id'] = user_login.login_id  # Store login_id in session
            request.session['user_id'] = user.user_id  # User-specific ID
            request.session['email'] = user_login.email
            request.session['name'] = user.name  # Fetch the user's name
              # Increment login count and update login timestamp
            user_login.login()  # Call the method to update login info

            
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
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from django.shortcuts import render, redirect
from django.contrib import messages

@decorator_from_middleware(CacheMiddleware)
def adminhome(request):
    # Check if the user is logged in and is an admin
    if not request.session.get('user_type') == 'admin':
        # If not an admin, redirect to the login page
        messages.error(request, 'You need to log in as admin to access the admin dashboard.')
        # Redirect to login page
        response = redirect('/login/')
    else:
        # If admin, allow access to the admin dashboard
        response = render(request, 'admin/adminhome.html')

    # Set Cache-Control headers to prevent caching of the page
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response



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
def product_details(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    context = {'product': product}
    return render(request, 'admin/product_details.html', context)

def toggle_product_status(request, product_id):
    # Get the product object using product_id, or return 404 if not found
    product = get_object_or_404(Product, product_id=product_id)
    
    # Toggle the status field (assuming it's a BooleanField)
    product.status = not product.status  # If status is True, set it to False, and vice versa
    
    # Save the updated product object to the database
    product.save()
    
    # Redirect back to the product details page after toggling
    return redirect('product_details', product_id=product_id)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product
from .forms import ProductForm  # Assuming you have a form class for the product

def update_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')  # Redirect to product list or detail page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/update_product.html', {'form': form, 'product': product})


# Delete a product
def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('view_products')
    return render(request, 'admin/view_products.html')

#update a product
# def update_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect('product_detail', product_id=product.id)
#     else:
#         form = ProductForm(instance=product)

#     return render(request, 'update_product.html', {'form': form, 'product': product})

     #--------------------------------------------------------------------------------------#
def view_registered_users(request):
    users = Tbl_user.objects.all()  # Fetch all users
    return render(request, 'admin/view_registered_users.html', {'users': users})


from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Tbl_user, Tbl_login

def toggle_user_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(Tbl_user, user_id=user_id)
        action = request.POST.get('action')

        if action == 'deactivate':
            user.status = False
            user.login.status = False
        elif action == 'activate':
            user.status = True
            user.login.status = True

        user.login.save()
        user.save()

    return redirect(reverse('view_registered_users'))

 #---------------------------------------------------------------
from .forms import StaffForm

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/adminhome/')  # Redirect to a view after successful staff addition
    else:
        form = StaffForm()

    return render(request, 'admin/add_staff.html', {'form': form})


def view_staff(request):
    # Fetch all staff from the database
    staff_members = Tbl_staff.objects.all()
    # Pass the staff members to the template
    return render(request, 'admin/view_staff.html', {'staff_members': staff_members})




def update_staff(request, staff_id):
    staff = get_object_or_404(Tbl_staff, staff_id=staff_id)

    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            # Update login details
            login = get_object_or_404(Tbl_login, login_id=staff.login.login_id)
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

def staffhome(request):
    return render(request, 'staffhome.html')

#staff views.py-------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm
 
def add_p(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Ensure 'product_list' is defined in your URLs
    else:
        form = ProductForm()
    categories = Category.objects.all() 
    return render(request, 'admin/add_p.html', {'form': form, 'categories': categories})



def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Ensure 'product_list' is defined in your URLs
    else:
        form = ProductForm()
    return render(request, 'admin/add_product.html', {'form': form})



from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'admin/product_list.html', {'products': products})



from django.shortcuts import get_object_or_404

def update_p(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Make sure 'product_list' is defined in your URLs
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/update_p.html', {'form': form, 'product': product})


# -----------------------------------------------------------------------------------------------------

def product(request):
    return render(request, 'user/product.html')



def ring_list(request):
    # Fetch all products with the category 'Rings'
    rings = Product.objects.filter(category='Ring', is_active=True)

    # Get filter criteria from the request
    ring_size = request.GET.get('ring_size')
    ring_type = request.GET.get('ring_type')
    stone_type = request.GET.get('stone_type')
    metal_type = request.GET.get('metal_type')

    # Apply filters if they are present
    if ring_size:
        rings = rings.filter(size=ring_size)
    if ring_type:
        rings = rings.filter(ring_type=ring_type)
    if stone_type:
        rings = rings.filter(gemstone=stone_type)
    if metal_type:
        rings = rings.filter(metal_type=metal_type)


    return render(request, 'user/ring_list.html', {'rings': rings})


def earring_list(request):
    # Fetch all products with the category 'Earrings'
    earrings = Product.objects.filter(category='Earring', is_active=True)

    # Get filter criteria from the request
    earring_style = request.GET.get('earring_style')
    shop_for = request.GET.get('shop_for')
    stone_type = request.GET.get('stone_type')
    metal_type = request.GET.get('metal_type')

    # Apply filters if they are present
    if earring_style:
        earrings = earrings.filter(earring_style__iexact=earring_style)
    if shop_for:
        earrings = earrings.filter(shop_for__iexact=shop_for)
    if stone_type:
        earrings = earrings.filter(stone_type__iexact=stone_type)
    if metal_type:
        earrings = earrings.filter(metal_type__iexact=metal_type)

    return render(request, 'user/earring_list.html', {'earrings': earrings})



def bracelet_list(request):
    # Fetch all products with the category 'Bracelet'
    bracelets = Product.objects.filter(category='Bracelet', is_active=True)

    # Get filter criteria from the request
    bracelet_style = request.GET.get('bracelet_style')
    shop_for = request.GET.get('shop_for')
    stone_type = request.GET.get('stone_type')
    metal_type = request.GET.get('metal_type')

    # Apply filters if they are present
    if bracelet_style:
        bracelets = bracelets.filter(bracelet_style__iexact=bracelet_style)
    if shop_for:
        bracelets = bracelets.filter(shop_for__iexact=shop_for)
    if stone_type:
        bracelets = bracelets.filter(stone_type__iexact=stone_type)
    if metal_type:
        bracelets = bracelets.filter(metal_type__iexact=metal_type)

    return render(request, 'user/bracelet.html', {'bracelets': bracelets})

from django.shortcuts import render, get_object_or_404

def ring_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id, category='Ring')
    return render(request, 'user/ring_detail.html', {'product': product})



from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cart, Product, Tbl_login

def add_to_cart(request, product_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'You need to register or log in to add items to the cart.'})
    
    # If the user is authenticated, proceed to add the product to the cart
    product = get_object_or_404(Product, id=product_id)
    user_login = request.user.tbl_login  # Assuming you have a way to link the user to Tbl_login
    cart, created = Cart.objects.get_or_create(login=user_login)

    if product not in cart.products.all():
        cart.products.add(product)

    cart.save()
    return redirect('ring_detail')


from django.shortcuts import render, redirect
from .models import Category, CategoryAttribute

def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        attribute_names = request.POST.getlist('attribute_names')

        # Create a new category
        category = Category.objects.create(name=category_name)

        # Add attributes to the category
        for attribute_name in attribute_names:
            if attribute_name.strip():  # Ensure it's not empty
                CategoryAttribute.objects.create(category=category, name=attribute_name)

        return redirect('add_category')  # Redirect to the same page after saving

    return render(request, 'admin/add_category.html')

from django.http import JsonResponse
from .models import CategoryAttribute
from django.http import JsonResponse
from .models import Category, CategoryAttribute

def get_category_attributes(request, category_id):
    print("hello")
    try:
        # Get the category by its ID
        category = Category.objects.get(category_id=category_id)

        # Retrieve attributes associated with this category
        attributes = CategoryAttribute.objects.filter(category=category)

        # Prepare the response data in the expected format
        response_data = {
            'attributes': [{'name': attribute.name} for attribute in attributes]
        }

        return JsonResponse(response_data, safe=False)
    except Category.DoesNotExist:
        # If the category doesn't exist, return an empty list with a 404 status code
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        # Handle other errors
        return JsonResponse({'error': str(e)}, status=500)
    
from django.shortcuts import render, redirect
from .models import Metaltype
from django.http import HttpResponse

def add_metaltype(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Metaltype.objects.create(name=name)
            return redirect('add_metaltype')  # Redirect after successful creation
        else:
            return HttpResponse("Name field cannot be empty.")

    return render(request, 'admin/add_metaltype.html')

    
from django.shortcuts import render, redirect
from .models import Metaltype
from django.http import HttpResponse

def add_stonetype(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Stonetype.objects.create(name=name)
            return redirect('add_stonetype')  # Redirect after successful creation
        else:
            return HttpResponse("Name field cannot be empty.")

    return render(request, 'admin/add_stonetype.html')

