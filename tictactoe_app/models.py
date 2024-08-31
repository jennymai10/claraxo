from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class TicTacToeUserManager(BaseUserManager):
    """
    Custom manager for TicTacToeUser model.

    Provides helper methods to create a user with specific fields.
    """

    def create_user(self, username, password=None, email=None, account_type=None):
        """
        Creates and returns a new user with the given username, password, email, and account type.

        Args:
            username (str): The username of the user. This field is required.
            password (str): The password for the user. This field is required.
            email (str): The email address of the user. This field is required.
            account_type (int): The type of the account (1 for Player, 2 for Research). This field is required.

        Returns:
            TicTacToeUser: A new user instance.

        Raises:
            ValueError: If any of the required fields are not provided.
        """
        if not username:
            raise ValueError("The Username field is required.")
        if not password:
            raise ValueError("The Password field is required.")
        if not email:
            raise ValueError("The Email field is required.")
        if not account_type:
            raise ValueError("The Account Type field is required.")
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            account_type=account_type
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class TicTacToeUser(AbstractBaseUser):
    """
    Custom user model for the Tic Tac Toe application.

    This model extends the AbstractBaseUser to include fields for username, email,
    password, and account type. It uses the TicTacToeUserManager for object creation.
    """

    ACCOUNT_TYPE_CHOICES = (
        (1, 'Player'),
        (2, 'Research'),
    )

    username = models.CharField(
        max_length=15,
        validators=[MinLengthValidator(7)],
        unique=True,
        help_text="A unique username with a minimum length of 7 characters."
    )
    password = models.CharField(
        max_length=35,
        help_text="A secure password with a maximum length of 35 characters."
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="A valid email address."
    )
    account_type = models.IntegerField(
        choices=ACCOUNT_TYPE_CHOICES,
        help_text="The type of user account: Player or Research."
    )

    objects = TicTacToeUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'account_type']

    def __str__(self):
        """
        Returns the string representation of the user, which is the username.
        """
        return self.username