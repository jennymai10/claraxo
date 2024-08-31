from django import forms
from .models import TicTacToeUser

class UserForm(forms.ModelForm):
    """
    Form for creating and updating TicTacToeUser instances.

    This form is based on the TicTacToeUser model and provides fields for 
    username, password, email, and account type. It includes custom validation
    logic for the username and account type fields.
    """

    class Meta:
        model = TicTacToeUser
        fields = ['username', 'password', 'email', 'account_type']
        widgets = {
            'password': forms.PasswordInput(),
        }
        help_texts = {
            'username': 'A unique username between 7 and 15 characters long.',
            'password': 'A secure password for the user.',
            'email': 'A valid email address for user communication.',
            'account_type': 'Select 1 for Player or 2 for Research account type.',
        }

    def clean_username(self):
        """
        Validates the username field.

        Ensures that the username is between 7 and 15 characters long.
        If the username does not meet this requirement, a ValidationError is raised.

        Returns:
            str: The cleaned username.
        
        Raises:
            forms.ValidationError: If the username is not between 7 and 15 characters.
        """
        username = self.cleaned_data.get('username')
        if len(username) < 7 or len(username) > 15:
            raise forms.ValidationError("Username must be between 7 and 15 characters long.")
        return username

    def clean_account_type(self):
        """
        Validates the account_type field.

        Ensures that the account type is either 1 (Player) or 2 (Research).
        If the account type does not meet this requirement, a ValidationError is raised.

        Returns:
            int: The cleaned account type.
        
        Raises:
            forms.ValidationError: If the account type is not 1 or 2.
        """
        account_type = self.cleaned_data.get('account_type')
        if account_type not in [1, 2]:
            raise forms.ValidationError("Account type must be 1 or 2.")
        return account_type