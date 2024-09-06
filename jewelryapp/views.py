from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tbl_login, Tbl_user
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

        # Authentication logic
        try:
            user = Tbl_login.objects.get(email=email, password=password)
            # Set session data after successful login
            request.session['user_id'] = user.login_id
            request.session['email'] = user.email
            return redirect('/base_home/')  # Redirect to home page or dashboard after login
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
