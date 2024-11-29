from django.shortcuts import render
from ..forms import UserRegistrationForm, LoginForm
from ..models import TicTacToeUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
import random, json
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timezone, timedelta
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import IntegrityError
from ..utils import decrypt_data

@swagger_auto_schema(
    method='post',
    operation_description="Update the profile of the logged-in user, including username, email, full name, account type, age, API key, and password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="New username for the user"
            ),
            'email': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="New email address, triggers email verification"
            ),
            'fullname': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="Full name or display name of the user"
            ),
            'account_type': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description="Type of user account, represented as an integer"
            ),
            'age': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description="Age of the user"
            ),
            'api_key': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted API key, containing 'ciphertext' and 'iv' fields",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted password, containing 'ciphertext' and 'iv' fields",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="Profile updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request: Validation error or duplicate field",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'error'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message with details"),
                }
            )
        ),
        401: 'Unauthorized: Authentication required'
    }
)
@login_required
@api_view(['POST'])
def update_profile(request):
    """
    Update the profile of the currently logged-in user.
    Handles changes to username, email, full name, account type, age, API key, and password.
    """
    user = request.user  # Get the current logged-in user
    data = request.data  # Access the request data, assuming JSON or form data format

    try:
        # Update username if provided
        if 'username' in data:
            user.username = data['username']
            user.save()

        # Update email and trigger verification if the email changes
        if 'email' in data and user.email != data['email']:
            user.email = data['email']
            user.verification_code = random.randint(100000, 999999)
            user.is_active = False  # Deactivate until verification
            user.save()
            send_verification_email(user)  # Trigger verification email

        # Update full name (display name) if provided
        if 'fullname' in data:
            user.profile_name = data['fullname']
            user.save()
        
        # Update account type if provided
        if 'account_type' in data:
            user.account_type = int(data['account_type'])
            user.save()

        # Update age if provided
        if 'age' in data:
            user.age = int(data['age'])
            user.save()
 
        # Update API key if a new, valid key is provided
        if 'api_key' in data and data['api_key'] != 'PLACEHOLDER':
            encrypted_api_key = json.loads(request.POST.get('api_key'))
            decrypted_api_key = decrypt_data(encrypted_api_key['ciphertext'], None, encrypted_api_key['iv'])
            if decrypted_api_key != 'PLACEHOLDER':
                user.store_api_key_in_secret_manager(decrypted_api_key, user.api_key_secret_id, True)
                user.save()
        
        # Update password securely if provided
        if 'password' in data:
            encrypted_password = json.loads(request.POST.get('password'))
            decrypted_password = decrypt_data(encrypted_password['ciphertext'], None, encrypted_password['iv'])
            if decrypted_password != 'PLACEHOLDER':
                user.set_password(decrypted_password)
                user.save()
                update_session_auth_hash(request, user)  # Ensure session remains active after password change

        # Save the user and profile changes
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Account updated successfully.'}, status=200)

    except IntegrityError as e:
        # Handle integrity errors (duplicate username/email)
        if 'tictactoe_app_tictactoeuser.email' in str(e):
            return JsonResponse({'status': 'error', 'message': 'Email is already in use.'}, status=400)
        elif 'tictactoe_app_tictactoeuser.username' in str(e):
            return JsonResponse({'status': 'error', 'message': 'Username is already in use.'}, status=400)
    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="Register a new user with encrypted password and API key. After registration, the user is redirected to email verification.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['password', 'password2', 'api_key'],
        properties={
            'password': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted password with 'ciphertext' and 'iv' fields",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING, description="Ciphertext of the password"),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING, description="Initialization vector for decryption")
                }
            ),
            'password2': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted password confirmation, should match 'password'",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING, description="Ciphertext of the confirmation password"),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING, description="Initialization vector for decryption")
                }
            ),
            'api_key': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted API key with 'ciphertext' and 'iv' fields",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING, description="Ciphertext of the API key"),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING, description="Initialization vector for decryption")
                }
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="User registered successfully and redirected to email verification",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL for email verification")
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request: Decryption or validation error",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'error'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT, description="Detailed form validation errors")
                }
            )
        ),
        405: 'Method Not Allowed: Only POST is allowed'
    }
)
@api_view(['POST'])
def register_user(request):
    """
    Register a new user with encrypted password and API key.
    This function decrypts sensitive data, validates the user form, and sends a verification email.
    """
    
    if request.method == 'POST':
        # Parse and load encrypted password, confirmation, and API key from request data
        encrypted_password = json.loads(request.data.get('password'))
        encrypted_password2 = json.loads(request.data.get('password2'))
        encrypted_api_key = json.loads(request.data.get('api_key'))

        # Validate presence of 'ciphertext' and 'iv' for decryption
        if 'ciphertext' not in encrypted_password or 'iv' not in encrypted_password:
            return JsonResponse({'status': 'error', 'message': 'Invalid encrypted password data.'}, status=400)
        if 'ciphertext' not in encrypted_api_key or 'iv' not in encrypted_api_key:
            return JsonResponse({'status': 'error', 'message': 'Invalid encrypted API key data.'}, status=400)

        # Decrypt the password, password confirmation, and API key
        decrypted_password = decrypt_data(encrypted_password['ciphertext'], None, encrypted_password['iv'])
        decrypted_password2 = decrypt_data(encrypted_password2['ciphertext'], None, encrypted_password2['iv'])
        decrypted_api_key = decrypt_data(encrypted_api_key['ciphertext'], None, encrypted_api_key['iv'])

        # Verify decryption and matching passwords
        if not decrypted_password or decrypted_password != decrypted_password2:
            return JsonResponse({'status': 'error', 'message': 'Failed to decrypt data or passwords do not match.'}, status=400)
        
        # Prepare form data with decrypted values
        form_data = request.POST.copy()
        form_data['password'] = decrypted_password
        form_data['password2'] = decrypted_password2
        form_data['api_key'] = decrypted_api_key

        # Validate and save user registration form
        form = UserRegistrationForm(form_data)
        if form.is_valid():
            user = form.save(commit=False)
            user.verification_code = random.randint(100000, 999999)  # Generate verification code
            user.is_active = False  # Deactivate account until verification
            user.save()
            send_verification_email(user)  # Send verification email

            # Redirect URL for email verification
            redirect_url = '/verifyemail/' + user.username
            return JsonResponse({
                'status': 'success',
                'message': 'Successfully created an account. Proceeding to Email Verification.',
                'redirect_url': redirect_url
            }, status=200)
        else:
            # Handle form validation errors
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'status': 'error',
                'message': "Form validation failed.",
                'errors': errors
            }, status=400)

    # Return error if request method is not POST
    return JsonResponse({
        'status': 'error',
        'message': "Not a POST request."
    }, status=405)

