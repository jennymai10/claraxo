from django.shortcuts import render, redirect
from ..forms import UserRegistrationForm, LoginForm
from ..models import TicTacToeUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random

from django.http import JsonResponse

from django.middleware.csrf import get_token

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

def register_user(request):
    """
    Handle the user registration process.

    This view renders a registration form where a new user can input their details. 
    If the request method is POST, the form is validated, and if valid:
    - A new user instance is created with the form data.
    - A random 6-digit verification code is generated.
    - The user's 'is_active' field is set to False, so the user cannot log in until email verification.
    - An email with the verification code is sent to the user's email address.
    On successful registration, the user is redirected to the email verification page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered registration template with the form.
        HttpResponseRedirect: Redirect to the email verification page if the form is valid.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user temporarily without committing to add verification details
            user = form.save(commit=False)
            # Generate a random 6-digit verification code
            user.verification_code = random.randint(100000, 999999)
            # Mark the user as inactive until email is verified
            user.is_active = False
            user.save()

            # Redirect to the email verification page
            return redirect('http://localhost:8000/verify_email/')
    else:
        # Display the empty registration form for a GET request
        form = UserRegistrationForm()

    return render(request, 'tictactoe_app/register.html', {'form': form})


def verify_email(request):
    """
    Handle email verification for new users.

    This view allows the user to input their username and the 6-digit verification code
    they received via email. If the code matches the one generated during registration,
    the user's account is activated, and they are logged in. Otherwise, an error message
    is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered email verification template with or without an error message.
        HttpResponseRedirect: Redirect to the login page after successful verification and activation.
    """
    send_mail(
                'Email Verification',
                f'Your verification code is {user.verification_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['code']
        try:
            # Retrieve the user by their username and verification code
            user = TicTacToeUser.objects.get(username=username, verification_code=code)
            # Activate the user and clear the verification code
            user.is_active = True
            user.verification_code = None
            user.save()
            # Automatically log in the user after verification
            login(request, user)
            # Redirect to the login page
            return redirect('http://localhost:8000/login/')
        except TicTacToeUser.DoesNotExist:
            # If the username or code is incorrect, render the verification page with an error
            return render(request, 'tictactoe_app/verify_email.html', {'error': 'Invalid code or username'})
    return render(request, 'tictactoe_app/verify_email.html')


@login_required
def get_users(request):
    """
    Display all registered users.

    This view retrieves all TicTacToeUser instances from the database and displays
    them on the users page. It is only accessible to logged-in users due to the 
    @login_required decorator.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template with the list of registered users.
    """
    # Query all registered users from the TicTacToeUser model
    users = TicTacToeUser.objects.all()
    # Render the users template and pass the users data to the template
    return render(request, 'tictactoe_app/users.html', {'users': users})


def login_user(request):
    """
    Handle user login.

    This view processes the login form, where a user can input their username and password.
    If the credentials are valid, the user is logged in and redirected to the users page.
    If the user's account is not activated (i.e., email not verified), they are prompted
    to verify their email first. If the credentials are invalid, an error message is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered login template with the form and optional error messages.
        HttpResponseRedirect: Redirect to the users page after successful login.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)
            # Authenticate the user with the provided credentials
            user = authenticate(request, username=username, password=password)
            print(user.account_type)
            if user is not None:
                # Check if the user's email is verified (is_active is True)
                if user.is_active:
                    # Log in the user
                    login(request, user)
                    return JsonResponse({
                        'status': 'success',
                        'redirect_url': '/new_game/'
                    })
                else:
                    # If the user's email is not verified, display an error message
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please verify your email before logging in.',
                        'redirect_url': '/verify_email/'
                    }, status=403)
            else:
                # If the credentials are invalid, add an error to the form
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid username or password.',
                    'redirect_url': '/login/'
                }, status=401)
    else:
        # Display the empty login form for a GET request
        form = LoginForm()
        return render(request, 'tictactoe_app/login.html', {'form': form})
        # return JsonResponse({
        #         'status': 'error',
        #         'message': 'Empty form.',
        #         'redirect_url': '/login/'
        #     }, status=400)

@login_required
def logout_user(request):
    """
    Handle user logout.

    This view logs out the user and redirects them to the login page.
    """
    logout(request)
    return redirect('/login/')

def get_user_type(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = TicTacToeUser.objects.get(username=username)
            account_type = user.account_type
            return JsonResponse({'status': 'success', 'account_type': account_type})
        except TicTacToeUser.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'User not found'})
    return JsonResponse({'status': 'fail', 'message': 'Only POST requests are allowed'})