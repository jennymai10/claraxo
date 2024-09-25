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
    Form for updating user profile information, including username, email, age, profile name,
    API key, and password. The form ensures email verification for updated email and validates
    old password when changing the password.
    """
    old_password = forms.CharField(required=False, widget=forms.PasswordInput(), help_text="Enter old password to change your password.")
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(), help_text="Enter new password if you want to change it.")
    api_key = forms.CharField(required=False, widget=forms.PasswordInput(), help_text="Update your API key.")
    
    class Meta:
        model = TicTacToeUser
        fields = ['username', 'email', 'profile_name', 'age']

    def clean_old_password(self):
        """
        Ensure the user provides the correct old password if they are changing their password.
        """
        old_password = self.cleaned_data.get('old_password')
        if old_password:
            user = self.instance
            if not authenticate(username=user.username, password=old_password):
                raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean_email(self):
        """
        If the email is changed, mark the user as inactive and generate a new verification code.
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
        Handle API key update using Google Cloud Secret Manager and other profile changes.
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