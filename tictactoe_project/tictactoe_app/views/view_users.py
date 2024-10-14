from django.shortcuts import render, redirect
from ..forms import UserRegistrationForm, LoginForm, UserProfileForm
from ..models import TicTacToeUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random
from google.cloud import secretmanager
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Get CSRF Token",
    responses={200: openapi.Response('CSRF Token', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'csrfToken': openapi.Schema(type=openapi.TYPE_STRING)
    }))}
)
@api_view(['GET'])
def get_csrf_token(request):
    """
    Retrieve a CSRF token.

    This view generates a CSRF token that can be used for making secure POST requests.
    This is particularly useful when building frontend applications that need to interact
    with Django APIs.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the CSRF token.
    """
    csrf_token = get_token(request)  # Generate a CSRF token for the current session
    return JsonResponse({'csrfToken': csrf_token}, 200)

@swagger_auto_schema(
    method='post',
    operation_description="Update the profile of a logged-in user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'age': openapi.Schema(type=openapi.TYPE_INTEGER),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Response('Success'),
        400: 'Bad Request'
    }
)
@login_required
@api_view(['POST'])
def update_profile(request):
    print(request.data)
    user = request.user  # Get the current logged-in user
    data = request.data  # Assuming POST data comes in as JSON or form data

    try:
        # Update username
        if 'username' in data:
            user.username = data['username']
            user.save()

        # Update email
        if 'email' in data and user.email != data['email']:
            user.email = data['email']
            user.verification_code = random.randint(100000, 999999)
            user.is_active = False  # Mark user inactive until email is verified
            user.save()  # Save the email change first
            # Here you should trigger the email verification process
            send_mail(
                'C-Lara | Email Verification',
                f'Hi {user.profile_name}! Your verification code is {user.verification_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

        # Update full name (profile name)
        if 'fullname' in data:
            user.profile_name = data['fullname']
            user.save()
        
        if 'account_type' in data:
            user.account_type = int(data['account_type'])
            user.save()

        # Update age
        if 'age' in data:
            user.age = int(data['age'])
            user.save()
 
        # Update API key
        if 'api_key' in data and data['api_key'] != 'PLACEHOLDER':
            user.store_api_key_in_secret_manager(data['api_key'], user.api_key_secret_id, True)
            user.save()

        # Update password
        if 'password' in data and data['password'] != 'PLACEHOLDER':
            user.set_password(data['password'])  # Update the password securely
            user.save()
            update_session_auth_hash(request, user)  # Update session so the user stays logged in

        # Save the user and profile changes
        user.save()
        print("Profile updated successfully.")
        # Return success response
        return JsonResponse({'status': 'success', 'message': 'Account updated successfully.'}, status=200)
    except Exception as e:
        # Return error message in case something goes wrong
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="Register a new user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'password', 'email']
    ),
    responses={
        200: openapi.Response('User registered successfully', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'redirect_url': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        400: 'Form validation failed',
    }
)
@api_view(['POST'])
def register_user(request):
    """
    Handle user registration process.

    This view allows new users to register by providing their username, password, and email.
    Once the form is validated and the user is created, a verification email is sent to the
    provided email address. The user cannot log in until they verify their email.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating success or failure of registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.verification_code = random.randint(100000, 999999)  # Generate a random 6-digit verification code
            user.is_active = False  # Set user as inactive until email is verified
            user.save()
            send_mail(
                'C-Lara | Email Verification',
                f'Hi {user.profile_name}! Your verification code is {user.verification_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            # Redirect to the email verification page
            redirect_url = '/verifyemail/' + user.username
            return JsonResponse({
                        'status': 'success',
                        'message': 'Successfully created an account. Proceeding to Email Verification.',
                        'redirect_url': redirect_url
                    }, status=200)
        else:
            # Handle form validation errors
            errors = {field: error[0] for field, error in form.errors.items()}
            print(errors)
            return JsonResponse({
                    'status': 'error',
                    'message': "Form validation failed.",
                    'errors': errors
                }, status=400)
    return JsonResponse({
                    'status': 'error',
                    'message': "Not a POST request.",
                    'errors': errors
                }, status=400)


@swagger_auto_schema(
    method='post',
    operation_description="Verify the user's email with a 6-digit verification code",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'verification_code': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response('Email verified successfully', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'redirect_url': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        401: openapi.Response('Invalid verification code', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
    }
)
@api_view(['POST'])
def verifyemail(request):
    """
    Handle email verification for new users.

    This view allows users to verify their email address by providing their username and
    the 6-digit verification code sent to their email. If the code matches, the user's
    account is activated, and they are automatically logged in.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating success or failure of the verification.
    """
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['verification_code']
        try:
            # Retrieve the user by their username and verification code
            user = TicTacToeUser.objects.get(username=username, verification_code=code)
            # Activate the user and clear the verification code
            user.is_active = True  # Activate the user account
            user.verification_code = None  # Clear the verification code
            user.save()
            # Automatically log in the user after verification
            login(request, user)  # Log the user in
            # Redirect to the login page
            return JsonResponse({
                    'status': 'success',
                    'redirect_url': "/new_game/",
                }, status=200)
        except TicTacToeUser.DoesNotExist:
            # If the username or code is incorrect, render the verification page with an error
            errors = {'verification_code': 'Invalid verification code.'}
            return JsonResponse({
                    'status': 'error',
                    'message': "Invalid verification code.",
                    'errors': errors
                }, status=401)
    return render(request, 'tictactoe_app/verifyemail.html')


@swagger_auto_schema(
    method='get',
    operation_description="Get a list of all registered users (authenticated users only)",
    responses={
        200: openapi.Response('List of users', openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )),
    }
)

@login_required
@api_view(['GET'])
def get_user(request):
    """
    Display all registered users.

    This view retrieves and displays all registered users. It is accessible only to
    authenticated users due to the @login_required decorator.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the users page with the list of registered users.
    """
    user = request.user  # Get the current authenticated user
    try:
        ttt_user = TicTacToeUser.objects.get(username=user.username)
        # Prepare the data to send to the frontend
        user_data = {
            'username': ttt_user.username,
            'account_type': ttt_user.account_type,
            'email': ttt_user.email,
            'api_key': "PLACEHOLDER",
            'password': "PLACEHOLDER",
            'age': ttt_user.age,
            'full_name': ttt_user.profile_name,
        }
        return JsonResponse(user_data, status=200)
    except TicTacToeUser.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)


@swagger_auto_schema(
    method='post',
    operation_description="Authenticate a user with their username and password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Response('Login successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'redirect_url': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        401: openapi.Response('Login failed', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
    }
)
@api_view(['POST'])
def login_user(request):
    """
    Handle user login.

    This view processes user login by validating the credentials provided in the login form.
    If the credentials are correct and the user's email is verified, they are logged in.
    If the API key associated with the user is expiring soon, a warning email is sent to the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating success or failure of the login attempt, along with a redirect URL.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Bind the form with the POST data
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate the user with the provided credentials
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if the API key is expiring soon (less than 7 days)
                if user.api_key_expiry_date:
                    current_time = datetime.now(timezone.utc)  # Get the current time in UTC
                    days_remaining = (user.api_key_expiry_date - current_time).days
                    if days_remaining <= 7:
                        # Send a warning email to the user about the API key expiration
                        send_warning_email(user, days_remaining)
                
                # Check if the user's email is verified (is_active is True)
                if user.is_active:
                    # Log in the user
                    login(request, user)
                    return JsonResponse({
                        'status': 'success',
                        'redirect_url': '/new_game/'
                    })
            else:
                # Handle when authentication fails (incorrect username or password)
                try:
                    user_object = TicTacToeUser.objects.get(username=username)
                    # If the user's email is not verified
                    if not user_object.is_active:
                        send_mail(
                            'C-Lara | Email Verification',
                            f'Hi {user_object.profile_name}! Your verification code is {user_object.verification_code}',
                            settings.EMAIL_HOST_USER,
                            [user_object.email],
                            fail_silently=False,
                        )
                        # If email is not verified, redirect to the email verification page
                        redirect_url = '/verifyemail/' + user_object.username
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Email has not been verified.',
                            'errors': {'submit': 'Email has not been verified. You will be redirected to verify your email in 5s.'},
                            'redirect_url': redirect_url,
                        }, status=401)
                except TicTacToeUser.DoesNotExist:
                    # If the username does not exist in the database
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Incorrect username or password.',
                        'errors': {'submit': 'Incorrect username or password.'},
                    }, status=401)
    else:
        # For a GET request, render an empty login form
        form = LoginForm()
        return render(request, 'tictactoe_app/login.html', {'form': form})

