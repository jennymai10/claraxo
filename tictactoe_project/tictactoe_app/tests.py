from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from .models import TicTacToeUser

class UserRegistrationTests(TestCase):
    """
    Test case for user registration functionality in the TicTacToe application.
    
    This class contains tests to validate that:
    - A user can successfully submit a valid registration form.
    - The user receives an email with a verification code.
    - User data is correctly saved in the database after registration.
    """

    def setUp(self):
        """
        Set up the test client and relevant URLs for registration, email verification, login, and users.

        The test client simulates HTTP requests to the Django application, and the reverse function
        retrieves the URLs for the respective views by name.
        """
        self.client = Client()  # Simulates a browser
        self.register_url = reverse('register_user')  # URL for registration view
        self.verify_email_url = reverse('verify_email')  # URL for email verification view
        self.login_url = reverse('login_user')  # URL for login view
        self.users_url = reverse('get_users')  # URL for the users view

    def test_registration_form_valid_submission(self):
        """
        Test the registration flow with valid form data.

        This test ensures that when valid form data is submitted:
        - The user is created successfully.
        - The user is inactive (as the email needs to be verified).
        - A verification code is generated and sent via email.
        - The server responds with a redirect (status code 302) after successful submission.
        """
        # Simulate a POST request with valid form data for registration
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'password': 'securepassword123',  # Must match the app's password rules
            'email': 'test@example.com',
            'account_type': 1,  # Assuming 1 = Player
            'profile_name': 'Test User',
            'age': 25,
            'api_key': 'sampleapikey123'
        })
        # Check if the response status code is 302 (redirect after successful form submission)
        self.assertEqual(response.status_code, 302)
        
        # Check if the user was created in the database
        user = TicTacToeUser.objects.get(username='testuser')
        # Verify that the user is inactive, as they must verify their email first
        self.assertFalse(user.is_active)
        # Check that a verification code was generated for the user
        self.assertIsNotNone(user.verification_code)

        # Check if an email was sent (Django stores sent emails in a test outbox)
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the email body contains the correct verification code
        self.assertIn(str(user.verification_code), mail.outbox[0].body)