@swagger_auto_schema(
    method='post',
    operation_description="Verify the user's email using the username and a 6-digit verification code. Activates the user's account upon successful verification.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'verification_code'],
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="Username of the user attempting verification"
            ),
            'verification_code': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="6-digit verification code sent to the user's email"
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="Email verified successfully, user is logged in and redirected",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL to redirect after successful verification"),
                }
            )
        ),
        401: openapi.Response(
            description="Unauthorized: Invalid verification code or username",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'error'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message describing the issue"),
                    'errors': openapi.Schema(
                        type=openapi.TYPE_OBJECT, 
                        description="Detailed error for incorrect verification code",
                        properties={
                            'verification_code': openapi.Schema(type=openapi.TYPE_STRING, description="Specific error message for the verification code")
                        }
                    )
                }
            )
        ),
        405: 'Method Not Allowed: Only POST is allowed'
    }
)
@api_view(['POST'])
def verifyemail(request):
    """
    Handle email verification for new users.
    Verifies the username and 6-digit code, activates the account, and logs the user in.
    """
    
    if request.method == 'POST':
        # Retrieve username and verification code from the request
        username = request.POST['username']
        code = request.POST['verification_code']

        try:
            # Look up the user by username and verification code
            user = TicTacToeUser.objects.get(username=username, verification_code=code)
            
            # Activate user account and clear the verification code
            user.is_active = True
            user.verification_code = None
            user.save()

            # Log the user in after successful verification
            login(request, user)
            
            # Redirect to the new game page upon successful verification
            return JsonResponse({
                'status': 'success',
                'redirect_url': "/new_game/",
            }, status=200)

        except TicTacToeUser.DoesNotExist:
            # Handle case where username or code is incorrect
            errors = {'verification_code': 'Invalid verification code.'}
            return JsonResponse({
                'status': 'error',
                'message': "Invalid verification code.",
                'errors': errors
            }, status=401)

    # Render the email verification page for non-POST requests
    return render(request, 'tictactoe_app/verifyemail.html')

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve details of the authenticated user.",
    responses={
        200: openapi.Response(
            description="User data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the authenticated user"),
                    'account_type': openapi.Schema(type=openapi.TYPE_INTEGER, description="Account type of the user"),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email address of the user"),
                    'api_key': openapi.Schema(type=openapi.TYPE_STRING, description="Placeholder for API key"),
                    'password': openapi.Schema(type=openapi.TYPE_STRING, description="Placeholder for password"),
                    'age': openapi.Schema(type=openapi.TYPE_INTEGER, description="Age of the user"),
                    'full_name': openapi.Schema(type=openapi.TYPE_STRING, description="Full name or display name of the user"),
                }
            )
        ),
        404: openapi.Response(
            description="User not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message if user does not exist")
                }
            )
        ),
        401: 'Unauthorized: Authentication required'
    }
)
@login_required
@api_view(['GET'])
def get_user(request):
    """
    Retrieve and display the profile information of the authenticated user.
    Accessible only to logged-in users.
    """
    
    user = request.user  # Get the current authenticated user
    
    try:
        # Retrieve the TicTacToeUser object for the authenticated user
        ttt_user = TicTacToeUser.objects.get(username=user.username)
        
        # Prepare user data for response
        user_data = {
            'username': ttt_user.username,
            'account_type': ttt_user.account_type,
            'email': ttt_user.email,
            'api_key': "PLACEHOLDER",  # Placeholder for security
            'password': "PLACEHOLDER",  # Placeholder for security
            'age': ttt_user.age,
            'full_name': ttt_user.profile_name,
        }
        
        # Return the user's profile data as JSON
        return JsonResponse(user_data, status=200)
    
    except TicTacToeUser.DoesNotExist:
        # Handle case where user does not exist in the database
        return JsonResponse({'error': 'User does not exist'}, status=404)

