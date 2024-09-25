from django import forms

class LoginForm(forms.Form):
    """
    LoginForm is a Django form class that facilitates user authentication by collecting
    the required credentials: username and password.

    Attributes:
        username (CharField): A field to input the user's username. It is limited
                              to a maximum length of 15 characters.
        password (CharField): A field to input the user's password. The input is
                              rendered as a password input type to mask the characters.

    Methods:
        There are no custom methods in this form. It relies on the built-in form
        methods provided by Django for validation and rendering.
    """

    # CharField for the username input
    username = forms.CharField(
        max_length=15,         # Sets the maximum number of characters allowed for the username.
        help_text="Enter your username."  # Provides a help message displayed in the form for guidance.
    )

    # CharField for the password input, rendered with a PasswordInput widget for security
    password = forms.CharField(
        widget=forms.PasswordInput,   # PasswordInput widget masks the input characters for security.
        help_text="Enter your password."  # Provides a help message displayed in the form for guidance.
    )