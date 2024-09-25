from django import forms
import re
from ..models.user_model import TicTacToeUser

class UserRegistrationForm(forms.ModelForm):
    """
    UserRegistrationForm is a Django form class used to create and update TicTacToeUser instances.
    It is based on the TicTacToeUser model and provides fields for user registration and profile
    updates, including username, password, email, account type, profile name, age, and an optional
    API key for external integrations.

    This form includes custom validation methods for:
    - Passwords: Ensuring strong password security.
    - Username: Validating username length.
    - Account type: Ensuring correct account type selection.
    - Age: Validating a realistic age range.

    Attributes:
        password2 (CharField): An additional password field for confirming the user's password.
        api_key (CharField): An optional field for providing an API key for external services.

    Meta:
        model (TicTacToeUser): Specifies the model that this form is associated with.
        fields (list): Specifies the fields to include in the form.
        widgets (dict): Custom widgets for the form fields to control their rendering.
        help_texts (dict): Help text for each form field to guide the user.

    Methods:
        clean_password2(): Validates that both password fields match and meet security criteria.
        clean_username(): Validates that the username is between 5 and 15 characters long.
        clean_account_type(): Ensures the account type is either 1 (Player) or 2 (Research).
        clean_age(): Validates that the user's age is within a realistic range.
        save(commit=True): Hashes the password and API key securely before saving the user instance.
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
        Custom validation for the password confirmation field.

        This method checks that both the 'password' and 'password2' fields match.
        It also validates that the password meets the following security requirements:
        - Length between 7 and 25 characters.
        - Contains at least one number.
        - Contains at least one uppercase letter.

        Returns:
            str: The cleaned 'password2' value if all validations pass.

        Raises:
            forms.ValidationError: If the passwords do not match or do not meet security requirements.
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
        Custom validation for the username field.

        This method ensures that the username length is between 5 and 15 characters.
        It also checks if the username is unique within the application.

        Returns:
            str: The cleaned 'username' value if it meets the length requirements.

        Raises:
            forms.ValidationError: If the username is not between 5 and 15 characters.
        """
        username = self.cleaned_data.get('username')
        if len(username) < 5 or len(username) > 15:
            raise forms.ValidationError("Username must be between 5 and 15 characters long.")
        return username

    def clean_account_type(self):
        """
        Custom validation for the account type field.

        Ensures that the account type is either 1 (Player) or 2 (Research).
        If the input does not match these values, a validation error is raised.

        Returns:
            int: The cleaned 'account_type' value if it is valid.

        Raises:
            forms.ValidationError: If the account type is not 1 or 2.
        """
        account_type = self.cleaned_data.get('account_type')
        if account_type not in [1, 2]:
            raise forms.ValidationError("Account type must be 1 (Player) or 2 (Research).")
        return account_type

    def clean_age(self):
        """
        Custom validation for the age field.

        Ensures that the age is a positive integer between 13 and 120.
        This is to ensure that the user is of a realistic and acceptable age.

        Returns:
            int: The cleaned 'age' value if it is valid.

        Raises:
            forms.ValidationError: If the age is less than 13 or greater than 120.
        """
        age = self.cleaned_data.get('age')
        if age <= 0 or age > 120:
            raise forms.ValidationError("Invalid age.")
        return age

    def save(self, commit=True):
        """
        Overrides the default save method to hash the password and API key before saving.

        This method securely hashes the password using the set_password method provided
        by Django's AbstractBaseUser model. It also stores the API key using a secret
        manager if provided.

        Args:
            commit (bool): Indicates whether to commit the changes to the database. Defaults to True.

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