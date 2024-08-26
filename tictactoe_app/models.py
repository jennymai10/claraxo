from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class TicTacToeUserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, account_type=None):
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
    ACCOUNT_TYPE_CHOICES = (
        (1, 'Player'),
        (2, 'Research'),
    )

    username = models.CharField(
        max_length=15,
        validators=[MinLengthValidator(7)],
        unique=True
    )
    password = models.CharField(max_length=35)
    email = models.EmailField(validators=[EmailValidator()])
    account_type = models.IntegerField(choices=ACCOUNT_TYPE_CHOICES)

    objects = TicTacToeUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'account_type']

    def __str__(self):
        return self.username
