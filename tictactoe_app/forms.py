from django import forms
from .models import TicTacToeUser

# Form class for creating or updating a TicTacToeUser
class UserForm(forms.ModelForm):
    class Meta:
        model = TicTacToeUser  # Specifies the model to use for this form
        fields = ['username', 'password', 'email', 'account_type']  # Fields to include in the form
        widgets = {
            'password': forms.PasswordInput(),  # Renders the password field as a password input (masked)
        }

    # Custom validation for the username field
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5 or len(username) > 15:
            raise forms.ValidationError("Username must be between 5 and 15 characters long.")
        return username

    # Custom validation for the account_type field
    def clean_account_type(self):
        account_type = self.cleaned_data.get('account_type')
        if account_type not in [1, 2]:
            raise forms.ValidationError("Account type must be 1 or 2.")
        return account_type
