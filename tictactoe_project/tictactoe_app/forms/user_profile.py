from django import forms
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from ..models import TicTacToeUser
from ..views import get_secret
from django.core.mail import send_mail
from django.conf import settings
import random

class UserProfileForm(forms.ModelForm):
    """
        UserProfileForm is a Django form class for updating user profile information,
        including fields such as username, email, profile name, age, and optional fields
        for changing the password and API key. It handles validation for email changes and
        old password verification when updating the password.

        Attributes:
            old_password (CharField): Optional field for inputting the old password, used when changing the password.
            new_password (CharField): Optional field for inputting the new password, used to update the user's password.
            api_key (CharField): Optional field for updating the user's API key in the secret manager.

        Meta:
            model (TicTacToeUser): Specifies the model that this form is associated with.
            fields (list): Specifies the fields to include in the form.

        Methods:
            clean_old_password(): Validates the old password if provided.
            clean_email(): Handles email change verification and sends a verification code.
            save(commit=True): Saves the form data, updates password and API key if provided, and commits changes to the database.
        """
    old_password = forms.CharField(required=False, widget=forms.PasswordInput(), help_text="Enter old password to change your password.")
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(), help_text="Enter new password if you want to change it.")
    api_key = forms.CharField(required=False, widget=forms.PasswordInput(), help_text="Update your API key.")
    
    class Meta:
        model = TicTacToeUser
        fields = ['username', 'email', 'profile_name', 'age']

    def clean_old_password(self):
        """
        Validates the old password provided by the user.

        If the user has entered an old password, this method checks if it is correct
        by authenticating the user with the current username and old password. If the
        authentication fails, it raises a ValidationError.

        Returns:
            str: The cleaned old_password data.

        Raises:
            forms.ValidationError: If the old password is incorrect.
        """
        old_password = self.cleaned_data.get('old_password')
        if old_password:
            user = self.instance
            if not authenticate(username=user.username, password=old_password):
                raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean_email(self):
        """
        Validates the email field and handles email change verification.

        If the email is changed, this method sets the user as inactive and generates
        a new verification code. It then sends an email with the new verification code
        to the updated email address.

        Returns:
            str: The cleaned email data.
        """
        email = self.cleaned_data.get('email')
        if self.instance.email != email:
            # If email is changed, mark the user as inactive until verified again
            self.instance.is_active = False
            self.instance.verification_code = random.randint(100000, 999999)
            # Send an email verification message
            send_mail(
                'Email Verification',
                f'Your new verification code is {self.instance.verification_code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        return email

    def save(self, commit=True):
        """
        Saves the form data, including updating the password and API key if provided.

        If a new password is provided, this method sets it for the user. It also updates
        the API key in Google Cloud Secret Manager if a new key is provided and differs
        from the current one. After making all changes, it saves the user instance.

        Args:
            commit (bool): Indicates whether to commit the changes to the database. Default is True.

        Returns:
            TicTacToeUser: The saved user instance.
        """
        user = super().save(commit=False)
        
        # Update password if provided
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        # Update API key in Secret Manager if provided
        api_key = self.cleaned_data.get('api_key')
        if api_key != get_secret(f"api-key-{user.api_key_secret_id}"):
            secret_name = user.store_api_key_in_secret_manager(api_key, str(user.api_key_secret_id), True)
        
        if commit:
            user.save()
        return user