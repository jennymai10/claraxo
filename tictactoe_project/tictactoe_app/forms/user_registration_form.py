from django import forms
import re
from ..models.user_model import TicTacToeUser

class UserRegistrationForm(forms.ModelForm):
    """
    Form for creating and updating TicTacToeUser instances.

    This form is based on the TicTacToeUser model and provides fields for username,
    password, password confirmation (password2), email, account_type, profile_name,
    age, and api_key. It includes custom validation for passwords to ensure strong 
    security and also checks for username, account type, and age validation.
    """

    password2 = forms.CharField(label='Re-type Password', widget=forms.PasswordInput())
    api_key = forms.CharField(widget=forms.PasswordInput(), required=False, help_text='Optional API key for external integrations.')


    class Meta:
        model = TicTacToeUser
        fields = ['username', 'password', 'password2', 'email', 'account_type', 'profile_name', 'age', 'api_key']
        widgets = {
            'password': forms.PasswordInput(),  # Mask the password input field
            'api_key': forms.PasswordInput(),   # Mask the API key input field
        }
        help_texts = {
            'username': 'A unique username between 5 and 15 characters long.',
            'password': 'A secure password for the user.',
            'password2': 'Please enter the same password again for confirmation.',
            'email': 'A valid email address for user communication.',
            'account_type': 'Select 1 for Player or 2 for Research account type.',
            'profile_name': 'A display name between 2 and 30 characters long.',
            'age': 'Your age. Must be at least 13 years old.',
            'api_key': 'A secure API key for GPT-4.',
        }

    def clean_password2(self):
        """
        Custom validation method for passwords.

        This method validates that both password and password2 match and checks that the password
        meets the following security requirements:
        - Length between 7 and 25 characters.
        - Contains at least one number.
        - Contains at least one uppercase letter.

        Returns:
            str: The cleaned password2 value if the validation passes.

        Raises:
            forms.ValidationError: If passwords do not match or if password does not meet the requirements.
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        # Ensure passwords match
        if password and password2:
            if password != password2:
                raise forms.ValidationError("Passwords do not match.")
            
            # Check for password length (7-25 characters)
            if len(password) < 7 or len(password) > 25:
                raise forms.ValidationError("Password must be between 7 and 25 characters long.")

            # Check for at least one number
            if not re.search(r'\d', password):
                raise forms.ValidationError("Password must contain at least one number.")

            # Check for at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")

        return password2

    def clean_username(self):
        """
        Custom validation method for the username.

        This method ensures that the username length is between 5 and 15 characters.

        Returns:
            str: The cleaned username value.

        Raises:
            forms.ValidationError: If the username is not between 5 and 15 characters.
        """
        username = self.cleaned_data.get('username')
        if len(username) < 5 or len(username) > 15:
            raise forms.ValidationError("Username must be between 5 and 15 characters long.")
        return username

    def clean_account_type(self):
        """
        Custom validation method for the account type.

        Ensures that the account type is either 1 (Player) or 2 (Research).

        Returns:
            int: The cleaned account_type value.

        Raises:
            forms.ValidationError: If the account type is not 1 or 2.
        """
        account_type = self.cleaned_data.get('account_type')
        if account_type not in [1, 2]:
            raise forms.ValidationError("Account type must be 1 (Player) or 2 (Research).")
        return account_type

    def clean_age(self):
        """
        Custom validation method for age.

        Ensures that the age is a positive integer. You can customize it further to add minimum age restrictions.

        Returns:
            int: The cleaned age value.

        Raises:
            forms.ValidationError: If age is less than or equal to 0.
        """
        age = self.cleaned_data.get('age')
        if age <= 0 or age > 120:
            raise forms.ValidationError("Invalid age.")
        return age

    def save(self, commit=True):
        """
        Override the save method to securely hash the password and API key before saving the user instance.

        This method hashes both the password and API key using the built-in methods provided by Django's
        AbstractBaseUser model.

        Args:
            commit (bool): Whether to commit the user instance to the database. Defaults to True.

        Returns:
            TicTacToeUser: The saved user instance with hashed password and API key.
        """
        user = super().save()

        # Hash the password securely before saving
        user.set_password(self.cleaned_data['password'])

        # Hash the API key securely before saving (if provided)
        if 'api_key' in self.cleaned_data and self.cleaned_data['api_key']:
            # Store the API key using the secret manager and link to the user model
            secret_name = user.store_api_key_in_secret_manager(self.cleaned_data['api_key'], str(user.api_key_secret_id))
            user.api_key_secret_name = secret_name

        if commit:
            user.save()
        return user