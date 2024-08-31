from django.shortcuts import render, redirect
from .forms import UserForm
from .models import TicTacToeUser

#@login_required
def manage_account(request):
    """
    Render the manage account page where users can change their username, email,
    date of birth, and password.
    """
    return render(request, 'tictactoe_app/manage_account.html', {'user': request.user})

#@login_required
def change_email(request):
    """
    Handle the email change request for a logged-in user.

    This view allows a user to change their email. It validates the new email
    and updates the user's information in the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the email change form template.
        HttpResponseRedirect: Redirects to a success page after successful update.
    """
    user = request.user

    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            user.email = new_email
            user.save()
            return redirect('profile')  # Redirect to a profile page or success page
    return render(request, 'tictactoe_app/manage_account.html', {'user': user})

#@login_required
def change_date_of_birth(request):
    """
    Handle the date of birth change request for a logged-in user.

    This view allows a user to change their date of birth. It validates the new date of birth
    and updates the user's information in the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the date of birth change form template.
        HttpResponseRedirect: Redirects to a success page after successful update.
    """
    user = request.user

    if request.method == 'POST':
        new_dob = request.POST.get('date_of_birth')
        if new_dob:
            user.date_of_birth = new_dob
            user.save()
            return redirect('profile')  # Redirect to a profile page or success page
    return render(request, 'tictactoe_app/manage_account.html', {'user': user})

#@login_required
def change_password(request):
    """
    Handle the password change request for a logged-in user.

    This view allows a user to change their password. It validates the new password
    and updates the user's information in the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the password change form template.
        HttpResponseRedirect: Redirects to a success page after successful update.
    """
    user = request.user

    if request.method == 'POST':
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in after password change
            return redirect('profile')  # Redirect to a profile page or success page
    return render(request, 'tictactoe_app/manage_account.html', {'user': user})


# @login_required
def change_username(request):
    """
    Handle the username change request for a logged-in user.

    This view allows a user to change their username. It validates the new username
    and updates the user's information in the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the username change form template.
        HttpResponseRedirect: Redirects to a success page after successful update.
    """
    user = request.user  # Get the logged-in user

    if request.method == 'POST':
        new_username = request.POST.get('username')
        if new_username:
            user.username = new_username
            user.save()
            return redirect('profile')  # Redirect to a profile page or success page
    return render(request, 'tictactoe_app/manage_account.html', {'user': user})

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
