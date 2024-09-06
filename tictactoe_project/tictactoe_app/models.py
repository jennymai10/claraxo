import random
from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class TicTacToeUserManager(BaseUserManager):
    """
    Custom manager for the TicTacToeUser model.

    Provides helper methods to create users with specific fields. This manager
    simplifies user creation by enforcing required fields and setting up
    verification codes and password hashing.
    """

    def create_user(self, username, password=None, email=None, account_type=None, profile_name=None, age=None, api_key=None):
        """
        Creates and returns a new user with the given fields. This method ensures
        that required fields like username, password, email, account_type, profile_name, 
        and age are provided. It also generates a random verification code for 
        email verification and hashes the password.

        Args:
            username (str): The username of the user (required).
            password (str): The password of the user (required, hashed internally).
            email (str): The email address of the user (required).
            account_type (int): The type of user (Player=1, Research=2).
            profile_name (str): The display name for the user's profile.
            age (int): The user's age (must be provided).
            api_key (str): Optional API key for the user (hashed internally).

        Returns:
            TicTacToeUser: A new user instance.

        Raises:
            ValueError: If any of the required fields are missing.
        """
        if not username:
            raise ValueError("The Username field is required.")
        if not password:
            raise ValueError("The Password field is required.")
        if not email:
            raise ValueError("The Email field is required.")
        if not account_type:
            raise ValueError("The Account Type field is required.")
        if not profile_name:
            raise ValueError("The Profile Name field is required.")
        if age is None:
            raise ValueError("The Age field is required.")

        # Create user instance but do not commit to the database yet
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            account_type=account_type,
            profile_name=profile_name,
            age=age,
            # Generate a random 6-digit verification code for email verification
            verification_code=random.randint(100000, 999999)
        )
        # Hash the password
        user.set_password(password)
        if api_key:
            # Hash the API key if provided
            user.set_api_key(api_key)
        # Save the user instance to the database
        user.save(using=self._db)
        return user


class TicTacToeUser(AbstractBaseUser):
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

    # A hashed API key for external integrations, if required
    api_key = models.CharField(
        max_length=128,
        blank=True,
        help_text="A securely hashed API key for the user.",
        default=''
    )

    # Is the account active? (Email verified or not)
    is_active = models.BooleanField(default=False)

    # A 6-digit verification code for email verification (optional until used)
    verification_code = models.IntegerField(blank=True, null=True)

    # Use the custom manager to handle user creation
    objects = TicTacToeUserManager()

    # Define the unique identifier for authentication (username in this case)
    USERNAME_FIELD = 'username'

    # Required fields when creating a user
    REQUIRED_FIELDS = ['email', 'account_type', 'profile_name', 'age', 'api_key']

    def __str__(self):
        """
        Returns the string representation of the user, which is the username.
        """
        return self.username

    def set_api_key(self, raw_api_key):
        """
        Hashes and securely stores the API key for the user, similar to password hashing.

        Args:
            raw_api_key (str): The plain-text API key that needs to be hashed.
        """
        self.api_key = make_password(raw_api_key)

    def check_api_key(self, raw_api_key):
        """
        Validates whether the provided API key matches the stored, hashed API key.

        Args:
            raw_api_key (str): The plain-text API key to be checked.

        Returns:
            bool: True if the API key matches the stored hash, False otherwise.
        """
        return self.api_key == make_password(raw_api_key)