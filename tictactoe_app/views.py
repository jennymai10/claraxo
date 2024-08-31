from django.shortcuts import render, redirect
from .forms import UserForm
from .models import TicTacToeUser

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