@swagger_auto_schema(
    method='post',
    operation_description="Authenticate and log in a user with encrypted credentials. Redirects to email verification if the email is not verified.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted username with 'ciphertext' and 'iv' fields",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING, description="Ciphertext of the username"),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING, description="Initialization vector for decryption")
                }
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Encrypted password with 'ciphertext' and 'iv' fields",
                properties={
                    'ciphertext': openapi.Schema(type=openapi.TYPE_STRING, description="Ciphertext of the password"),
                    'iv': openapi.Schema(type=openapi.TYPE_STRING, description="Initialization vector for decryption")
                }
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="User logged in successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL to redirect after successful login"),
                }
            )
        ),
        401: openapi.Response(
            description="Unauthorized: Invalid credentials or email not verified",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'error'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message describing the issue"),
                    'errors': openapi.Schema(
                        type=openapi.TYPE_OBJECT, 
                        description="Detailed error messages for incorrect credentials or unverified email",
                        properties={
                            'submit': openapi.Schema(type=openapi.TYPE_STRING, description="Specific error message")
                        }
                    ),
                    'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL to redirect for email verification, if needed")
                }
            )
        ),
        405: 'Method Not Allowed: Only POST is allowed'
    }
)
@api_view(['POST'])
def login_user(request):
    """
    Handle user login with encrypted credentials.
    Validates credentials, logs in the user, and checks email verification.
    """
    
    if request.method == 'POST':
        # Parse encrypted password and username from the request data
        encrypted_password = json.loads(request.POST.get('password'))
        encrypted_username = json.loads(request.POST.get('username'))
        
        # Validate presence of 'ciphertext' and 'iv' in both fields
        if 'ciphertext' not in encrypted_password or 'iv' not in encrypted_password:
            return JsonResponse({'status': 'error', 'message': 'Invalid encrypted password data.'}, status=400)
        if 'ciphertext' not in encrypted_username or 'iv' not in encrypted_username:
            return JsonResponse({'status': 'error', 'message': 'Invalid encrypted username data.'}, status=400)

        # Decrypt the password and username
        decrypted_password = decrypt_data(encrypted_password['ciphertext'], None, encrypted_password['iv'])
        decrypted_username = decrypt_data(encrypted_username['ciphertext'], None, encrypted_username['iv'])

        # Ensure decryption was successful
        if not decrypted_password or not decrypted_username:
            return JsonResponse({'status': 'error', 'message': 'Failed to decrypt username or password.'}, status=400)

        # Authenticate user using Django's built-in system
        user = authenticate(request, username=decrypted_username, password=decrypted_password)
            
        if user is not None:
            # Extend API key expiry if approaching expiration
            if user.api_key_expiry_date:
                user.api_key_expiry_date = datetime.now(timezone.utc) + timedelta(days=90)
            
            # Check if the user's email is verified
            if user.is_active:
                login(request, user)  # Log in the user
                return JsonResponse({
                    'status': 'success',
                    'redirect_url': '/new_game/'
                })

        else:
            # Handle incorrect username/password or unverified email
            try:
                user_object = TicTacToeUser.objects.get(username=decrypted_username)
                
                # If the user's email is unverified, resend verification email
                if not user_object.is_active:
                    send_verification_email(user_object)
                    redirect_url = '/verifyemail/' + user_object.username
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Email has not been verified.',
                        'errors': {'submit': 'Email has not been verified. You will be redirected to verify your email in 5s.'},
                        'redirect_url': redirect_url,
                    }, status=401)
            except TicTacToeUser.DoesNotExist:
                # Return error if username is not found
                return JsonResponse({
                    'status': 'error',
                    'message': 'Incorrect username or password.',
                    'errors': {'submit': 'Incorrect username or password.'},
                }, status=401)
    else:
        # Render an empty login form if request is not POST
        form = LoginForm()
        return render(request, 'tictactoe_app/login.html', {'form': form})

