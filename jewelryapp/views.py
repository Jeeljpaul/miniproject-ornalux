from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import PasswordResetRequestForm  # Import both forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

def index(request):
    return render(request, 'index.html', {'user': request.user})

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
        print("Login POST request received")
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Server-side email validation
        try:
            validate_email(email)
        except ValidationError:
            print("Invalid email format")  # Debug print
            messages.error(request, 'Please enter a valid email address')
            return redirect('/login/')
        
        # Server-side password validation
        if len(password) < 8:
            print("Password validation failed") 
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
            staff_login = Tbl_login.objects.get(email=email, password=password)
            staff = Tbl_staff.objects.get(login_id=staff_login.login_id)
            # Staff login success
            request.session['user_type'] = 'staff'
            request.session['login_id'] = staff_login.login_id  # Store login_id in session
            request.session['staff_id'] = staff.staff_id
            request.session['email'] = staff_login.email
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
            request.session.save()  # Explicitly save the session to ensure it is stored
            print("User session data:", dict(request.session)) 
            user_login.login()
            print("User logged in:", request.session)   # Call the method to update login info

            
            return redirect('/')  # Redirect to user dashboard
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


from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Product  # Adjust the import based on your app structure

def toggle_product_status(request, product_id):
    if request.method == 'POST':
        # Get the product object using product_id, or return 404 if not found
        product = get_object_or_404(Product, product_id=product_id)
        
        # Get the action from the request to determine if we should activate or deactivate
        action = request.POST.get('action')

        if action == 'deactivate':
            product.is_active = False
        elif action == 'activate':
            product.is_active = True

        # Save the updated product object to the database
        product.save()

    # Redirect to the product list or any appropriate view after toggling
    return redirect(reverse('product_list'))


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Product
# from .forms import ProductForm 

# def update_product(request, product_id):
#     product = get_object_or_404(Product, product_id=product_id)

#     if request.method == "POST":
#         form = ProductForm(request.POST, instance=product)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Product updated successfully!')
#             return redirect('product_list') 
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = ProductForm(instance=product)

#     return render(request, 'admin/update_product.html', {'form': form, 'product': product})




# def delete_product(request, product_id):
#     product = get_object_or_404(Product, product_id=product_id)
#     if request.method == 'POST':
#         product.delete()
#         return redirect('view_products')
#     return render(request, 'admin/view_products.html')



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



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
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
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Tbl_login, Tbl_staff
from .forms import StaffForm

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()

            # After saving the staff details, send an email with the login credentials
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']

            subject = 'Your Staff Account Details'
            message = f'Hello {name},\n\nYou have been added as a staff member.\n\nYour login details are:\nEmail: {email}\nPassword: {password}\n\nPlease login and change your password.\n\nBest regards,\nAdmin Team'

            # Send the email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

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

# from django.shortcuts import render, redirect
# from .models import Product
# from .forms import ProductForm
 
# def add_p(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')  
#     else:
#         form = ProductForm()
#     categories = Category.objects.all() 
#     return render(request, 'admin/add_p.html', {'form': form, 'categories': categories})



# def add_product(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')  
#     else:
#         form = ProductForm()
#     return render(request, 'admin/add_product.html', {'form': form})



from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'admin/product_list.html', {'products': products})



# from django.shortcuts import get_object_or_404

# def update_p(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
    
#     if request.method == "POST":
#         form = ProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')  
#     else:
#         form = ProductForm(instance=product)

#     return render(request, 'admin/update_p.html', {'form': form, 'product': product})


# -----------------------------------------------------------------------------------------------------

#userpage

def product(request): 
    return render(request, 'user/product.html')


from django.shortcuts import render
from .models import Product, Stonetype, Metaltype, ProductAttribute, Category

def ring_lists(request):
    # Get all possible filter values from the database
    ring_sizes = ProductAttribute.objects.filter(attribute_name='Ringsize').values_list('attribute_value', flat=True).distinct()
    ring_types = ProductAttribute.objects.filter(attribute_name='Ringtype').values_list('attribute_value', flat=True).distinct()
    gemstones = Stonetype.objects.all()
    materials = Metaltype.objects.all()

    # Retrieve selected filters from the request
    selected_ring_sizes = request.GET.getlist('ring_size')
    selected_ring_types = request.GET.getlist('ring_type')
    selected_gemstones = request.GET.getlist('gemstone')
    selected_materials = request.GET.getlist('metal_type')

    # Initialize the queryset to fetch all ring products initially
    category_ring = Category.objects.get(name='Ring')
    rings = Product.objects.filter(category=category_ring, is_active=True)

    # Apply filtering based on selected values
    if selected_ring_sizes:
        rings = rings.filter(attributes__attribute_name='Ringsize', attributes__attribute_value__in=selected_ring_sizes)
    if selected_ring_types:
        rings = rings.filter(attributes__attribute_name='Ringtype', attributes__attribute_value__in=selected_ring_types)
    if selected_gemstones:
        rings = rings.filter(stonetype__name__in=selected_gemstones)
    if selected_materials:
        rings = rings.filter(metaltype__name__in=selected_materials)

    context = {
        'rings': rings,
        'ring_sizes': ring_sizes,
        'ring_types': ring_types,
        'gemstones': gemstones,
        'materials': materials,
        'selected_ring_sizes': selected_ring_sizes,
        'selected_ring_types': selected_ring_types,
        'selected_gemstones': selected_gemstones,
        'selected_materials': selected_materials,
    }

    return render(request, 'user/ring_list.html', context)







from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAttribute, Metaltype, Stonetype, Category

def ring_detail(request, product_id):
    # Get the specific product by its ID, along with related Metaltype, Stonetype, and Category
    product = get_object_or_404(Product.objects.select_related('metaltype', 'stonetype', 'category'), product_id=product_id)
  

    # Fetch the product's attributes (e.g., ring size, ring type, etc.)
    product_attributes = ProductAttribute.objects.filter(product=product)

    # Fetch the category attributes for the specific product category (if any)
    category_attributes = product.category.attributes.all() if product.category else []

    context = {
        'product': product,
        'product_attributes': product_attributes,
        'category_attributes': category_attributes,
        'metaltype': product.metaltype,
        'stonetype': product.stonetype,
    }

    return render(request, 'user/ring_detail.html', context)



