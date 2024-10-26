from django.test import TestCase
from django.contrib.auth import authenticate
import uuid, random
from django.contrib.auth.tokens import default_token_generator
from tictactoe_app.forms import UserRegistrationForm
from tictactoe_app.models.user_model import TicTacToeUser
from datetime import datetime, timedelta, timezone

class TicTacToeUserModelTests(TestCase):

    def setUp(self):
        # Set up a sample user for testing
        self.user = TicTacToeUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123",
            age=25,
            account_type=1,
            profile_name="Tester"
        )
        self.user.is_active = True  # Mark user as active to allow login
        self.user.save()

    def test_create_user_with_valid_data(self):
        """
        Test that a user can be created with valid data.
        """
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("TestPassword123"))
        self.assertEqual(self.user.age, 25)
        self.assertEqual(self.user.account_type, 1)
        self.assertTrue(self.user.is_active)

    def test_create_user_with_api_key(self):
        """
        Test that a user is created with a unique API key.
        """
        self.assertIsNotNone(self.user.api_key_secret_id)
        self.assertIsInstance(self.user.api_key_secret_id, uuid.UUID)

    def test_user_login_with_valid_credentials(self):
        """
        Test that a user can log in with valid credentials.
        """
        # Authenticate the user with valid credentials
        user = authenticate(username="testuser", password="TestPassword123")
        
        # Assert that authentication was successful
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    def test_user_login_with_invalid_credentials(self):
        """
        Test that login fails with incorrect credentials.
        """
        # Attempt to authenticate with an incorrect password
        user = authenticate(username="testuser", password="WrongPassword123")
        
        # Assert that authentication fails
        self.assertIsNone(user)

class EmailVerificationTests(TestCase):
    def setUp(self):
        self.user = TicTacToeUser.objects.create_user(
            username="verifuser",
            email="verifyuser@example.com",
            password="TestPassword123",
            age=25,
            account_type=1,
            profile_name="Verifier"
        )
        self.user.verification_code = random.randint(100000, 999999)
        self.user.is_active = False
        self.user.save()

    def test_successful_email_verification(self):
        """
        Test that email verification succeeds with a correct code.
        """
        correct_code = self.user.verification_code
        # Simulate verification process
        if correct_code == self.user.verification_code:
            self.user.is_active = True
            self.user.verification_code = None  # Clear code after successful verification
            self.user.save()
        
        # Check that the user is now active
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.verification_code)

    def test_incorrect_email_verification_code(self):
        """
        Test that email verification fails with an incorrect code.
        """
        incorrect_code = 123456  # Use a code that doesn't match
        # Simulate verification failure
        if incorrect_code != self.user.verification_code:
            self.user.is_active = False
            self.user.save()

        # Ensure the user remains inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(self.user.verification_code)

class UserRegistrationFormTests(TestCase):

    def test_registration_with_valid_data(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePassword123',
            'password2': 'SecurePassword123',
            'age': 18,
            'profile_name': 'New User',
            'account_type': 1,
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_with_invalid_age(self):
        form_data = {
            'username': 'younguser',
            'email': 'younguser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123',
            'age': 10,  # Age below the valid limit
            'profile_name': 'Young User',
            'account_type': 1,
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)

class APIKeyManagementTests(TestCase):

    def setUp(self):
        self.user = TicTacToeUser.objects.create_user(
            username="apikeyuser",
            email="apikeyuser@example.com",
            password="TestPassword123",
            age=30,
            account_type=1,
            profile_name="API Tester"
        )
        self.user.api_key_secret_id = uuid.uuid4()
        self.user.api_key_expiry_date = datetime.now(timezone.utc) + timedelta(days=90)
        self.user.save()

    def test_api_key_creation_on_user_creation(self):
        self.assertIsNotNone(self.user.api_key_secret_id)
        self.assertIsInstance(self.user.api_key_secret_id, uuid.UUID)
        self.assertIsNotNone(self.user.api_key_expiry_date)

    def test_api_key_expiry(self):
        # Manually set the expiry date to the past
        self.user.api_key_expiry_date = datetime.now(timezone.utc) - timedelta(days=1)
        self.user.save()
        
        # Check if the API key is expired
        self.user.refresh_from_db()
        self.assertLess(self.user.api_key_expiry_date, datetime.now(timezone.utc))

    def test_api_key_regeneration(self):
        # Regenerate the API key by assigning a new UUID and extending the expiry
        old_secret_id = self.user.api_key_secret_id
        self.user.api_key_secret_id = uuid.uuid4()
        self.user.api_key_expiry_date = datetime.now(timezone.utc) + timedelta(days=90)
        self.user.save()

        # Ensure the API key has changed
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.api_key_secret_id, old_secret_id)



class PasswordResetTests(TestCase):

    def setUp(self):
        self.user = TicTacToeUser.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="InitialPassword123",
            age=30,
            account_type=1,
            profile_name="Reset User"
        )
        self.user.is_active = True
        self.user.save()

    def test_password_reset_token_generation(self):
        token = default_token_generator.make_token(self.user)
        self.assertTrue(default_token_generator.check_token(self.user, token))

    def test_invalid_password_reset_token(self):
        invalid_token = 'invalid-token'
        self.assertFalse(default_token_generator.check_token(self.user, invalid_token))

    def test_successful_password_reset(self):
        token = default_token_generator.make_token(self.user)
        new_password = 'NewSecurePassword456'

        # Simulate password reset
        self.user.set_password(new_password)
        self.user.save()

        # Authenticate with the new password
        user = authenticate(username="resetuser", password=new_password)
        self.assertIsNotNone(user)