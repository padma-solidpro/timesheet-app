from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

def custom_logout(request):
    logout(request)
    return redirect(reverse('login'))

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")  
    return render(request, 'accounts/login.html')

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Check if the email is associated with a user
            user = User.objects.get(email=email)
            print(user)
            # Generate a password reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Send the email
            send_mail(
                'Password Reset Request',
                f'Hello {user.username},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.',
                'spdt-apps-svc@solidpro-es.com',  # Replace with your email
                [email],
                fail_silently=False,
            )

            # Redirect to a success page
            messages.success(request, 'Password reset link sent to your email.')
            return redirect('password_reset_done')
        except User.DoesNotExist:
            messages.error(request, 'No user is associated with this email address.')
    return render(request, 'accounts/password_reset.html')