@swagger_auto_schema(
    method='get',
    operation_description="Log out the authenticated user and redirect to the login page",
    responses={302: 'Redirect to login'}
)
@api_view(['POST', 'GET'])
def logout_user(request):
    """
    Handle user logout.

    This view logs out the current user and redirects them to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects the user to the login page after logging out.
    """
    logout(request)  # Log out the current user
    return JsonResponse({
                        'status': 'success',
                        'message': 'Successfully logged out!',
                    }, status=200)

def send_warning_email(user, days_remaining):
    """
    Send a warning email to the user if their API key is expiring soon.

    This function sends an email notification to the user if their API key is set to expire
    within the next 7 days, reminding them to renew their key.

    Args:
        user (TicTacToeUser): The user whose API key is expiring.
        days_remaining (int): Number of days left before the API key expires.

    Returns:
        None
    """

    # Email subject and message content
    subject = 'C-Lara | Your API Key is Expiring Soon'
    message = f"""
    Hello {user.profile_name},

    This is a reminder that your API key will expire in {days_remaining} day(s).

    Please take necessary action to renew your API key before it expires.

    Best regards,
    C-Lara TicTacToe Team
    """
    
    # Send the email to the user's email address
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender email address from settings
        [user.email],  # Recipient's email address
        fail_silently=False,  # Raise exceptions if the email fails to send
    )

@api_view(['POST'])
def verifyemail_resend(request):
    if request.method == 'POST':
        username = request.POST['username']
        try:
            # Retrieve the user by their username and verification code
            user = TicTacToeUser.objects.get(username=username)
            if user is None:
                errors = {'submit': 'Username is invalid. Please sign up for an account.'}
                return JsonResponse({
                    'status': 'error',
                    'message': "Username is invalid.",
                    'errors': errors
                }, status=401)
            # Activate the user and clear the verification code
            user.is_active = False  # Activate the user account
            user.verification_code = random.randint(100000, 999999)  # Clear the verification code
            user.save()
            send_mail(
                    'C-Lara | Email Verification',
                    f'Hi {user.profile_name}! Your verification code is {user.verification_code}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
            return JsonResponse({
                    'status': 'success',
                    'redirect_url': "/verifyemail/",
                }, status=200)
        except TicTacToeUser.DoesNotExist:
            errors = {'submit': 'Username is invalid. Please sign up for an account.'}
            return JsonResponse({
                    'status': 'error',
                    'message': "Username is invalid.",
                    'errors': errors,
                }, status=401)
    return JsonResponse({
                        'status': 'error',
                        'message': "Invalid GET Request.",
                        'errors': errors,
                    }, status=500)