@swagger_auto_schema(
    method='post',
    operation_description="Log out the current user and provide a success message upon logout.",
    responses={
        200: openapi.Response(
            description="User logged out successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Logout success message"),
                }
            )
        ),
        405: 'Method Not Allowed: Only POST and GET are allowed'
    }
)
@swagger_auto_schema(
    method='get',
    operation_description="Log out the current user and provide a success message upon logout.",
    responses={
        200: openapi.Response(
            description="User logged out successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Logout success message"),
                }
            )
        ),
        405: 'Method Not Allowed: Only POST and GET are allowed'
    }
)
@api_view(['POST', 'GET'])
def logout_user(request):
    """
    Log out the current user and return a success message.
    """
    logout(request)  # Log out the current authenticated user
    
    # Return JSON response confirming logout success
    return JsonResponse({
        'status': 'success',
        'message': 'Successfully logged out!',
    }, status=200)

@swagger_auto_schema(
    method='post',
    operation_description="Resend email verification code to the specified username.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username'],
        properties={
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Username of the user requesting verification code resend"
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Verification email resent successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'success'"),
                    'redirect_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL to redirect for verification"),
                }
            )
        ),
        401: openapi.Response(
            description="Unauthorized: Invalid username or user does not exist",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'error'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message describing the issue"),
                    'errors': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Detailed error for invalid username",
                        properties={
                            'submit': openapi.Schema(type=openapi.TYPE_STRING, description="Specific error message for invalid username")
                        }
                    )
                }
            )
        ),
        500: openapi.Response(
            description="Server error: Invalid request method or other error",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates 'error'"),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message describing the server issue"),
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT, description="Additional error details if available"),
                }
            )
        ),
    }
)
@api_view(['POST'])
def verifyemail_resend(request):
    """
    Resend email verification code to a user based on their username.
    """
    
    if request.method == 'POST':
        # Retrieve the username from the request data
        username = request.POST['username']
        
        try:
            # Attempt to retrieve the user by their username
            user = TicTacToeUser.objects.get(username=username)
            
            # If the user is not found, return an error response
            if user is None:
                errors = {'submit': 'Username is invalid. Please sign up for an account.'}
                return JsonResponse({
                    'status': 'error',
                    'message': "Username is invalid.",
                    'errors': errors
                }, status=401)
            
            # Deactivate user, generate a new verification code, and send verification email
            user.is_active = False
            user.verification_code = random.randint(100000, 999999)
            user.save()
            send_verification_email(user)

            # Return success response with a redirect URL
            return JsonResponse({
                'status': 'success',
                'redirect_url': "/verifyemail/",
            }, status=200)
        
        except TicTacToeUser.DoesNotExist:
            # Handle case where username is invalid and the user does not exist
            errors = {'submit': 'Username is invalid. Please sign up for an account.'}
            return JsonResponse({
                'status': 'error',
                'message': "Username is invalid.",
                'errors': errors,
            }, status=401)

    # Return an error for invalid request method
    return JsonResponse({
        'status': 'error',
        'message': "Invalid GET Request.",
        'errors': {'submit': 'Only POST requests are allowed.'}
    }, status=500)

def send_verification_email(user_object):
    """
    Send an email to the user with a verification code for email verification.
    """
    
    subject = 'ClaraXO | Email Verification'
    from_email = settings.EMAIL_HOST_USER
    to_email = [user_object.email]

    # Load HTML email content from template
    html_content = render_to_string('emails/verification_email.html', {
        'profile_name': user_object.profile_name,
        'verification_code': user_object.verification_code,
        'username': user_object.username
    })

    # Fallback plain text version of the email
    text_content = f"Hi {user_object.profile_name},\nYour verification code is {user_object.verification_code}."

    # Create the email with both HTML and plain text versions
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()