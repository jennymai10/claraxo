import random
from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from google.cloud import secretmanager
from google.api_core.exceptions import AlreadyExists, PermissionDenied, NotFound

from datetime import timedelta, datetime, timezone
import uuid

class TicTacToeUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the Tic Tac Toe application.

    This model extends Django's AbstractBaseUser to provide additional fields like profile_name, age, 
    email, and account_type. It supports custom password hashing and API key management. The model also 
    includes a verification mechanism for email verification.

    Fields:
        - username (str): A unique username for the user.
        - profile_name (str): The display name of the user.
        - age (int): The user's age, with a minimum age requirement of 13.
        - email (str): A unique and valid email address.
        - account_type (int): The type of account (1 for Player, 2 for Research).
        - api_key (str): A hashed API key for external integrations.
        - is_active (bool): Whether the account is active (used for email verification).
        - verification_code (int): A 6-digit code for email verification.

    Methods:
        - set_api_key: Hashes the API key securely.
        - check_api_key: Validates the hashed API key.
    """

    ACCOUNT_TYPE_CHOICES = (
        (1, 'Player'),
        (2, 'Research'),
    )

    # A unique username with a minimum of 5 characters
    username = models.CharField(
        max_length=15,
        validators=[MinLengthValidator(5)],
        unique=True,
        help_text="A unique username with a minimum length of 5 characters."
    )

    # A profile name for display purposes with a minimum of 2 characters
    profile_name = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(2)],
        help_text="A display name for the user's profile."
    )

    # Age with a minimum of 13 and a maximum of 120
    age = models.IntegerField(
        validators=[MinValueValidator(13), MaxValueValidator(120)],
        help_text="The age of the user. Must be between 13 and 120 years."
    )

    # A unique and valid email address
    email = models.EmailField(
        validators=[EmailValidator()],
        unique=True,
        help_text="A valid email address."
    )

    # Account type: Player (1) or Research (2)
    account_type = models.IntegerField(
        choices=ACCOUNT_TYPE_CHOICES,
        help_text="The type of user account: Player or Research.",
        default=1
    )
    
    api_key_secret_id = models.UUIDField(
        default=uuid.uuid4(),
        editable=False,
        unique=True,
        null=True,
        help_text="A unique identifier for the user's API key secret."
    )
    api_key_expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The expiration date of the API key."
    )

    # Is the account active? (Email verified or not)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # A 6-digit verification code for email verification (optional until used)
    verification_code = models.IntegerField(blank=True, null=True)

    # Use the custom manager to handle user creation
    objects = BaseUserManager()

    # Define the unique identifier for authentication (username in this case)
    USERNAME_FIELD = 'username'

    # Required fields when creating a user
    REQUIRED_FIELDS = ['email', 'account_type', 'profile_name', 'age', 'api_key']

    def __str__(self):
        """
        Returns the string representation of the user, which is the username.
        """
        return self.username
    
    def store_api_key_in_secret_manager(self, api_key, secret_id, update_secret=False):
        """
        Store the API key in Google Cloud Secret Manager and return the secret name.
        If an old secret name is provided, it will be deleted first.
        
        Args:
            api_key (str): The new API key to store.
            secret_id (str): The new secret ID for the API key.
            old_secret_name (str): The name of the old secret to delete (optional).
        
        Returns:
            str: The name of the new secret.
        """
        client = secretmanager.SecretManagerServiceClient()
        project_id = 'c-lara'
        parent = f"projects/{project_id}"

        try:
            # Delete old secret if provided
            if update_secret:
                try:
                    secret_name = f"projects/{project_id}/secrets/api-key-{secret_id}"
                    old_secret = client.delete_secret(request={"name": secret_name})
                except Exception as e:
                    print(f"Failed to delete old secret: {str(e)}")

            # Create a new secret for the updated API key
            secret = client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": f"api-key-{secret_id}",
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            # Calculate the expiration date (180 days from now)
            expiration_date = datetime.now(timezone.utc) + timedelta(days=90)

            # Add a version with the new API key data and set the expiration
            version = client.add_secret_version(
                request={
                    "parent": secret.name,
                    "payload": {"data": api_key.encode("UTF-8")},
                }
            )
            self.api_key_expiry_date = expiration_date
            self.save()

            # Simulating expiration: store expiration timestamp in metadata (not enforced by Google Cloud)
            print(f"Created new secret: {version.name}, expires on {expiration_date}")
            return secret.name
        except Exception as e:
            # Handle the exception appropriately
            print(f"Failed to store API key in Secret Manager: {str(e)}")
            raise