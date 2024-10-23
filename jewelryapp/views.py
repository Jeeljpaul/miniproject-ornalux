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


#----------------------------------------------------------------------------------------------------------------------------------------------------------

#adminpage

from django.shortcuts import render, redirect
from .models import Category, CategoryAttribute

def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        attribute_names = request.POST.getlist('attribute_names')
        attribute_datatypes = request.POST.getlist('attribute_datatypes')


        if category_name and attribute_names and attribute_datatypes:
            # Create a new Category
            category = Category.objects.create(name=category_name)

            # Add each attribute to the category
            for name, datatype in zip(attribute_names, attribute_datatypes):
                if name:  # Make sure the attribute name is not empty
                    CategoryAttribute.objects.create(category=category, name=name, datatype=datatype)
            return redirect('add_category')  # Redirect to the same page after saving

    return render(request, 'admin/add_category.html')

    
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


from django.shortcuts import render
from .models import Product, Category, Metaltype, Stonetype

def all_products(request):
    # Get all the products initially
    products = Product.objects.filter(is_active=True)
    
    # Get the categories and other filter options for display in the template
    categories = Category.objects.all()
    metal_types = Metaltype.objects.all()
    stone_types = Stonetype.objects.all()

    # Get the filter values from the request
    category_filter = request.GET.getlist('category')
    try_at_home_filter = request.GET.get('try_at_home')
    ring_size_filter = request.GET.getlist('ring_size')
    ring_type_filter = request.GET.getlist('ring_type')
    earring_style_filter = request.GET.getlist('earringstyle')
    bracelet_style_filter = request.GET.getlist('bracelet_style')
    gender_filter = request.GET.getlist('shop_for')
    gemstone_filter = request.GET.getlist('stone_type')
    material_filter = request.GET.getlist('metal_type')

    # Apply category filtering if selected
    if category_filter:
        products = products.filter(category__name__in=category_filter)
    
    # Apply Try at Home filter
    if try_at_home_filter == 'true':
        products = products.filter(try_at_home=True)

    # Apply ring size filter if selected
    if ring_size_filter:
        products = products.filter(attributes__attribute_name='Ring Size', attributes__attribute_value__in=ring_size_filter)

    # Apply ring type filter if selected
    if ring_type_filter:
        products = products.filter(attributes__attribute_name='Ring Type', attributes__attribute_value__in=ring_type_filter)

    # Apply earring style filter if selected
    if earring_style_filter:
        products = products.filter(attributes__attribute_name='Earring Style', attributes__attribute_value__in=earring_style_filter)

    # Apply bracelet style filter if selected
    if bracelet_style_filter:
        products = products.filter(attributes__attribute_name='Bracelet Style', attributes__attribute_value__in=bracelet_style_filter)

    # Apply gender filter if selected
    if gender_filter:
        products = products.filter(gender__in=gender_filter)

    # Apply gemstone filter if selected
    if gemstone_filter:
        products = products.filter(stonetype__name__in=gemstone_filter)

    # Apply material filter if selected
    if material_filter:
        products = products.filter(metaltype__name__in=material_filter)

    # Prepare the selected filters to pass back to the template
    context = {
        'categories': categories,
        'metal_types': metal_types,
        'stone_types': stone_types,
        'rings': products.filter(category__name='Ring'),
        'earrings': products.filter(category__name='Earring'),
        'bracelets': products.filter(category__name='Bracelet'),
        'selected_category': category_filter,
        'try_at_home_filter': try_at_home_filter,
        'selected_ring_sizes': ring_size_filter,
        'selected_ring_types': ring_type_filter,
        'selected_earring_styles': earring_style_filter,
        'selected_styles': bracelet_style_filter,
        'selected_shop_for': gender_filter,
        'selected_gemstones': gemstone_filter,
        'selected_materials': material_filter,
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


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, Booking
from django.utils import timezone

# Schedule booking form view
def schedule_booking(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    # Retrieve booked dates for the same product
    booked_dates = Booking.objects.filter(product=product).values_list('date', flat=True)
    return render(request, 'schedule_booking.html', {'product': product, 'booked_dates': booked_dates})

def submit_schedule(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, product_id=product_id)
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        date = request.POST.get('date')

        # Validate the inputs
        if not name or not phone or not address or not date:
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        if len(phone) != 10 or not phone.isdigit():
            return JsonResponse({'error': 'Invalid phone number'}, status=400)

        # Save the booking
        booking = Booking.objects.create(
            product=product,
            name=name,
            phone=phone,
            address=address,
            date=date,
            status='Pending'  # Set status as pending
        )

        return redirect('booking_confirmation', booking_id=booking.id)

