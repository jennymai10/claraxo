from django import forms

class LoginForm(forms.Form):
    """
    Form for logging in users.

    This form collects the username and password from the user.
    """
    username = forms.CharField(
        max_length=15,
        help_text="Enter your username."
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter your password."
    )