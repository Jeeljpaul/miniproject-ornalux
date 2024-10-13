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

#userpage

def product(request):
    return render(request, 'user/product.html')


from django.shortcuts import render
from .models import Product, ProductAttribute

def earring_list(request):
    # Get all products initially
    earrings = Product.objects.filter(category__name='Earring')

    # Get filter parameters from the request
    earring_style = request.GET.getlist('earring_style')
    shop_for = request.GET.getlist('shop_for')
    gemstone = request.GET.getlist('gemstone')
    metal_type = request.GET.getlist('metal_type')

    # Apply filters based on the selected values
    if earring_style:
        earrings = earrings.filter(attributes__attribute_name='earring_style', attributes__attribute_value__in=earring_style)

    if shop_for:
        earrings = earrings.filter(gender__in=shop_for)

    if gemstone:
        earrings = earrings.filter(stonetype__name__in=gemstone)

    if metal_type:
        earrings = earrings.filter(metaltype__name__in=metal_type)

    # Use distinct to avoid duplicate products in case of multiple attribute matches
    earrings = earrings.distinct()

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



from django.shortcuts import render
from .models import Product, ProductAttribute, Metaltype, Stonetype, Category

def ring_list(request):
    # Fetch only the rings from the Product table
    category_ring = Category.objects.get(name='Ring')
    rings = Product.objects.filter(category=category_ring)

    # Get the filtering options from the request
    selected_ring_sizes = request.GET.getlist('ring_size')
    selected_ring_types = request.GET.getlist('ring_type')
    selected_gemstones = request.GET.getlist('gemstone')
    selected_materials = request.GET.getlist('material')

    # Apply filters if they exist
    if selected_ring_sizes:
        rings = rings.filter(attributes__attribute_name='Ringsize', 
                             attributes__attribute_value__in=selected_ring_sizes)

    if selected_ring_types:
        rings = rings.filter(attributes__attribute_name='Ringtype', 
                             attributes__attribute_value__in=selected_ring_types)

    if selected_gemstones:
        rings = rings.filter(metaltype__name__in=selected_gemstones)

    if selected_materials:
        rings = rings.filter(stonetype__name__in=selected_materials)

    # Fetch distinct ring sizes, ring types, gemstones, and materials for checkbox filters
    ring_sizes = ProductAttribute.objects.filter(attribute_name='Ringsize').values_list('attribute_value', flat=True).distinct()
    ring_types = ProductAttribute.objects.filter(attribute_name='Ringtype').values_list('attribute_value', flat=True).distinct()
    gemstones = Metaltype.objects.all().values_list('name', flat=True)
    materials = Stonetype.objects.all().values_list('name', flat=True)

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

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, product_id):
    
    if request.user.is_authenticated:
        
        if request.method == 'POST':
            product = get_object_or_404(Product, product_id=product_id)
            
            user = get_object_or_404(Tbl_user, user_id=request.user.id)
            user_cart, created = Cart.objects.get_or_create(login=user.login)

            cart_item, item_created = CartItem.objects.get_or_create(cart=user_cart, product=product)

            if not item_created:
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({'success': True, 'message': f'{product.product_name} added to cart successfully!'})
    else:
        return JsonResponse({'success': False, 'message': 'User not authenticated.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Tbl_user, Product, Wishlist

def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Retrieve the logged-in user's Tbl_user instance
            user = Tbl_user.objects.get(login__email=request.user.email)

            # Retrieve the product based on the product_id
            product = get_object_or_404(Product, product_id=product_id)

            # Check if the product is already in the user's wishlist
            wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

            if created:
                # If the item is newly added to the wishlist
                return JsonResponse({'success': True, 'message': 'Product added to wishlist successfully!'})
            else:
                # If the item already exists in the wishlist
                return JsonResponse({'success': False, 'message': 'Product is already in your wishlist.'})
        else:
            # If the user is not authenticated, ask them to log in
            return JsonResponse({'success': False, 'message': 'You need to be logged in to add items to the wishlist.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


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

