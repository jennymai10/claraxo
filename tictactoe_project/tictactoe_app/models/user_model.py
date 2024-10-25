import random
from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from google.cloud import secretmanager
from google.api_core.exceptions import AlreadyExists, PermissionDenied, NotFound

from datetime import timedelta, datetime, timezone
import uuid

class TicTacToeUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Set the password using the built-in method
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given username, email, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class TicTacToeUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the Tic Tac Toe application.

    This model extends Django's AbstractBaseUser and PermissionsMixin to provide additional fields and functionalities
    specific to the application, such as custom user attributes (profile name, age, account type) and methods for API
    key management and email verification.

    Fields:
        username (CharField): A unique username for the user with a minimum length of 5 characters.
        profile_name (CharField): A display name for the user, with a minimum length of 2 characters.
        age (IntegerField): The age of the user, with constraints to ensure it is between 13 and 120.
        email (EmailField): A unique and valid email address for the user.
        account_type (IntegerField): The type of user account, either 'Player' (1) or 'Research' (2).
        api_key_secret_id (UUIDField): A unique identifier for the user's API key, used for secure external integrations.
        api_key_expiry_date (DateTimeField): The expiration date of the API key.
        is_active (BooleanField): Indicates whether the user's account is active (typically used for email verification).
        is_staff (BooleanField): Indicates whether the user has staff privileges.
        is_superuser (BooleanField): Indicates whether the user has superuser privileges.
        verification_code (IntegerField): A 6-digit code used for email verification.

    Methods:
        store_api_key_in_secret_manager(api_key, secret_id, update_secret=False):
            Stores the API key securely in Google Cloud Secret Manager, optionally updating an existing secret.
    """
    objects = TicTacToeUserManager()

    ACCOUNT_TYPE_CHOICES = (
        (1, 'Player'),
        (2, 'Research'),
    )

    # A unique username with a minimum of 5 characters
    username = models.CharField(
        max_length=15,
        validators=[MinLengthValidator(5)], # Ensures the username has at least 5 characters
        unique=True,                        # Enforces the uniqueness of the username
        help_text="A unique username with a minimum length of 5 characters."
    )

    # A profile name for display purposes with a minimum of 2 characters
    profile_name = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(2)], # Ensures the profile name has at least 2 characters
        help_text="A display name for the user's profile."
    )

    # User's age with a minimum of 13 and a maximum of 120
    age = models.IntegerField(
        validators=[MinValueValidator(13), MaxValueValidator(120)], # Age should be between 13 and 120
        help_text="The age of the user. Must be between 13 and 120 years."
    )

    # A unique and valid email address for user communication
    email = models.EmailField(
        validators=[EmailValidator()], # Ensures the email is in a valid format
        unique=True,                   # Enforces the uniqueness of the email address
        help_text="A valid email address."
    )

    # Account type: Player (1) or Research (2)
    account_type = models.IntegerField(
        choices=ACCOUNT_TYPE_CHOICES, # Limits the choices to predefined account types
        help_text="The type of user account: Player or Research.",
        default=1 # Default account type is set to Player
    )

    # A unique identifier for the user's API key secret in the Google Cloud Secret Manager
    api_key_secret_id = models.UUIDField(
        default=uuid.uuid4(),  # Generates a unique UUID for each API key
        editable=False,        # The field is not editable by users
        unique=True,           # Ensures the UUID is unique
        null=True,             # Allows the field to be null if no API key is set
        help_text="A unique identifier for the user's API key secret."
    )

    # Expiration date for the API key
    api_key_expiry_date = models.DateTimeField(
        blank=True,  # The field can be left blank
        null=True,  # The field can be null if no expiration date is set
        help_text="The expiration date of the API key."
    )

    # Boolean fields indicating user permissions and status
    is_staff = models.BooleanField(default=False)  # Indicates if the user has staff privileges
    is_superuser = models.BooleanField(default=False)  # Indicates if the user has superuser privileges
    is_active = models.BooleanField(default=False)  # Indicates if the user account is active (email verified)

    # A 6-digit verification code for email verification (optional until used)
    verification_code = models.IntegerField(blank=True, null=True)

    # Use the custom manager to handle user creation
    # objects = BaseUserManager()

    # Define the unique identifier for authentication (username in this case)
    USERNAME_FIELD = 'username'

    # Required fields when creating a user
    REQUIRED_FIELDS = ['email', 'account_type', 'profile_name', 'age', 'api_key']

    def __str__(self):
        """
        Returns the string representation of the user, which is the username.

        Returns:
            str: The username of the user.
        """
        return self.username
    
    def store_api_key_in_secret_manager(self, api_key, secret_id, update_secret=False):
        """
        Store the API key in Google Cloud Secret Manager and return the secret name.

        This method securely stores the provided API key in Google Cloud Secret Manager under a unique secret ID.
        If the 'update_secret' flag is set to True, it will first attempt to delete the existing secret before
        creating a new one with the updated API key.

        Args:
            api_key (str): The new API key to store.
            secret_id (str): The unique identifier for the API key secret.
            update_secret (bool): Whether to update an existing secret. Default is False.

        Returns:
            str: The name of the newly created secret in the Secret Manager.

        Raises:
            Exception: If there is an error in storing the API key or creating the secret.
        """
        client = secretmanager.SecretManagerServiceClient()  # Create a client for Secret Manager
        project_id = 'c-lara'  # The GCP project ID where secrets are stored
        parent = f"projects/{project_id}"  # Parent resource path for the secrets

        try:
            # Delete old secret if provided
            if update_secret:
                try:
                    secret_name = f"projects/{project_id}/secrets/api-key-{secret_id}"
                    old_secret = client.delete_secret(request={"name": secret_name})  # Attempt to delete the old secret
                except Exception as e:
                    print(f"Failed to delete old secret: {str(e)}") # Handle deletion error
            if not api_key or api_key == '':
                self.api_key_expiry_date = None
                return None
            # Create a new secret for the updated API key
            secret = client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": f"api-key-{secret_id}",
                    "secret": {"replication": {"automatic": {}}}, # Use automatic replication for the secret
                }
            )
            # Calculate the expiration date (90 days from now)
            expiration_date = datetime.now(timezone.utc) + timedelta(days=90)

            # Add a version with the new API key data and set the expiration
            version = client.add_secret_version(
                request={
                    "parent": secret.name,
                    "payload": {"data": api_key.encode("UTF-8")}, # Encode API key as UTF-8
                }
            )

            # Store the expiration date in the model
            self.api_key_expiry_date = expiration_date
            self.save()

            # Log and return the created secret's name
            print(f"Created new secret: {version.name}, expires on {expiration_date}")
            return secret.name
        except Exception as e:
            # Handle any errors during the API key storage process
            print(f"Failed to store API key in Secret Manager: {str(e)}")
            raise # Re-raise the exception for further handling