from django.shortcuts import render
from .models import Product, Stonetype, Metaltype, ProductAttribute

def earring_list(request):
    # Get all possible filter values from the database
    gemstones = Stonetype.objects.all()
    materials = Metaltype.objects.all()
    earring_styles = ProductAttribute.objects.filter(attribute_name='Earring Style').values_list('attribute_value', flat=True).distinct()
    shop_for_options = Product.objects.values_list('gender', flat=True).distinct()

    # Retrieve selected filters from the request
    selected_gemstones = request.GET.getlist('gemstone')
    selected_materials = request.GET.getlist('metal_type')
    selected_earring_styles = request.GET.getlist('earringstyle')
    selected_shop_for = request.GET.getlist('shop_for')

    # Initialize the queryset to fetch all products initially
    category_earring = Category.objects.get(name='Earring')
    earrings = Product.objects.filter(category=category_earring, is_active=True)


    # Apply filtering based on selected values
    if selected_shop_for:
        earrings = earrings.filter(gender__in=selected_shop_for)
    if selected_gemstones:
        earrings = earrings.filter(stonetype__name__in=selected_gemstones)
    if selected_materials:
        earrings = earrings.filter(metaltype__name__in=selected_materials)
    if selected_earring_styles:
        earrings = earrings.filter(attributes_attribute_name='Earring Style', attributes__attribute_value__in=selected_earring_styles)

    context = {
        'earrings': earrings,
        'gemstones': gemstones,
        'materials': materials,
        'earring_styles': earring_styles,
        'shop_for_options': shop_for_options,
        'selected_gemstones': selected_gemstones,
        'selected_materials': selected_materials,
        'selected_earring_styles': selected_earring_styles,
        'selected_shop_for': selected_shop_for,
    }

    return render(request, 'user/earring_list.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAttribute, Metaltype, Stonetype, Category

def earring_detail(request, product_id):
    # Get the specific product by its ID, along with related Metaltype, Stonetype, and Category
    product = get_object_or_404(Product.objects.select_related('metaltype', 'stonetype', 'category'), product_id=product_id)
  

    # Fetch the product's attributes (e.g., ring size, ring type, etc.)
    product_attributes = ProductAttribute.objects.filter(product=product)

    # Fetch the category attributes for the specific product category (if any)
    category_attributes = product.category.attributes.all() if product.category else []

    context = {
        'product': product,
        'product_attributes': product_attributes,
        'category_attributes': category_attributes,
        'metaltype': product.metaltype,
        'stonetype': product.stonetype,
    }

    return render(request, 'user/earring_detail.html', context)


from django.shortcuts import render
from .models import Product, Stonetype, Metaltype, ProductAttribute, Category

def bracelet_lists(request):
    # Get all possible filter values from the database
    bracelet_styles = ProductAttribute.objects.filter(attribute_name='Bracelet Style').values_list('attribute_value', flat=True).distinct()
    gemstones = Stonetype.objects.all()
    materials = Metaltype.objects.all()
    shop_for_options = Product.objects.values_list('gender', flat=True).distinct()

    # Retrieve selected filters from the request
    selected_styles = request.GET.getlist('bracelet_style')
    selected_shop_for = request.GET.getlist('shop_for')
    selected_gemstones = request.GET.getlist('gemstone')
    selected_materials = request.GET.getlist('metal_type')

    # Initialize the queryset to fetch all bracelet products initially
    category_bracelet = Category.objects.get(name='Bracelets')
    bracelets = Product.objects.filter(category=category_bracelet, is_active=True)

    # Apply filtering based on selected values
    if selected_styles:
        bracelets = bracelets.filter(attributes__attribute_name='Bracelet Style', attributes__attribute_value__in=selected_styles)
    if selected_shop_for:
        bracelets = bracelets.filter(gender__in=selected_shop_for)
    if selected_gemstones:
        bracelets = bracelets.filter(stonetype__name__in=selected_gemstones)
    if selected_materials:
        bracelets = bracelets.filter(metaltype__name__in=selected_materials)

    context = {
        'bracelets': bracelets,
        'bracelet_styles': bracelet_styles,
        'shop_for_options': shop_for_options,
        'gemstones': gemstones,
        'materials': materials,
        'selected_styles': selected_styles,
        'selected_shop_for': selected_shop_for,
        'selected_gemstones': selected_gemstones,
        'selected_materials': selected_materials,
    }

    return render(request, 'user/bracelet.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAttribute, Metaltype, Stonetype, Category

def bracelet_detail(request, product_id):
    # Get the specific product by its ID, along with related Metaltype, Stonetype, and Category
    product = get_object_or_404(Product.objects.select_related('metaltype', 'stonetype', 'category'), product_id=product_id)
  

    # Fetch the product's attributes (e.g., ring size, ring type, etc.)
    product_attributes = ProductAttribute.objects.filter(product=product)

    # Fetch the category attributes for the specific product category (if any)
    category_attributes = product.category.attributes.all() if product.category else []

    context = {
        'product': product,
        'product_attributes': product_attributes,
        'category_attributes': category_attributes,
        'metaltype': product.metaltype,
        'stonetype': product.stonetype,
    }

    return render(request, 'user/bracelet_details.html', context)

#----------------------------------------------------------------------------------------------------------------------------------------------

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Cart, CartItem
from .models import Tbl_user

def add_to_cart(request, product_id):
    if 'login_id' in request.session:
        product = get_object_or_404(Product, product_id=product_id)
        user_id = request.session['login_id']
        print(user_id)
        if request.method == 'POST':
            # Check if the user is authenticated
            # if request.user.is_authenticated:
                # user = get_object_or_404(Tbl_user, user_id=user_id)
                # print(user)
                user_cart, created = Cart.objects.get_or_create(login=user_id)
                print("kk")
                # Check if the cart item already exists
                cart_item, item_created = CartItem.objects.get_or_create(cart=user_cart, product=product)

                if not item_created:
                    # If the item is already in the cart, increase the quantity
                    cart_item.quantity += 1
                    cart_item.save()

                return JsonResponse({'success': True, 'message': f'{product.product_name} added to cart successfully!'})
            
            # else:
            #     # Handle cart for non-authenticated users using session
            #     cart = request.session.get('cart', {})

            #     # Check if the product is already in the cart
            #     if str(product_id) in cart:
            #         cart[str(product_id)]['quantity'] += 1
            #     else:
            #         cart[str(product_id)] = {
            #             'product_id': product_id,
            #             'product_name': product.product_name,
            #             'quantity': 1,
            #             'price': str(product.price)  # Convert to string for session compatibility
            #         }

            #     # Save the updated cart in the session
            #     request.session['cart'] = cart
            #     return JsonResponse({'success': True, 'message': f'{product.product_name} added to session cart successfully!'})

        return JsonResponse({'success': False, 'message': 'Invalid request.'})
    else:
        return redirect('login')

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Cart, CartItem, Product

def view_cart(request):
    # Check if the user is logged in
    if 'login_id' not in request.session:
        return redirect('login')  # Redirect to login page if the user is not logged in

    user_id = request.session['login_id']

    # Fetch the user's cart using the login_id stored in the session
    try:
        user_cart = Cart.objects.get(login=user_id)
        cart_items = CartItem.objects.filter(cart=user_cart).select_related('product')
    except Cart.DoesNotExist:
        # If the cart does not exist, initialize an empty list for cart items
        cart_items = []

    # Calculate the total price of all items in the cart
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'user/view_cart.html', context)


def update_cart_quantity(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        change = int(request.POST.get('change'))

        try:
            user_id = request.session['login_id']
            user_cart = Cart.objects.get(login=user_id)
            cart_item = CartItem.objects.get(cart=user_cart, product_id=product_id)

            # Update the quantity
            cart_item.quantity += change
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()

            # Calculate the updated total price for the cart item and the cart
            item_total_price = cart_item.product.price * cart_item.quantity
            total_price = sum(item.product.price * item.quantity for item in CartItem.objects.filter(cart=user_cart))

            return JsonResponse({
                'new_quantity': cart_item.quantity,
                'item_total_price': item_total_price,
                'new_total_price': total_price,
            })

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Cart or CartItem not found.'}, status=404)

    return JsonResponse({'error': 'Invalid request.'}, status=400)



def remove_item_from_cart(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')

        try:
            user_id = request.session['login_id']
            user_cart = Cart.objects.get(login=user_id)
            cart_item = CartItem.objects.get(cart=user_cart, product_id=product_id)

            # Remove the item from the cart
            cart_item.delete()

            # Recalculate the total price of the cart
            total_price = sum(item.product.price * item.quantity for item in CartItem.objects.filter(cart=user_cart))

            return JsonResponse({
                'new_total_price': total_price,
            })

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'error': 'Cart or CartItem not found.'}, status=404)

    return JsonResponse({'error': 'Invalid request.'}, status=400)


from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Wishlist, WishlistItem, Tbl_user

def add_to_wishlist(request, product_id):
    if 'login_id' in request.session:
        product = get_object_or_404(Product, product_id=product_id)
        user_id = request.session['login_id']

        user_instance = get_object_or_404(Tbl_login, login_id=user_id)
        
        if request.method == 'POST':
            # Get or create a wishlist for the user
            user_wishlist, created = Wishlist.objects.get_or_create(login=user_instance)
            # Check if the product is already in the wishlist
            wishlist_item, item_created = WishlistItem.objects.get_or_create(wishlist=user_wishlist, product=product)
            if not item_created:
                return JsonResponse({'success': False, 'message': f'{product.product_name} is already in your wishlist!'})

            return JsonResponse({'success': True, 'message': f'{product.product_name} added to your wishlist successfully!'})

        return JsonResponse({'success': False, 'message': 'Invalid request.'})
    else:
        return redirect('login')

def view_wishlist(request):
    if 'login_id' in request.session:
        user_id = request.session['login_id']
        user_instance = get_object_or_404(Tbl_login, login_id=user_id)

        # Get the user's wishlist
        user_wishlist = Wishlist.objects.filter(login=user_instance).first()
        wishlist_items = WishlistItem.objects.filter(wishlist=user_wishlist) if user_wishlist else []

        return render(request, 'user/wishlist.html', {'wishlist_items': wishlist_items})
    else:
        return redirect('login')

def remove_from_wishlist(request, item_id):
    if 'login_id' in request.session:
        wishlist_item = get_object_or_404(WishlistItem, id=item_id)
        wishlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Item removed from your wishlist.'})
    else:
        return JsonResponse({'success': False, 'message': 'You need to be logged in to perform this action.'})


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#adminpage
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Category, CategoryAttribute

# def add_category(request):
#     if request.method == 'POST':
#         category_name = request.POST.get('category_name')
#         attribute_names = request.POST.getlist('attribute_names')
#         attribute_datatypes = request.POST.getlist('attribute_datatypes')

#         existing_category_id = request.POST.get('existing_category')

#         if existing_category_id:
#             category = get_object_or_404(Category, id=existing_category_id)
#         elif category_name:
            
#             category = Category.objects.create(name=category_name)

#         if attribute_names and attribute_datatypes:
           
#             for name, datatype in zip(attribute_names, attribute_datatypes):
#                 if name:  
#                     CategoryAttribute.objects.create(category=category, name=name, datatype=datatype)

#         return redirect('add_category')  

    
#     categories = Category.objects.all()

#     context = {
#         'categories': categories
#     }
#     return render(request, 'admin/add_category.html', context)
from django.shortcuts import render, redirect
from .models import Category

def add_category(request):
    error_message = None

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        
        if not category_name:
            error_message = "Category name cannot be empty."
        elif Category.objects.filter(name__iexact=category_name).exists():
            error_message = "This category already exists in the database."
        else:
            # Create a new Category if it doesn't already exist
            Category.objects.create(name=category_name)
            return redirect('view_categories')  # Redirect after successful creation

    return render(request, 'admin/add_category.html', {'error_message': error_message})



def view_categories(request):
    categories = Category.objects.all().prefetch_related('attributes')
    return render(request, 'admin/view_categories.html', {'categories': categories})


def add_attribute_to_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        attribute_name = request.POST.get('attribute_name')

        if attribute_name:
            # Add the new attribute to the existing category
            CategoryAttribute.objects.create(category=category, name=attribute_name)
            return redirect('view_categories')  # Redirect to category list after adding attribute

    return render(request, 'admin/add_attribute.html', {'category': category})



#-----------------------------------------------------------------------------------------------------------------------------------------

  
# from django.shortcuts import render, redirect
# from .models import Metaltype
# from django.http import HttpResponse

# def add_metaltype(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         if name:
#             Metaltype.objects.create(name=name)
#             return redirect('add_metaltype') 
#         else:
#             return HttpResponse("Name field cannot be empty.")

#     return render(request, 'admin/add_metaltype.html')

# views.py
from django.shortcuts import render
from .models import Metaltype

def view_metaltypes(request):
    metaltypes = Metaltype.objects.all()
    return render(request, 'admin/view_metaltype.html', {'metaltypes': metaltypes})


from django.shortcuts import render, redirect
from .models import Metaltype

def add_metaltype(request):
    error_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        
        if not name:
            error_message = "Name field cannot be empty."
        elif Metaltype.objects.filter(name__iexact=name).exists():
            error_message = "This metal type already exists in the database."
        else:
            Metaltype.objects.create(name=name)
            return redirect('view_metaltypes')  # Redirect after successful creation

    # Fetch all metal types to display in the template
    # metaltypes = Metaltype.objects.all()

    return render(request, 'admin/add_metaltype.html', {'error_message': error_message})






#-----------------------------------------------------------------------------------------------------------------


# views.py
from django.shortcuts import render
from .models import Stonetype

def view_stonetypes(request):
    stonetypes = Stonetype.objects.all()
    return render(request, 'admin/view_stonetypes.html', {'stonetypes': stonetypes})




from django.shortcuts import render, redirect
from .models import Stonetype

def add_stonetype(request):
    error_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        
        if not name:
            error_message = "Name field cannot be empty."
        elif Stonetype.objects.filter(name__iexact=name).exists():
            error_message = "This stone type already exists in the database."
        else:
            Stonetype.objects.create(name=name)
            return redirect('view_stonetypes')  # Redirect after successful creation

    return render(request, 'admin/add_stonetype.html', {'error_message': error_message})



# from django.shortcuts import render, redirect
# from .models import Metaltype
# from django.http import HttpResponse

# def add_stonetype(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         if name:
#             Stonetype.objects.create(name=name)
#             return redirect('add_stonetype')  
#         else:
#             return HttpResponse("Name field cannot be empty.")

#     return render(request, 'admin/add_stonetype.html')




#--------------------------------------------------------------------------------------------------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Category, Metaltype, Stonetype, ProductAttribute, CategoryAttribute

def add_pro(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('id_category')
        product_description = request.POST.get('product_description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        weight = request.POST.get('weight')
        metaltype_id = request.POST.get('metaltype', None)
        stonetype_id = request.POST.get('stonetype', None)
        gender = request.POST.get('gender','Unisex')
        image = request.FILES.get('image') 

        # Handling delivery options (checkboxes)
        delivery_options = request.POST.getlist('delivery_options[]')
        home_delivery = 'Home Delivery' in delivery_options
        store_pickup = 'Store Pickup' in delivery_options
        try_at_home = 'Try at home' in delivery_options
        
        # Handling bestselling checkbox
        bestseller = request.POST.get('bestselling', 'off') == 'Yes'  # Checkbox for bestselling item

        # Validate the inputs
        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
            weight = float(weight)
        except ValueError:
            messages.error(request, "Invalid input values.")
            return redirect('add_pro')

        if not (100 <= price <= 10000000):
            messages.error(request, "Price must be between 100 and 10,000,000.")
            return redirect('add_pro')

        if not (0 <= stock_quantity <= 50):
            messages.error(request, "Stock quantity must be between 0 and 50.")
            return redirect('add_pro')

        if not (1 <= weight <= 100):
            messages.error(request, "Weight must be between 1 and 100 grams.")
            return redirect('add_pro')

        # Check if the product already exists
        try:
            category = Category.objects.get(category_id=category_id)  # Ensure category is fetched correctly
            if Product.objects.filter(product_name=product_name, category=category).exists():
                messages.error(request, "Product with this name already exists in the selected category.")
                return redirect('add_pro')
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist.")
            return redirect('add_pro')

        # Create the product instance and save it
        try:
            metaltype = Metaltype.objects.get(metaltype_id=metaltype_id) if metaltype_id else None
            stonetype = Stonetype.objects.get(stonetype_id=stonetype_id) if stonetype_id else None
            
            product = Product(
                product_name=product_name,
                category=category,
                product_description=product_description,
                price=price,
                stock_quantity=stock_quantity,
                weight=weight,
                gender=gender,
                images=image,
                metaltype=metaltype,
                stonetype=stonetype,
                home_delivery=home_delivery,
                store_pickup=store_pickup,
                try_at_home=try_at_home,
                bestselling=bestseller
            )
            product.save()
            messages.success(request, "Product added successfully!")

            # Now handle product attributes
            attributes_data = request.POST.getlist('attributes')
            for attribute_id in attributes_data:
                if attribute_id:  # Only proceed if the ID is not empty
                    try:
                        # Debug print statement to check the attribute ID being processed
                        print(f"Processing attribute ID: {attribute_id}")

                        # Fetch the attribute name from CategoryAttribute using the attribute_id
                        category_attribute = CategoryAttribute.objects.get(id=attribute_id)
                        attribute_name = category_attribute.name

                        # Fetch the attribute value from the form using the attribute ID
                        attribute_value = request.POST.get(f'attribute_{attribute_id}', '')
                        print(f"Processing attribute {attribute_name} with value: {attribute_value}")


                        # Check if attribute value is provided
                        if attribute_value:
                            # Create a ProductAttribute object with the product, attribute name, and value
                            ProductAttribute.objects.create(
                                product=product,
                                attribute_name=attribute_name,
                                attribute_value=attribute_value
                            )
                        else:
                            messages.warning(request, f"Attribute value for {attribute_name} is missing. Skipping.")
                    except CategoryAttribute.DoesNotExist:
                        messages.error(request, f"Attribute with ID {attribute_id} does not exist.")
                    except Exception as e:
                        messages.error(request, f"Error saving attribute: {str(e)}")

            return redirect('add_pro')  # Redirect after success

        except (Metaltype.DoesNotExist, Stonetype.DoesNotExist) as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('add_pro')

    # GET request to render the page
    categories = Category.objects.all()
    metaltypes = Metaltype.objects.all()
    stonetypes = Stonetype.objects.all()
    context = {
        'categories': categories,
        'metaltypes': metaltypes,
        'stonetypes': stonetypes,
    }
    return render(request, 'admin/add_p.html', context)


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Product, Category, Metaltype, Stonetype, CategoryAttribute, ProductAttribute

def update_pro(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('id_category')
        product_description = request.POST.get('product_description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        weight = request.POST.get('weight')
        metaltype_id = request.POST.get('metaltype', None)
        stonetype_id = request.POST.get('stonetype', None)
        gender = request.POST.get('gender', 'Unisex')
        image = request.FILES.get('image', product.images)  # Keep existing image if not changed


        # Handling delivery options (checkboxes)
        delivery_options = request.POST.getlist('delivery_options[]')
        home_delivery = 'Home Delivery' in delivery_options
        store_pickup = 'Store Pickup' in delivery_options
        try_at_home = 'Try at home' in delivery_options

        # Handling bestselling checkbox
        bestseller = request.POST.get('bestselling', 'off') == 'Yes'

        # Validate the inputs
        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
            weight = float(weight)
        except ValueError:
            messages.error(request, "Invalid input values.")
            return redirect('update_pro', product_id=product.product_id)

        if not (100 <= price <= 10000000):
            messages.error(request, "Price must be between 100 and 10,000,000.")
            return redirect('update_pro', product_id=product.product_id)

        if not (0 <= stock_quantity <= 50):
            messages.error(request, "Stock quantity must be between 0 and 50.")
            return redirect('update_pro', product_id=product.product_id)

        if not (1 <= weight <= 100):
            messages.error(request, "Weight must be between 1 and 100 grams.")
            return redirect('update_pro', product_id=product.product_id)

        try:
            category = Category.objects.get(category_id=category_id)
            metaltype = Metaltype.objects.get(metaltype_id=metaltype_id) if metaltype_id else None
            stonetype = Stonetype.objects.get(stonetype_id=stonetype_id) if stonetype_id else None

            # Update the product instance with new details
            product.product_name = product_name
            product.category = category
            product.product_description = product_description
            product.price = price
            product.stock_quantity = stock_quantity
            product.weight = weight
            product.gender = gender
            product.images = image
            product.metaltype = metaltype
            product.stonetype = stonetype
            product.home_delivery = home_delivery
            product.store_pickup = store_pickup
            product.try_at_home = try_at_home
            product.bestselling = bestseller

            product.save()
            messages.success(request, "Product updated successfully!")

            # Handle product attributes
            attributes_data = request.POST.getlist('attributes')
            for attribute_id in attributes_data:
                if attribute_id:
                    try:
                        category_attribute = CategoryAttribute.objects.get(id=attribute_id)
                        attribute_name = category_attribute.name
                        attribute_value = request.POST.get(f'attribute_{attribute_id}', '')

                        # Update or create the product attribute
                        if attribute_value:
                            product_attribute, created = ProductAttribute.objects.update_or_create(
                                product=product,
                                attribute_name=attribute_name,
                                defaults={'attribute_value': attribute_value}
                            )
                    except CategoryAttribute.DoesNotExist:
                        messages.error(request, f"Attribute with ID {attribute_id} does not exist.")
                    except Exception as e:
                        messages.error(request, f"Error updating attribute: {str(e)}")

            return redirect('product_list')

        except (Category.DoesNotExist, Metaltype.DoesNotExist, Stonetype.DoesNotExist) as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('update_pro', product_id=product.product_id)

    # GET request to render the page with existing product details
    categories = Category.objects.all()
    metaltypes = Metaltype.objects.all()
    stonetypes = Stonetype.objects.all()
    product_attributes = ProductAttribute.objects.filter(product=product)

    context = {
        'product': product,
        'categories': categories,
        'metaltypes': metaltypes,
        'stonetypes': stonetypes,
        'product_attributes': product_attributes,
    }
    return render(request, 'admin/update_p.html', context)



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
            'attributes': [{'id': attribute.id, 'name': attribute.name} for attribute in attributes]
        }

        return JsonResponse(response_data, safe=False)
    except Category.DoesNotExist:
        # If the category doesn't exist, return an empty list with a 404 status code
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        # Handle other errors
        return JsonResponse({'error': str(e)}, status=500)



from django.shortcuts import render
from .models import Product, Category, Metaltype, Stonetype

def product_list(request):
    # Get all possible filter values from the database
    products = Product.objects.all()
    categories = Category.objects.all()

    # Retrieve selected filters from the request
    selected_categories = request.GET.getlist('category')
    selected_price = request.GET.get('price')
    selected_weight = request.GET.get('weight')

    # Apply filtering based on selected categories
    if selected_categories and any(selected_categories):
        products = products.filter(category___in=selected_categories)
    # Apply exact price filtering if specified
    if selected_price:
        products = products.filter(price=selected_price)

    # Apply exact weight filtering if specified
    if selected_weight:
        products = products.filter(weight=selected_weight)

    context = {
        'products': products,
        'categories': categories,
        'selected_categories': selected_categories,
        'selected_price': selected_price,
        'selected_weight': selected_weight,
    }

    return render(request, 'admin/product_list.html', context)


# def all_products(request):
#     categories = Category.objects.all()
#     materials = Metaltype.objects.all()
#     gemstones = Stonetype.objects.all()
#     ring_sizes = ProductAttribute.objects.filter(attribute_name='Ringsize').values_list('attribute_value', flat=True).distinct()
#     ring_types = ProductAttribute.objects.filter(attribute_name='Ringtype').values_list('attribute_value', flat=True).distinct()
#     earring_styles = ProductAttribute.objects.filter(attribute_name='Earring Style').values_list('attribute_value', flat=True).distinct()
#     shop_for_options = Product.objects.values_list('gender', flat=True).distinct()
#     bracelet_styles = ProductAttribute.objects.filter(attribute_name='Bracelet Style').values_list('attribute_value', flat=True).distinct()


#     selected_ring_sizes = request.GET.getlist('ring_size')
#     selected_ring_types = request.GET.getlist('ring_type')
#     selected_earring_styles = request.GET.getlist('earringstyle')
#     selected_shop_for = request.GET.getlist('shop_for')
#     selected_styles = request.GET.getlist('bracelet_style')
#     selected_gemstones = request.GET.getlist('gemstone')
#     selected_materials = request.GET.getlist('metal_type')
#     selected_category =  request.GET.getlist('category')
#     try_at_home_filter = request.GET.get('try_at_home')

#     category_earring = Category.objects.get(name='Earring')
#     category_ring = Category.objects.get(name='Ring')
#     category_bracelets = Category.objects.get(name='Bracelets')

#     products = Product.objects.filter(is_active=True)
#     rings = Product.objects.filter(category=category_ring, is_active=True)
#     earrings = Product.objects.filter(category=category_earring, is_active=True)
#     bracelets = Product.objects.filter(category=category_bracelets, is_active=True)

#     if selected_ring_sizes:
#         rings = rings.filter(attributes__attribute_name='Ringsize', attributes__attribute_value__in=selected_ring_sizes)
#     if selected_ring_types:
#         rings = rings.filter(attributes__attribute_name='Ringtype', attributes__attribute_value__in=selected_ring_types)
#     if selected_earring_styles:
#         earrings = earrings.filter(attributes__attribute_name='Earring Style', attributes__attribute_value__in=selected_earring_styles)
#     if selected_styles:
#         bracelets = bracelets.filter(attributes__attribute_name='Bracelet Style', attributes__attribute_value__in=selected_styles)
#     if selected_shop_for:
#         products = products.filter(gender__in=selected_shop_for)

#     if selected_gemstones:
#         products = products.filter(stonetype__name__in=selected_gemstones)
#     if selected_materials:
#         products = products.filter(metaltype__name__in=selected_materials)
#     if try_at_home_filter:
#         products = products.filter(try_at_home=True)
#     if selected_category:
#         products =  products.filter(category__name__in=selected_category)

#     context = {
#         'products': products,
#         'rings': rings,
#         'earrings': earrings,
#         'bracelets': bracelets,
#         'categories':categories,
#         'earring_styles': earring_styles,
#         'bracelet_styles': bracelet_styles,
#         'ring_sizes': ring_sizes,
#         'ring_types': ring_types,
#         'shop_for_options': shop_for_options,
#         'gemstones': gemstones,
#         'materials': materials,
#         'selected_ring_sizes': selected_ring_sizes,
#         'selected_ring_types': selected_ring_types,
#         'selected_earring_styles': selected_earring_styles,
#         'selected_styles': selected_styles,
#         'selected_gemstones': selected_gemstones,
#         'selected_materials': selected_materials,
#         'selected_shop_for': selected_shop_for,
#     }

#     return render(request, 'user/all_products.html', context)

#-----------------------------------------------------------------------------------------------------------------------------
from django.shortcuts import render
from .models import Product, Category, Metaltype, Stonetype, CategoryAttribute, ProductAttribute

def all_products(request):
    products = Product.objects.filter(is_active=True)  # Fetch only active products
    
    # Get filter values from the request
    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_metaltype = request.GET.getlist('metaltype')
    selected_stonetype = request.GET.getlist('stonetype')
    selected_gender = request.GET.getlist('gender')
    try_at_home = request.GET.get('try_at_home', None)
    attribute_filters = {}

    # Debugging output
    print(f"Selected Category: {selected_category}")
    print(f"Search Query: {search_query}")

    # Filter by search query
    if search_query:
        products = products.filter(product_name__icontains=search_query)

    # Filter by category
    category_attributes = None
    if selected_category and selected_category.isdigit():  # Ensure valid category ID
        try:
            category_id = int(selected_category)
            print(f"Filtering by category ID: {category_id}")
            products = products.filter(category_id=category_id)

            # Fetch category-specific attributes
            category_attributes = CategoryAttribute.objects.filter(category_id=category_id)
            
            # Apply attribute filters from user input
            for attribute in category_attributes:
                attribute_value = request.GET.get(f"attribute_{attribute.id}", None)
                if attribute_value:
                    attribute_filters[attribute.name] = attribute_value
                    products = products.filter(
                        attributes__attribute_name=attribute.name,
                        attributes__attribute_value=attribute_value
                    )
        except ValueError:
            print("Invalid category ID passed.")

    # Filter by metal type
    if selected_metaltype:
        products = products.filter(metaltype_id__in=selected_metaltype)

    # Filter by stone type
    if selected_stonetype:
        products = products.filter(stonetype_id__in=selected_stonetype)

    # Filter by gender
    if selected_gender:
        products = products.filter(gender__in=selected_gender)

    # Filter by try at home
    if try_at_home:
        products = products.filter(try_at_home=True)

    # Fetch filter options
    categories = Category.objects.all()
    metaltypes = Metaltype.objects.all()
    stonetypes = Stonetype.objects.all()
    product_gender_choices = Product.GENDER_CHOICES

    context = {
        'products': products,
        'categories': categories,
        'metaltypes': metaltypes,
        'stonetypes': stonetypes,
        'product_gender_choices': product_gender_choices,
        'selected_category': selected_category,
        'category_attributes': category_attributes,
        'attribute_filters': attribute_filters
    }

    return render(request, 'user/all_products.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAttribute, Metaltype, Stonetype, Category

def detail(request, product_id):
    # Get the specific product by its ID, along with related Metaltype, Stonetype, and Category
    product = get_object_or_404(Product.objects.select_related('metaltype', 'stonetype', 'category'), product_id=product_id)
  

    # Fetch the product's attributes (e.g., ring size, ring type, etc.)
    product_attributes = ProductAttribute.objects.filter(product=product)

    # Fetch the category attributes for the specific product category (if any)
    category_attributes = product.category.attributes.all() if product.category else []

    context = {
        'product': product,
        'product_attributes': product_attributes,
        'category_attributes': category_attributes,
        'metaltype': product.metaltype,
        'stonetype': product.stonetype,
    }

    return render(request, 'user/all_details.html', context)

#---------------------------------------------------------------------------------------------------------------------------------------------------------

def get_booked_dates_for_product(product):
    # Fetch all booked dates for the given product
    booked_dates = Booking.objects.filter(product=product).values_list('booking_date', flat=True)
    return list(booked_dates)



# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Product, Tbl_user

# def book_schedule(request, product_id):
#     if 'login_id' not in request.session:
#         return redirect('login')  
    
#     login_id = request.session.get('login_id')
    
#     user = get_object_or_404(Tbl_user, login_id=login_id)  
    
#     product = get_object_or_404(Product, pk=product_id)
    
#     booked_dates = get_booked_dates_for_product(product) 

#     context = {
#         'product': product,
#         'user': user,
#         'booked_dates': booked_dates
#     }

#     return render(request, 'user/schedule_booking.html', context)



def book_schedule(request, product_id):
    if 'login_id' not in request.session:
        return redirect('login')  # Redirect to the login page if not logged in

    login_id = request.session.get('login_id')
    user = get_object_or_404(Tbl_user, login_id=login_id)
    product = get_object_or_404(Product, pk=product_id)
    booked_dates = get_booked_dates_for_product(product)

    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')

        # Check if the user has already booked the same product for the selected date
        existing_booking = Booking.objects.filter(user=user, product=product, date=booking_date).exists()

        if existing_booking:
            messages.error(request, "You have already booked this product for the selected date.")
        else:
            # Create a new booking
            Booking.objects.create(user=user, product=product, date=booking_date, status='pending')
            messages.success(request, "Your booking has been scheduled successfully.")
            return redirect('booking_confirmation')  # Redirect to a confirmation page

    context = {
        'product': product,
        'user': user,
        'booked_dates': booked_dates,
    }
    return render(request, 'user/schedule_booking.html', context)  # Render the template with context


from django.core.mail import send_mail
from django.conf import settings

def submit_schedule(request, product_id):
    if request.method == "POST":
        login_id = request.session.get('login_id')
        user = get_object_or_404(Tbl_user, login_id=login_id)
        product = get_object_or_404(Product, pk=product_id)
        address = request.POST.get('address')
        booking_date = request.POST.get('date')

        # Create and save a new booking
        booking = Booking(user=user, product=product, address=address, booking_date=booking_date)
        booking.save()

        # Send email to staff
        staff_email = 'jeelelzapaul@gmail.com'  # Replace with actual staff email
        subject = f'New Booking for {product.product_name}'
        message = f'Booking Details:\n\nUser: {user.name}\nPhone: {user.phone}\nProduct: {product.product_name}\nDate: {booking_date}\nAddress: {address}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [staff_email])

        # Redirect to booking details page with booking ID
        return redirect('booking_details', booking_id=booking.booking_id)
    
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    context = {
        'booking': booking,
        'product': booking.product,
        'user': booking.user
    }

    return render(request, 'user/booking_detail.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, Tbl_user, Product, Tbl_staff
from django.contrib import messages

def view_bookings(request):
    bookings = Booking.objects.all()  # Fetch all bookings
    staff_members = Tbl_staff.objects.filter(status=True)  # Active staff only

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = get_object_or_404(Booking, booking_id=booking_id)  # Get the specific booking
        user = booking.user
        product = booking.product

        if action == 'approve':
            booking.status = 'confirmed'
            booking.save()

            # Send email to the user
            send_mail(
                'Booking Confirmation',
                f'Dear {user.name},\n\nYour booking for {product.product_name} has been confirmed.',
                settings.DEFAULT_FROM_EMAIL,
                [user.login.email],
            )
            messages.success(request, 'Booking approved and email sent to user.')

        elif action == 'reject':
            booking.status = 'cancelled'
            booking.save()

            # Send email to the user
            send_mail(
                'Booking Cancellation',
                f'Dear {user.name},\n\nYour booking for {product.product_name} has been cancelled.',
                settings.DEFAULT_FROM_EMAIL,
                [user.login.email],
            )
            messages.success(request, 'Booking rejected and email sent to user.')

        elif action == 'assign_staff':
            staff_id = request.POST.get('staff_id')
            staff = get_object_or_404(Tbl_staff, staff_id=staff_id)

            # Assign the staff for try at home
            booking.try_at_home = True  # Assuming this attribute indicates assignment
            booking.save()

            # Send email to the staff
            send_mail(
                'New Try at Home Assignment',
                f'Dear {staff.name},\n\nYou have been assigned to assist with the booking for {product.product_name}.',
                settings.DEFAULT_FROM_EMAIL,
                [staff.login.email],
            )
            messages.success(request, 'Staff assigned and email sent to staff.')

        return redirect('view_bookings')  # Redirect to the same page to see updated status

    return render(request, 'admin/view_booking.html', {
        'bookings': bookings,
        'staff_members': staff_members,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Tbl_user

def booking_history(request):
    # Check if the user is logged in by verifying 'login_id' in the session
    if 'login_id' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    # Get the login_id from session and fetch the corresponding user
    login_id = request.session['login_id']
    user = get_object_or_404(Tbl_user, login_id=login_id)

    # Retrieve bookings for the logged-in user, ordered by most recent first
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')

    # Pass bookings to the template
    return render(request, 'user/booking.html', {'bookings': bookings})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Booking, Tbl_user

def edit_booking(request, booking_id):  
    # Check if the user is logged in
    if 'login_id' not in request.session:
        return redirect('login')

    login_id = request.session['login_id']
    user = get_object_or_404(Tbl_user, login_id=login_id)

    # Retrieve the booking based on booking_id and user
    booking = get_object_or_404(Booking, booking_id=booking_id, user=user)

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Phone validation
        if not (phone.isdigit() and len(phone) == 10 and phone[0] in '6789'):
            messages.error(request, "Phone number must be 10 digits and start with 6, 7, 8, or 9.")
            return render(request, 'user/edit_booking.html', {'form': None, 'booking': booking})

        # Address validation
        if not address.strip():
            messages.error(request, "Address cannot be empty.")
            return render(request, 'user/edit_booking.html', {'form': None, 'booking': booking})

        # Update the booking if validations pass
        booking.address = address
        booking.phone = phone  # Assuming you have a phone field in the Booking model
        booking.save()
        messages.success(request, "Booking updated successfully.")
        return redirect('booking_history')

    return render(request, 'user/edit_booking.html', {'form': None, 'booking': booking})

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# from django.shortcuts import render, redirect, get_object_or_404
# from django.urls import reverse
# from django.http import JsonResponse
# from .models import Cart, CartItem, Billing, Tbl_user, Order, Product
# from django.db import transaction

# Checkout View
# def checkout(request):
    
#     if 'login_id' not in request.session:
#         return redirect('login') 

#     login_id = request.session['login_id']
    
#     try:
#         user = Tbl_user.objects.get(login__login_id=login_id)
#     except Tbl_user.DoesNotExist:
#         return redirect('login')  

#     cart = get_object_or_404(Cart, login=login_id)
#     cart_items = cart.items.filter(status=True)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)

#     addresses = Billing.objects.filter(user=user)

   
#     context = {
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'addresses': addresses,
#     }
#     return render(request, 'user/billing.html', context)



from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Billing, Tbl_user

def add_address(request):
    # Check if the user is logged in
    if 'login_id' not in request.session:
        return redirect('login')
    
    # Retrieve the logged-in user's ID from the session
    login_id = request.session['login_id']
    
    # Get the `Tbl_user` instance related to the `Tbl_login` session ID
    try:
        user = Tbl_user.objects.get(login__login_id=login_id)
    except Tbl_user.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('checkout')

    if request.method == 'POST':
        # Collect form data
        house_name = request.POST.get('house_name')
        postal_address = request.POST.get('postal_address')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        # Create and save the new Billing address
        billing_address = Billing(
            user=user,  # `user` is an instance of `Tbl_user`
            house_name=house_name,
            postal_address=postal_address,
            city=city,
            district=district,
            state=state,
            pincode=pincode
        )
        
        try:
            billing_address.save()
            messages.success(request, "Address added successfully!")
            return redirect('checkout')
        except Exception as e:
            messages.error(request, f"Error saving address: {e}")
            return redirect('add_address')

    # Render the add address page if request method is GET
    return render(request, 'user/add_address.html')


# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Billing  # Replace with your actual address model

@csrf_exempt
def remove_address(request, address_id):
    if request.method == 'POST':
        try:
            address = Billing.objects.get(id=address_id)
            address.delete()
            return JsonResponse({'status': 'success'})
        except Billing.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Address not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Cart, CartItem, Product, Order, OrderItem, Billing, Payment, Tbl_login, Tbl_user
from django.conf import settings
import razorpay

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def checkout(request):
    if 'login_id' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    login_id = request.session['login_id']
    login_user = get_object_or_404(Tbl_login, login_id=login_id)
    user = get_object_or_404(Tbl_user, login=login_user)

    # Retrieve the user's cart and active cart items
    cart = get_object_or_404(Cart, login=login_user)
    cart_items = cart.items.filter(status=True)  # Only active items
    total_price = cart.total_price()

    # Retrieve billing addresses associated with the user
    addresses = Billing.objects.filter(user=user)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        
        # Check if an address is selected
        if not selected_address_id:
            messages.error(request, "Please select a billing address.")
            return redirect('checkout')  # Redirect back to the checkout page
        
        # Get the selected address and create an order
        address = get_object_or_404(Billing, id=selected_address_id)
        order = Order.objects.create(
            user=user,
            billing=address,
            cart=cart,
            total_amount=total_price,
            status='Pending'
        )

        # Create order items from cart items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Razorpay order creation
        razorpay_order = razorpay_client.order.create({
            "amount": int(total_price * 100),  # Amount in paise
            "currency": "INR",
            "payment_capture": "1"
        })
        
        # Store Razorpay order ID in the order
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return render(request, 'user/billing.html', {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_API_KEY,
            'total_price': total_price
        })

    return render(request, 'user/billing.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'addresses': addresses
    })


@csrf_exempt
def payment_handler(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        # Retrieve the corresponding order
        order = get_object_or_404(Order, razorpay_order_id=order_id)
        
        # Verify the Razorpay signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            # Payment is successful, save payment details
            Payment.objects.create(
                order=order,
                payment_id=payment_id,
                status="Success",
                amount=order.total_amount,
                created_at=timezone.now()
            )
            # Mark cart items as inactive and update stock quantities
            for item in order.cart.items.filter(status=True):
                item.status = False  # Mark item as inactive
                item.save()
                
                # Update stock quantity
                product = item.product
                product.stock_quantity = max(0, product.stock_quantity - item.quantity)
                product.save()
            
            # Update order status to completed
            order.status = "Completed"
            order.save()

            messages.success(request, "Payment successful and order placed.")
            return JsonResponse({"status": "success"})

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment failed due to signature verification error.")
            return JsonResponse({"status": "failed"})

    return JsonResponse({"status": "invalid request"})


# Order Summary View
# def order_summary(request, order_id):
#     if 'login_id' not in request.session:
#         return redirect('login')  
#     user_id = request.session['login_id']
    
#     order = get_object_or_404(Order, id=order_id, user_id=user_id)
#     context = {'order': order}
#     return render(request, 'order_summary.html', context)
