from django.shortcuts import render, redirect
from .forms import UserForm
from .models import TicTacToeUser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def register_user(request):
    """
    Handle user registration.

    This view processes the registration form for creating a new TicTacToeUser. 
    If the request method is POST, it validates and saves the form data. 
    On successful registration, the user is redirected to a specified URL.
    If the request method is GET, an empty form is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered registration template with the form.
        HttpResponseRedirect: Redirects to a URL after successful registration.
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('https://www.google.com/')  # Placeholder for post-registration redirect
    else:
        form = UserForm()
    return render(request, 'tictactoe_app/register.html', {'form': form})

def get_users(request):
    """
    Display a list of all registered users.

    This view retrieves all TicTacToeUser instances from the database and 
    renders them in a template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template with the list of users.
    """
    users = TicTacToeUser.objects.all()
    return render(request, 'tictactoe_app/users.html', {'users': users})


@csrf_exempt
def handle_login(request):
    """
    Handle user login via a POST request with JSON payload.

    This view processes a JSON payload containing 'username' and 'password'.
    It checks the credentials against hardcoded values and returns a JSON response
    indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object, expected to contain a JSON body with 'username' and 'password'.

    Returns:
        JsonResponse: A JSON response with a success or failure message and the appropriate HTTP status code.
    
    Raises:
        JSONDecodeError: If the JSON payload is malformed.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            # Hardcoded credentials (for demonstration purposes only)
            correct_username = 'my_username'
            correct_password = 'my_password'
            
            if username == correct_username and password == correct_password:
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Login failed'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)